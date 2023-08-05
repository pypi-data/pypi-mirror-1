#!/usr/bin/env python

import sys
from daversy import plugins

def main():
    if len(sys.argv) > 1:
        commands = []
        for cmd in plugins.Command.all().values():
            commands.append(','.join(cmd.name))
            if sys.argv[1] in cmd.name:
                cmd.execute(sys.argv[2:])
                sys.exit(0)
        # print usage
        print "usage: dvs COMMAND [options] [args]\nDaversy command-line client, version 0.1\n\n" \
        "Available subcommands:\n\n  " + '\n  '.join(commands) + '\n\nDaversy is a source control tool for relational databases.\n' \
        'For additional information, see http://www.svn-hosting.com/trac/Daversy'
    else:
        print "Type 'dvs help' for usage."

if __name__ == '__main__':
    sys.exit(main())