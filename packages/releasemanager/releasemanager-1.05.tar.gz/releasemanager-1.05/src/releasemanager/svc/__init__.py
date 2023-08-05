import os, sys
import socket
from twisted.web import xmlrpc
from twisted.internet import reactor
import logging

from releasemanager.auth import AuthMaker


class SvcBase(xmlrpc.XMLRPC):
    """service base"""
    prefix = None
    action_class = None
    allowNone = True
    config_base = None
    
    def __init__(self, configName, configPath=None, selfSufficient=True, configStyle='py'):
        self.reactor = None
        if selfSufficient:
            self.reactor = reactor
        if not configName.startswith("%s_" % self.prefix):
            configName = "%s_%s" % (self.prefix, configName)
        self._configName = configName
        self._configPath = "%s/%s" % (configPath, self.config_base)
        self._configStyle = configStyle
        self._logentry = "".join([i.capitalize() for i in self.prefix.split("_")])
        self.load()
   

    def load(self):
        self.actor = self.action_class(self._configName, configPath = self._configPath, configStyle=self._configStyle)
        self._config = self.actor._config  
        self._build_auth()


    def _build_auth(self):
        if not hasattr(self._config, 'auth_plugin'):
            self.auth = AuthMaker()
            return
        auth_plugin = str(self._config.auth_plugin)
        if hasattr(self._config.auth_plugin, 'plugin_path'):
            plugin_path = str(self._config.augh_plugin.plugin_path)
        else:
            plugin_path = "%s/../plugins/auth/" % self._configPath
            
        try:
            self.auth = AuthMaker(plugin=auth_plugin, plugin_dir=plugin_path)
        except LookupError:
            logging.info("%s: Lookup for Auth plugin %s failed!  Using Anonymous..." % (self._logentry, auth_plugin))
            self.auth = AuthMaker()

    

    

class SvcWorkerBase(SvcBase):
    """worker base"""

    def load(self):
        self.actor = self.action_class(self._configName, configPath = self._configPath, configStyle=self._configStyle)
        self._config = self.actor._config  
        self._build_auth()
        self.register()


    def register(self):
        for h in self._config.release_managers.host:
            url = "http://%s:%s/RPC2" % (str(h.name), str(h.port))
            try:
                s = xmlrpc.Proxy(url)
                registration = dict(
                    host = socket.gethostname(),
                    port = str(self._config.listen_port),
                    payload = self.actor.report(),
                )
                s.callRemote('register', '%s' % self.prefix, registration)
            except Exception, e:
                logging.info("%s: Unable to register with ReleaseManager %s, error: %s" % (self._logentry, url, str(e)))
        
    
    def xmlrpc_new_config(self, credentials, request_data):
        newconfig = request_data.get('newconfig')
        if not newconfig:
            return False
        # check that we're authenticated
        if not self.auth.authenticate(credentials):
            logging.info("%s: Not Authenticated for username: %s" % (self._logentry, credentials.get('username')))
            return False
        svc_role = str(self._config.svc_role)
        credentials['sa_role'] = svc_role
        if not self.auth.authorize(credentials):
            logging.info("%s: Not Authorized for build action %s for username: %s" % (self._logentry, svc_role, credentials.get('username')))
            return False
        config_file = os.path.join(self._configPath, "%s.xml" % self._configName)
        bak_file = os.path.join(self._configPath, "%s.xml~" % self._configName)
        if not os.path.isfile(config_file):
            return False
        try:
            orig = open(config_file).read()
            open(bak_file).write(orig)
            output = newconfig.data
            open(config_file, 'w').write(output)
        except IOError:
            try:
                bak = open(bak_file).read()
                open(config_file).write(bak)
            except IOError:
                raise
        self.load()
        return True

    
    def xmlrpc_get_config(self, credentials):
        # check that we're authenticated
        if not self.auth.authenticate(credentials):
            logging.info("%s: Not Authenticated for username: %s" % (self._logentry, credentials.get('username')))
            return False
        svc_role = str(self._config.svc_role)
        credentials['sa_role'] = svc_role
        if not self.auth.authorize(credentials):
            logging.info("%s: Not Authorized for build action %s for username: %s" % (self._logentry, svc_role, credentials.get('username')))
            return False
        config_file = os.path.join(self._configPath, "%s.xml" % self._configName)
        try:
            orig = open(config_file).read()
        except IOError:
            return False
        data = xmlrpc.Binary(orig)
        return data
