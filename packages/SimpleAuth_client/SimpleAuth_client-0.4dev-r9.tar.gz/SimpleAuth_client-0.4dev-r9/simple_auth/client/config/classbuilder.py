import os,sys

from simple_auth.client.config import ConfigLoader, DEFAULT_CONFIG_PATH, ConfigError

class KlassBuilder(object):
    def __init__(self, configName, configPath=None):
        """takes a name, and a configpath, of the form:
           my_config_file_name, configPath=/some/config/path
           should read the config in using ConfigLoader.

           all configs are required to have the following:
           package="dotted.package.name"
           klass="MyNewWatcherClass"
           name="new_name"
        """
        if configPath is None:
            configPath = DEFAULT_CONFIG_PATH
        
        # if we're given a config path that fails to load
        # the config correctly, try from the default location
        # if they both fall through, we'll raise anyway
        try:
            config = ConfigLoader(configPath).load(configName)
        except ConfigError:
            config = ConfigLoader(DEFAULT_CONFIG_PATH).load(configName)
        self.package = str(config.package)
        self.loadklass = str(config.klass)
        self.name = str(config.name)

    def __call__(self):
        try:
           p = __import__(self.package, {}, {}, (self.loadklass,))
           klass = getattr(p, self.loadklass)
        except ImportError, e:
           raise ConfigError("No package for config.  Error: %s" % e)
        return klass

        
