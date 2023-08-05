import os, sys
from optparse import OptionParser
from daversy import plugins, state

class Generate(plugins.Command):

    def __init__(self):
        self.name        = ['generate']
        self.description = 'Generate a creation SQL from an existing state'
        self.parser      = OptionParser(usage='%prog generate INPUT OUTPUT [options]')

        self.parser.add_option('-e', '--encoding', dest='encoding',
                               help='use the given ENCODING')
        self.parser.add_option('-f', dest='filter',
                               help='selectively copy the state using the given FILTER specification')
        self.parser.add_option('-t', dest='tags', metavar='TAG1,TAG2', default='all',
                               help='include selected (default: "all") tags from the filter spec')
        self.parser.add_option('-s', dest='sql_type', metavar='TYPE', default='all',
                               help='generate create, comment or all SQL')
        self.parser.add_option('-i', dest='info', default='** dvs **',
                               help='provider specific information used by the target')

    def execute(self, argv):
        (options, args) = self.parser.parse_args(argv)

        if not len(args) == 2:
            self.parser.print_help()
            sys.exit(1)

        filters = {}
        if options.filter:
            if not os.path.exists(options.filter):
                self.parser.error('Unable to open the filter specification')
            filters = state.create_filter(options.filter, options.tags)

        if not options.sql_type in ['all','create','comment']:
            self.parser.error('Invalid SQL generation type specified')

        input, output = args
        saved_state = None
        for provider in state.PROVIDERS:
            if provider.can_load(input):
                saved_state = provider.load(input, options.encoding, filters)

        saved = False
        for provider in state.PROVIDERS:
            if provider.can_save(output) and hasattr(provider, 'save_sql'):
                saved = True
                provider.save_sql(saved_state, output, options.info, options.sql_type)

        if not saved:
            self.parser.error('Unable to generate the SQL to given location')
