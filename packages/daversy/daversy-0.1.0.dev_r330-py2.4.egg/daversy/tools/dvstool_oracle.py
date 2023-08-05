#!/usr/bin/env python
import os, sys, re, datetime, ConfigParser, time
import subprocess, glob, optparse, cStringIO, tempfile

from daversy.utils import get_uuid4

CMDLINE = 100
TOOLERR = 101
CMDERR  = 102
SQLERR  = 103
MIGERR  = 104

class DvsOracleTool(object):
    def execute(self, cmd):
        try:
            command = subprocess.Popen(cmd, stderr=subprocess.STDOUT,
                                            stdout=subprocess.PIPE)
            self.output = ''
            while 1:
                temp = command.stdout.read()
                if not temp:
                    break
                self.output += temp
            result = command.wait()
            self.output = self.output.strip()
            return result
        except KeyboardInterrupt, SystemExit:
            raise
        except:
            pass
        return None

    def tempfile(self, data='', ext='.sql'):
        if not hasattr(self, 'files'):
            self.files = []
        handle, location = tempfile.mkstemp(ext)
        os.write(handle, data)
        os.close(handle)
        location = location.replace('\\','/')
        self.files.append(location)
        return location

    def sqlplus(self, code):
        result = False
        location = self.tempfile(code)
        try:
            status = self.execute(['sqlplus', '-S', '-L', self.connectString,
                                   '@' + location])
            result = (status == 0)
        except KeyboardInterrupt, SystemExit:
            raise
        except:
            pass
        return result

    def check_commands(self):
        if self.execute(['sqlplus', '/?']) != 0:
            self.message('Unable to execute SQL*Plus, please check that Oracle is in the PATH.')
            self.quit(TOOLERR)

        if self.execute(['dvs']) != 0:
            self.message('Unable to execute Daversy, please ensure that it is in the PATH.')
            self.quit(TOOLERR)

        if hasattr(self, 'connectString') and not self.sqlplus(SQLPLUS_EXEC % ''):
            self.message('Unable to connect to Oracle, please the connection string.')
            self.quit(TOOLERR)

    def message(self, msg, prefix='**'):
        if prefix:
            print prefix, msg
        else:
            print msg
        sys.stdout.flush()

    def execute_cmd(self, msg, cmd):
        self.message(msg)
        status = self.execute(cmd)
        if not status == 0:
            self.message('FAILED')
            self.quit(CMDERR)

    def execute_ddl(self, msg, *list):
        self.message(msg)
        for ddl in list:
            if not self.sqlplus(SQLPLUS_EXEC_DDL % ddl):
                self.message('FAILED')
                self.quit(SQLERR)

    def execute_sql(self, msg, *list):
        self.message(msg)
        sys.stdout.flush()
        for ddl in list:
            if not self.sqlplus(SQLPLUS_EXEC % ddl):
                self.message('FAILED')
                self.quit(SQLERR)

    def read_file(self, name):
        file = open(name, 'r')
        data = file.read()
        file.close()
        return data

    def write_file(self, name, data):
        file = open(name, 'w')
        file.write(data)
        file.close()

    def cleanup(self, code=0):
        if hasattr(self, 'files'):
            while len(self.files):
                try:
                    os.remove(self.files.pop())
                except OSError:
                    pass

    def quit(self, code=0):
        self.cleanup()
        sys.exit(code)

class CleanDb(DvsOracleTool):
    def __main__(self):
        parser = optparse.OptionParser(usage='%prog clean CONNECT-STRING')
        (options, args) = parser.parse_args(sys.argv[2:])

        if not len(args) == 1:
            parser.print_help()
            self.quit(CMDLINE)

        self.connectString, = args

        self.check_commands()
        self.run()

    def run(self):
        self.execute_ddl('dropping all schema objects', DROPCODE_SQL, DROPTABLE_SQL)

class CreateDb(DvsOracleTool):
    def __main__(self):
        parser = optparse.OptionParser(usage='%prog create [options] CONNECT-STRING STATE')
        parser.add_option('--wrap', action='store_true', default=False, dest='wrap',
                          help='run the Oracle wrap utility on generated SQL')
        parser.add_option('--sql-type', dest='sql_type', metavar='TYPE', default='all',
                          help='generated the specified SQL type (default: "all")')
        (options, args) = parser.parse_args(sys.argv[2:])

        if not len(args) == 2:
            parser.print_help()
            self.quit(CMDLINE)

        self.connectString, state = args

        self.check_commands()
        self.run(options, state)

    def run(self, options, state):
        self.execute_cmd('getting state version', ['dvs', 'name', state])
        version = self.output

        ddl = self.tempfile()

        self.execute_cmd('generating schema DDL',
                         ['dvs', 'generate', '-s', options.sql_type, state, ddl])

        if options.wrap:
            self.execute_cmd('encoding schema DDL',
                             ['wrap', 'iname='+ddl, 'oname=' + ddl+'.enc'])
            os.remove(ddl)
            os.rename(ddl+'.enc', ddl)

        self.execute_ddl('dropping existing schema', DROPCODE_SQL, DROPTABLE_SQL)

        self.execute_ddl('creating new schema', SCHEMALOG_SQL % version,
                                                EXECSCRIPT_SQL % ddl)
        self.execute_ddl('recompiling schema', RECOMPILE_SQL)

        self.cleanup()

class DiffDb(DvsOracleTool):
    def __main__(self):
        parser = optparse.OptionParser(usage='%prog [options] SOURCE TARGET')
        (options, args) = parser.parse_args(sys.argv[2:])

        if not len(args) == 2:
            parser.print_help()
            self.quit(CMDLINE)

        self.check_commands()
        input, output = args
        self.quit( self.run(input, output) )

    def run(self, input, output):
        self.execute_cmd('comparing states', ['dvs', 'compare', input, output])

        if not self.output:
            return 0

        log = cStringIO.StringIO( self.output )
        for line in log:
            for elem in MIGRATION_NEEDED:
                if elem in line and not ('@comment' in line and line.startswith('M')):
                    return 2
        return 1

class MigrateDb(DvsOracleTool):
    def __main__(self):
        parser = optparse.OptionParser(usage='%prog migrate [options] CONNECT-STRING STATE FILTER MIGRATION-DIR')
        parser.add_option('--wrap', action='store_true', default=False, dest='wrap',
                          help='run the Oracle wrap utility on generated SQL')
        parser.add_option('--no-comment', action='store_true', default=False, dest='no_comment',
                          help='do not update the comments in the target schema')
        parser.add_option('-t', dest='tags', default='all',
                          help='use the given tags')
        (options, args) = parser.parse_args(sys.argv[2:])

        if not len(args) == 4:
            parser.print_help()
            self.quit(CMDLINE)

        self.connectString, state, filter, migration_dir = args
        self.check_commands()
        if not os.path.isdir(migration_dir):
            parser.error('The migrations directory does not exist')

        self.quit( self.run(options, state, filter, migration_dir) )

    def run(self, options, state, filter, migration_dir):

        #### determine current and target versions

        self.execute_cmd('getting target state version', ['dvs', 'name', state])
        self.target_version = self.output

        self.execute_ddl('getting source state version', GETVERSION_SQL)
        match = re.match(r'SCHEMA_VERSION\s+\-+\s+([\w\-]+)\s*', self.output)
        if not match:
            self.message('FAILED')
            self.quit(SQLERR)
        self.source_version = match.group(1)

        if self.source_version == self.target_version:
            self.message('no migration needed')
            return 0

        self.message('%s => %s' % (self.source_version, self.target_version))

        #### replace existing schema objects which don't need migration

        code_config = self.tempfile(CODEFILTER_INI, '.ini')
        ddl = self.tempfile()

        self.execute_cmd('generating updated objects',
                         ['dvs', 'generate', '-f', code_config,
                          '-s', 'create', state, ddl])

        if options.wrap:
            self.execute_cmd('encoding schema objects',
                             ['wrap', 'iname='+ddl, 'oname=_'+ddl])
            os.remove(ddl)
            os.rename('_'+ddl, ddl)

        self.execute_ddl('dropping existing objects', DROPCODE_SQL)
        self.execute_ddl('creating updated objects', EXECSCRIPT_SQL % ddl)
        self.execute_ddl('recompiling schema', RECOMPILE_SQL)

        #### determine and perform migrations

        self.do_migrations(migration_dir)

        self.execute_ddl('recompiling schema', RECOMPILE_SQL)

        #### replace existing comments

        if not options.no_comment:
            self.execute_cmd('generating updated comments',
                             ['dvs', 'generate', '-s', 'comment', state, ddl])

            self.execute_ddl('applying updated comments', EXECSCRIPT_SQL % ddl)

        #### check for successful migration
        migrated = self.tempfile(ext='.state')
        self.execute_cmd('extracting migrated state',
                         ['dvs', 'copy', '-f', filter, '-t', options.tags,
                          'oracle:' + self.connectString, migrated])

        return_val = DiffDb().run(state, migrated)

        if return_val == 2:
            self.message('migration was not successful: migrated and target schemas differ.')
            return return_val
        elif return_val == 1:
            self.message('warning: there were some code/comment changes!!')

        if self.migration_path:
            for new_version, description, data in self.migration_path:
                if data:
                    self.execute_sql('marking successful: [%s]' % description,
                                     UPDATESCHEMA_SQL % (new_version, description))
                    time.sleep(2)
        else:
                self.execute_sql('migrated successfully to [%s]' % self.target_version,
                                 UPDATESCHEMA_SQL % (self.target_version, '** simple migration **'))

        self.cleanup()
        return return_val


    def do_migrations(self, dir):

        self.migrations = {}

        ### get available migrations
        file_list = glob.glob(dir + '/*.sql')

        for file in file_list:
            data = self.read_file(file)
            match = MIGRATION_REGEX.match(data)
            if not match:
                self.message('[%s] is not a valid migration.' % os.path.basename(file))
                continue
            source, target, description = match.groups()

            entry = self.migrations.setdefault(target, [])
            entry.append( (source, description, data) )

        ### get the list of direct migrations
        no_migrations = ConfigParser.ConfigParser()
        no_migrations.read( os.path.join(dir, 'migration.ini') )

        for source in no_migrations.options('migrations'):
            target = no_migrations.get('migrations', source)
            entry = self.migrations.setdefault(target, [])
            entry.append( (source, '** no migration needed **', None) )

        ### find the migration path

        self.migration_path = self.find_path(self.target_version)
        if not self.migration_path:
            self.message('unable to find a migration path (assuming none needed)')
            return

        ### run the migrations

        for new_version, description, data in self.migration_path:
            if data:
                self.execute_sql('running migration: [%s]' % description, data)

    def find_path(self, node):
        targets = self.migrations.get(node)
        if not targets:
            return None

        path = None
        for version, description, data in targets:
            if version == self.source_version:
                return [ (node, description, data) ]
            path = self.find_path(version)
            if path:
                path.append( (node, description, data) )
                break

        return path

class SyncDb(DvsOracleTool):
    def __main__(self):
        parser = optparse.OptionParser(usage='%prog sync [options] CONNECT-STRING TEMP-CONNECT-STRING BASE-DIR')
        parser.add_option('-t', dest='tags', default='all',
                          help='use the given tags')
        (options, args) = parser.parse_args(sys.argv[2:])

        if not len(args) == 3:
            parser.print_help()
            self.quit(CMDLINE)

        self.connectString, self.tempConnectString, self.base_dir = args

        self.check_commands()
        if not os.path.isdir(self.base_dir):
            parser.error('The base directory does not exist')

        self.quit( self.run(options, self.base_dir) )

    def run(self, options, base_dir):
        # setup directory configuration

        self.config_dir     = os.path.join(base_dir, 'config')
        self.migration_dir  = os.path.join(base_dir, 'migration')
        self.filter_config  = os.path.join(self.config_dir, 'schema.ini')
        self.version_config = os.path.join(self.config_dir, 'version.ini')
        self.migration_conf = os.path.join(self.migration_dir, 'migration.ini')

        self.changelog      = os.path.join(base_dir, 'changes.txt')
        self.change_report  = os.path.join(base_dir, 'change_report.html')
        self.current_state  = os.path.join(base_dir, 'current.state')
        self.latest_state   = self.tempfile(ext='.state')

        # check for changes
        versions = ConfigParser.ConfigParser()
        versions.read(self.version_config)

        if not versions.has_option('version', 'current'):
            self.message('Version configuration file is missing or invalid, aborting.')
            self.quit(CMDLINE)

        self.current_version = versions.get('version', 'current')
        self.next_version    = versions.get('version', 'next')

        self.execute_cmd('extracting latest database state',
                         ['dvs', 'copy', '-f', self.filter_config,
                          '-n', self.next_version, '-t', options.tags,
                          'oracle:'+self.connectString, self.latest_state])

        differ = DiffDb()
        status = differ.run(self.current_state, self.latest_state)
        if status == 0:
            self.message('no changes detected')
            return 0
        elif status == 1:
            self.message('changes detected, skipping migration check')
            self.generate_diff()

            # mark that this requires no migration
            skip_migrations = ConfigParser.ConfigParser()
            skip_migrations.read(self.migration_conf)
            skip_migrations.set('migrations', self.current_version, self.next_version)
            migration_file = file(self.migration_conf, 'w')
            skip_migrations.write(migration_file)
            migration_file.close()
        elif status == 2:
            self.message('changes detected, performing migration check')
            self.generate_diff()
            if not self.check_migration(options):
                self.message('', None)
                self.message('migration check failed, migrations may be incomplete or invalid.')
                return 1
            self.message('', None)
            self.message('migration check succeeded')

        self.message('generating new version numbers')
        new_version = get_uuid4()
        versions.set('version', 'current', self.next_version)
        versions.set('version', 'next',    new_version)

        version_file = file(self.version_config, 'w')
        versions.write(version_file)
        version_file.close()

        self.execute_sql('synchronizing version numbers',
                         UPDATESCHEMA_SQL % (self.next_version, '** migrations tested **'))

        self.message('updating the change log')
        migration_changes = []
        if hasattr(self, 'migrate'):
            for version, description, data in self.migrate.migration_path:
                migration_changes.append('- ' + description)

        current_date = datetime.date.today().strftime('[%Y-%m-%d] ')

        text = current_date + self.next_version + '\n%s\n\n' % ('=' * 49)
        if migration_changes:
            text += 'Migrations:\n\n' + '\n'.join(migration_changes) + '\n\n'

        text += 'Schema Changes:\n\n' + differ.output + '\n\n\n\n'

        previous_changelog = self.read_file(self.changelog)
        self.write_file(self.changelog, text + previous_changelog)

        self.message('updating the current state with latest version')
        os.remove(self.current_state)
        os.rename(self.latest_state, self.current_state)

        return 0

    def check_migration(self, orig_options):
        options = optparse.Values()
        options.sql_type = 'all'
        options.no_comment = False
        options.wrap = False
        options.tags = orig_options.tags

        self.message('', None)
        self.message('creating existing state on a temporary database instance')
        self.message('', None)

        self.create = CreateDb()
        self.create.connectString = self.tempConnectString
        self.create.run(options, self.current_state)

        self.message('', None)
        self.message('running migrations on the temporary database instance')
        self.message('', None)
        self.migrate = MigrateDb()
        self.migrate.connectString = self.tempConnectString
        result = self.migrate.run(options, self.latest_state,
                                  self.filter_config, self.migration_dir)

        return result == 0

    def generate_diff(self):
        self.execute_cmd('generating schema difference report',
                         ['dvs', 'compare', '--html', '--context', '10',
                          self.current_state, self.latest_state])
        self.write_file(self.change_report, self.output)



MIGRATION_NEEDED = ['foreign-key', 'table', 'index', 'sequence']

SQLPLUS_EXEC = """
WHENEVER SQLERROR EXIT FAILURE ROLLBACK;
SET DEFINE off;
SET SQLBLANKLINES ON;
%s
exit
/
"""

SQLPLUS_EXEC_DDL = """
WHENEVER SQLERROR CONTINUE;
SET DEFINE off;
SET SQLBLANKLINES ON;
%s
exit
/
"""

DROPCODE_SQL = """
DECLARE CURSOR object_list IS
      SELECT   object_name, object_type
      FROM     user_objects
      WHERE    object_type IN ('PACKAGE', 'FUNCTION', 'PROCEDURE', 'TRIGGER', 'VIEW');
BEGIN
   FOR rec IN object_list LOOP
      EXECUTE IMMEDIATE ' DROP ' || rec.object_type || ' ' || rec.object_name;
   END LOOP;
END;
/
"""

DROPTABLE_SQL = """
DECLARE CURSOR object_list IS
      SELECT object_name FROM user_objects WHERE object_type = 'TABLE';
BEGIN
   FOR rec IN object_list LOOP
      EXECUTE IMMEDIATE ' DROP TABLE ' || rec.object_name || ' CASCADE CONSTRAINTS PURGE';
   END LOOP;
END;
/
DECLARE CURSOR object_list IS
      SELECT object_name FROM user_objects WHERE object_type = 'SEQUENCE';
BEGIN
   FOR rec IN object_list LOOP
      EXECUTE IMMEDIATE ' DROP SEQUENCE ' || rec.object_name;
   END LOOP;
END;
/
"""

RECOMPILE_SQL = """
BEGIN
    dbms_utility.compile_schema(USER);
END;
/
"""

SCHEMALOG_SQL = """
CREATE TABLE schema_log (
    schema_version     CHAR(36),
    schema_timestamp   TIMESTAMP DEFAULT sysdate,
    schema_description VARCHAR2(255),
    CONSTRAINT schema_log_req CHECK (schema_version IS NOT NULL)
)
/
INSERT INTO schema_log(schema_version, schema_description) VALUES ('%s', '*** fresh creation ***')
/
"""

UPDATESCHEMA_SQL = """
INSERT INTO schema_log(schema_version, schema_description) VALUES ('%s', '%s')
/
"""

EXECSCRIPT_SQL = """
@"%s"
/
"""

GETVERSION_SQL = """
SELECT schema_version
FROM   schema_log
WHERE  schema_timestamp = ( SELECT MAX(schema_timestamp) FROM schema_log );
"""

CODEFILTER_INI = """
[table]
[sequence]
[index]
[foreign-key]
[view]
.*=all
[stored-procedure]
.*=all
[function]
.*=all
[package]
.*=all
[trigger]
.*=all
"""



MIGRATION_REGEX = re.compile(r'/\*\*\*\s+Source-Version:\s+([\w\-]+)\s+Target-Version:\s+([\w\-]+)\s+Description:\s+(.+?)\s+\*\*\*\/')

TOOLS = { 'sync' : SyncDb, 'clean' : CleanDb, 'create' : CreateDb, 'diff' : DiffDb, 'migrate' : MigrateDb }

def main():
    if len(sys.argv) == 1 or sys.argv[1] not in TOOLS.keys():
        print 'Please specify a valid command (one of: %s)' % (', '.join(TOOLS.keys()))
        sys.exit(0)

    tool = TOOLS[ sys.argv[1] ]()
    try:
        tool.__main__()
    except:
        tool.cleanup()
        raise

if __name__ == '__main__':
    main()
