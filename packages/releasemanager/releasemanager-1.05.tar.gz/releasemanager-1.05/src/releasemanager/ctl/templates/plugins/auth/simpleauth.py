from simple_auth.client.model import AuthModel
from releasemanager.auth import PluginBase

class SimpleAuthPlugin(PluginBase):
    def __init__(self, config):
        super(SimpleAuthPlugin, self).__init__(config)
        self.auth = AuthModel(str(self._config.db.uri), str(self._config.db.type))
        self.sa_service = str(self._config.svc_name)
    
    def authenticate(self, credentials):
        username = credentials.get('username')
        password = credentials.get('password')
        return self.auth.authenticate(username, password)

    def authorize(self, credentials):
        username = credentials.get('username')
        role = credentials.get('sa_role')
        return self.auth.authorize(self.sa_service, username, role)    


