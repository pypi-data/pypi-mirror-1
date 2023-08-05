from simple_auth import auth as sa_auth
from releasemanager.auth import PluginBase

class SimpleAuthPlugin(PluginBase):
    sa_service = "releasemanager"
    def authenticate(self, credentials):
        username = credentials.get('username')
        password = credentials.get('password')
        return sa_auth.authenticate(username, password)

    def authorize(self, credentials):
        username = credentials.get('username')
        role = credentials.get('sa_role')
        return sa_auth.authorize(self.sa_service, username, role)    


