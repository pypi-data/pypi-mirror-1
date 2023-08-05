import os, sys, optparse, difflib
from daversy import providers, state
from daversy import plugins, difflib_ext

class Compare(plugins.Command):

    def __init__(self):
        self.name        = ['compare']
        self.description = 'Perform a comparison between two states'
        self.parser      = optparse.OptionParser(usage='%prog compare SOURCE TARGET [options]')

        self.parser.add_option('-f', dest='filter',
                               help='selectively load the states using given FILTER')
        self.parser.add_option('-t', dest='tags', metavar='TAG1,TAG2', default='all',
                               help='include selected (default: "all") tags from the filter spec')
        self.parser.add_option('-e', dest='encoding', default='utf-8',
                               help='assume the database uses given ENCODING')
        self.parser.add_option('--html', dest='html', default=False, action='store_true',
                               help='generate a inline-diff style HTML report')
        self.parser.add_option('--context', dest='lines', default=None, type='int', metavar='NUM',
                               help='number of context lines to include. if not specified, all lines will be included.')
    def execute(self, argv):
        if not argv:
            self.parser.print_help()
            sys.exit(1)

        (options, args) = self.parser.parse_args(argv)

        if not len(args) == 2:
            self.parser.print_help()
            sys.exit(1)

        filters = {}
        if options.filter:
            if not os.path.exists(options.filter):
                self.parser.error('Unable to open the filter specification')
            filters = state.create_filter(options.filter, options.tags)

        source_location, target_location = args
        source = target = None
        for provider in state.PROVIDERS:
            if provider.can_load(source_location):
                source = provider.load(source_location, options.encoding, filters)
            if provider.can_load(target_location):
                target = provider.load(target_location, options.encoding, filters)

        if not source:
            self.parser.error('Unable to load the source state from given location')

        if not target:
            self.parser.error('Unable to load the target state from given location')

        if not source.Provider == target.Provider:
            self.parser.error('The source and target state belong to different databases')

        self.source_version, self.target_version = source.name, target.name
        source.name = target.name = None
        if source == target:
            return

        self.provider = providers.DATABASES[source.Provider]
        self.builders = {}
        self.tags = {}
        for builder in self.provider.SCHEMA_BUILDERS:
            self.builders[builder.DbClass] = builder
            self.tags[builder.DbClass] = builder.XmlTag

        self.diff = []
        self.compute_diff([], source, target)
        if not options.html:
            self.print_simple_diff()
        else:
            self.print_html_diff(source, target, options.lines)


    def compute_diff(self, location, source, target):
        builder = self.builders[source.__class__]

        if source == target:
            return

        if hasattr(source, 'SubElements'):
            for key in source.SubElements.keys():
                src, tgt = source[key], target[key]
                if not src == tgt:
                    src_names = [elem.name for elem in src.values()]
                    tgt_names = [elem.name for elem in tgt.values()]
                    common    = []
                    for elem in src.values():
                        if not elem.name in tgt_names:
                            path = location[:]
                            path.append( (elem, None, elem.name) )
                            self.diff.append( ('D', path) )
                        elif common.count(elem.name) == 0:
                            common.append(elem.name)
                    for elem in tgt.values():
                        if not elem.name in src_names:
                            path = location[:]
                            path.append( (None, elem, elem.name) )
                            self.diff.append( ('A', path) )
                        elif common.count(elem.name) == 0:
                            common.append(elem.name)
                    for name in common:
                        path = location[:]
                        path.append( (src[name], tgt[name], name) )
                        self.compute_diff(path, src[name], tgt[name])

        if hasattr(builder, 'PropertyList'):
            for prop in builder.PropertyList.values():
                if not prop.exclude:
                    if source[prop.name] != target[prop.name]:
                        path = location[:]
                        path.append( (None, None, prop.name) )
                        self.diff.append( ('M', path) )

    def print_simple_diff(self):
        for op, path in self.diff:
            sys.stdout.write('%s' % op)
            for src, target, name in path:
                if src is None and target is None:
                    sys.stdout.write(' @%s' % name)
                else:
                    elem = src or target
                    sys.stdout.write(' %s[%s]' % (self.tags[elem.__class__], name))
            sys.stdout.write('\n')

    def print_html_diff(self, source, target, context):
        get_id = lambda x: 'ref__%s__%s' % (x.__class__.__name__, x.name)
        get_link = lambda type, x: '<li><div class="%s"></div>%s <a href="#%s">%s</a></li>' % \
                                   (type, x.__class__.__name__, get_id(x), x.name)

        seen  = {}
        diffs = []
        headers = []
        for op, path in self.diff:
            src, target, name = path[0]
            if len(path) == 1 and op == 'A':
                table = difflib_ext.make_table(get_id(target), name, [],
                                               self.get_sql(target), context)
                if table:
                    headers.append( get_link('add', target) )
                    diffs.append(table)
            elif len(path) == 1 and op == 'D':
                table = difflib_ext.make_table(get_id(src), name,
                                               self.get_sql(src), [], context)
                if table:
                    headers.append( get_link('rem', src) )
                    diffs.append(table)
            elif not seen.has_key( (src.__class__, name) ):
                table = difflib_ext.make_table(get_id(target), name,
                                               self.get_sql(src), self.get_sql(target),
                                               context)
                seen [ (src.__class__, name) ] = True
                if table:
                    headers.append( get_link('mod', target) )
                    diffs.append(table)


        output = difflib_ext.HTML_HEADER
        output += '<dl id="overview">'
        output += '<dt>Source:</dt><dd><span class="ver">%s</span></dd></dt>' % self.source_version
        output += '<dt>Target:</dt><dd><span class="ver">%s</span></dd></dt>' % self.target_version
        output += '<dt class="files">Changes:</dt><dd class="files"><ul>' + ''.join(headers) + '</ul></dd>'
        output += '</dl><div class="diff"><ul class="entries">' + ''.join(diffs) + '</ul></div>'
        output += difflib_ext.HTML_FOOTER
        print output

    def get_sql(self, elem):
        builder = self.builders[elem.__class__]
        sql = builder.createSQL(elem).splitlines()
        if hasattr(builder, 'commentSQL'):
            sql.extend( builder.commentSQL(elem) )
        return sql
