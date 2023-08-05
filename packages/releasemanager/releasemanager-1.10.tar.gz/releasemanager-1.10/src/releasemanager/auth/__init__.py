from releasemanager.config import KlassBuilder

class AnonymousAuth(object):
    def authenticate(self, *args, **kwargs):
        return True
    
    def authorize(self, *args, **kwargs):
        return True


class AuthMaker(object):
    def __init__(self, plugin=None, plugin_dir=None):
        self.auth = AnonymousAuth()
        if plugin:
            if not plugin.startswith("plugin_auth_"):
                plugin = "plugin_auth_" + plugin
            self.auth = KlassBuilder(plugin, plugin_dir)(instantiate=True)
        self.authenticate = self.auth.authenticate
        self.authorize = self.auth.authorize


class PluginBase(object):
    def __init__(self, config):
        self._config = config
        
    def authenticate(self, *args, **kwargs):
        raise NotImplementedError("Abstract, implement in derived class")
    
    def authorize(self, *args, **kwargs):
        raise NotImplementedError("Abstract, implement in derived class")

