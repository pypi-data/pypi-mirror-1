import os, sys

DEFAULT_CONFIG_PATH = os.path.join("%s" % os.path.dirname(__file__), '..%sconf' % os.sep)

from amara import binderytools

class ConfigError(Exception):
    """default configuration error"""

class ConfigLoader(object):
    """the idea is to be able to instantiate this against a directory
       and then call cl.load(config)
       >>> cl = ConfigLoader('../definitions/')
       >>> cl.load("watch_template")
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


class KlassBuilder(object):
    def __init__(self, configName, configPath=None):
        """takes a name, and a configpath, of the form:
           my_config_file_name, configPath=/some/config/path
           should read the config in using ConfigLoader.

           all configs are now required to have the following:
           package="dotted.package.name"
           class="MyNewWatcherClass"
           name="new_name"
           instead of the simple name="some_name" that they
           began with.
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
        self.obj_config = config

    def __call__(self, instantiate=False):
        try:
           p = __import__(self.package, {}, {}, (self.loadklass,))
           klass = getattr(p, self.loadklass)
        except ImportError, e:
           raise ConfigError("No package for config.  Error: %s" % e)
        if instantiate:
            k = klass(self.obj_config)
            return k
        return klass

        
