import os, sys

DEFAULT_CONFIG_PATH = os.path.join("%s" % os.path.dirname(__file__), '..%sconf' % os.sep)

class ConfigError(Exception):
    """default configuration error"""
    

class CfgBase(object):
    """simply a dotted notation way of accessing dicts"""
    pass


def build_config(config_dict):
    """build a chain of dotted notation objs"""
    this_obj = CfgBase()
    for k, v in config_dict.items():
        if isinstance(v, dict):
            setattr(this_obj, k, build_config(v))
        elif isinstance(v, (list, tuple)):
            new_value = []
            for v_elem in v:
                if isinstance(v_elem, dict):
                    new_value.append(build_config(v_elem))
                    continue
                new_value.append(v_elem)
            setattr(this_obj, k, new_value)
        else:
            setattr(this_obj, k, v)
    return this_obj


class LoadBehavior(object):
    def __init__(self, configdir):
        self.configdir = configdir

    def load(self, name):
        raise NotImplementedError("Abstract, implement in sublcass")
    
    def __call__(self, name):
        return self.load(name)
    


class PyConfigLoader(LoadBehavior):
    def load(self, name):
        name = name.strip()
        # try filepath at the configDir we're handed.
        # if it's not there, try the default.
        # if default is not there, raise
        filepath = os.path.join(self.configdir, "%s.py" % name)
        if not os.path.isfile(filepath.strip()):
            filepath = os.path.join(DEFAULT_CONFIG_PATH, "%s.py" % name)
            if not os.path.isfile(filepath.strip()):
                raise ConfigError("filename %s in configdir %s is not valid!" % (name, self.configdir))
        # this whole "get a name from locals" rather than use the name explicitly thing
        # is because _config_ seems unpredictable in how it gets loaded 
        # into the namespace from execfile
        execfile(filepath)
        if not locals().get('_config_'):
            raise ConfigError("Unable to find a _config_ setup for file %s" % filepath)
        return build_config(locals().get('_config_'))
    

class XmlConfigLoader(LoadBehavior):
    """to use the old-style xml configs, amara is required.
       because some systems either cannot or will not support the full
       4Suite-XML package, both pyconfigs and xmlconfigs are allowed"""
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
        # putting this here for now to support the old style configs if necessary
        from amara import binderytools
        configDoc = binderytools.bind_file(filepath)
        # we don't need to index the config like
        # classinstance.config.classname.attrs.attribute
        # instead
        # classinstance.config.attrs.attribute
        return configDoc.childNodes[0]


class ConfigLoader(object):
    """the idea is to be able to instantiate this against a directory
       and then call cl.load(config)
       >>> cl = ConfigLoader('../definitions/')
       >>> cl.load("watch_template")
    """
    def __init__(self, configdir=None, configStyle='py'):
        self.configdir = configdir.strip()
        if self.configdir is None:
            self.configdir = DEFAULT_CONFIG_PATH 
        if not os.path.isdir(self.configdir):
            raise ConfigError("directory |%s| is not valid!" % self.configdir)    
        conf_styles = {
            'py' : PyConfigLoader,
            'xml' : XmlConfigLoader,
        }
        if not configStyle in conf_styles:
            raise ConfigError("Cannot find %s config style loader!" % configStyle)
        self.loadBehavior = conf_styles[configStyle](self.configdir)
    
    def load(self, name):
        return self.loadBehavior(name)



class KlassBuilder(object):
    def __init__(self, configName, configPath=None, configStyle='py'):
        """takes a name, and a configpath, of the form:
           my_config_file_name, configPath=/some/config/path
           should read the config in using ConfigLoader.

           all configs are now required to have the following:
           package="dotted.package.name"
           class="MyNewClass"
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
            config = ConfigLoader(configPath, configStyle).load(configName)
        except ConfigError:
            config = ConfigLoader(DEFAULT_CONFIG_PATH, configStyle).load(configName)
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
