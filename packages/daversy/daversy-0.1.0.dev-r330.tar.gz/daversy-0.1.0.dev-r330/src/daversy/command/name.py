import os, sys
from optparse     import OptionParser
from ConfigParser import ConfigParser
from daversy import plugins, state, utils

class Name(plugins.Command):

    def __init__(self):
        self.name        = ['name']
        self.description = 'Display the name for a given state'
        self.parser      = OptionParser(usage='%prog name INPUT')

    def execute(self, argv):
        if not argv:
            self.parser.print_help()
            sys.exit(1)

        (options, args) = self.parser.parse_args(argv)

        if not len(args) == 1:
            self.parser.print_help()
            sys.exit(1)

        input, = args
        saved_state = None
        for provider in state.PROVIDERS:
            if provider.can_load(input):
                saved_state = provider.load(input, None)

        if not saved_state:
            self.parser.error('Unable to load the state from given location')

        print saved_state.name
