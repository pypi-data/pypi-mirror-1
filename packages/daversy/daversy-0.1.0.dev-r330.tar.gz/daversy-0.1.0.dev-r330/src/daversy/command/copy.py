import os, sys
from optparse     import OptionParser
from ConfigParser import ConfigParser
from daversy import plugins, state, utils

class Copy(plugins.Command):

    def __init__(self):
        self.name        = ['copy']
        self.description = 'Copy the state from source to destination'
        self.parser      = OptionParser(usage='%prog copy INPUT OUTPUT [options]')

        self.parser.add_option('-f', dest='filter',
                               help='selectively copy the state using the given FILTER specification')
        self.parser.add_option('-t', dest='tags', metavar='TAG1,TAG2', default='all',
                               help='include selected (default: "all") tags from the filter spec')
        self.parser.add_option('-e', dest='encoding',
                               help='assume the database uses given ENCODING')
        self.parser.add_option('-i', dest='info', default='** dvs **',
                               help='provider specific information used by the target')
        self.parser.add_option('-n', dest='name',
                               help='use the given name for the state')

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

        input, output = args
        saved_state = None
        for provider in state.PROVIDERS:
            if provider.can_load(input):
                saved_state = provider.load(input, options.encoding, filters)

        if not saved_state:
            self.parser.error('Unable to load the state from given location')

        if options.name:
            saved_state.name = options.name
        elif saved_state.setdefault('name') is None:
            saved_state.name = utils.get_uuid4()

        saved = False
        for provider in state.PROVIDERS:
            if provider.can_save(output):
                saved = True
                provider.save(saved_state, output, options.info)

        if not saved:
            self.parser.error('Unable to save the state to given location')
