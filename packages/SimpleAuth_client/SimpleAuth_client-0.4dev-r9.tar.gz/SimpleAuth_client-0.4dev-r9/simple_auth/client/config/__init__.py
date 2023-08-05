import os, sys

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../conf")

from amara import binderytools

class ConfigError(Exception):
    """default configuration error"""

class ConfigLoader(object):
    """the idea is to be able to instantiate this against a directory
       and then call cl.load(config)
    """
    def __init__(self, configdir=None):
        self.configdir = configdir.strip()
        if self.configdir is None:
            self.configdir = DEFAULT_CONFIG_PATH 
        if not os.path.isdir(self.configdir):
            raise ConfigError("directory |%s| is not valid!" % self.configdir)

    def load(self, name):
        name = name.strip()
        # try filepath at the configDir we're handed.
        # if it's not there, try the default.
        # if default is not there, raise
        filepath = os.path.join(self.configdir, "%s.xml" % name)
        if not os.path.isfile(filepath.strip()):
            filepath = os.path.join(DEFAULT_CONFIG_PATH, "%s.xml" % name)
            if not os.path.isfile(filepath.strip()):
                raise ConfigError("filename %s in configdir %s is not valid!" % (name, self.configdir))
        configDoc = binderytools.bind_file(filepath)
        # we don't need to index the config like
        # classinstance.config.classname.attrs.attribute
        # instead
        # classinstance.config.attrs.attribute
        return configDoc.childNodes[0]

