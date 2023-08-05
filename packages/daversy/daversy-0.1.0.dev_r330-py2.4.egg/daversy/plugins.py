
class Plugin(object):
    """A very simple plugin system."""
    @classmethod
    def initialize(cls):
        cls._all = {}
        if not hasattr(cls, 'PluginModule'):
            return
        try:
            __import__(cls.PluginModule, None, None, ['*'])
            for subclass in cls.__subclasses__():
                cls._all[subclass] = subclass()
        except:
            pass

    @classmethod
    def all(cls):
        if not hasattr(cls, '_all'):
            cls.initialize()
        return cls._all

class Command(Plugin):
    PluginModule = 'daversy.command'

class Provider(Plugin):
    PluginModule = 'providers'