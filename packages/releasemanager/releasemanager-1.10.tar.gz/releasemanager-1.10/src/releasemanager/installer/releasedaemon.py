from releasemanager.config import ConfigLoader
from releasemanager.logger import ReleaseLogger
from target import NamedTarget

class ReleaseInstaller(object):
    def __init__(self, configName, configPath=None, configStyle='py'):
        self._configPath = configPath
        self._configName = configName
        self._configStyle = configStyle
        self.load()

    def _loadConfig(self):
        self._config = ConfigLoader(self._configPath, self._configStyle).load(self._configName)
        self.logger = ReleaseLogger(self._config, configPath=self._configPath)
    
    def _buildNamedTargets(self):
        """build a dict of env[name] = obj for environments and named targets"""
        # we intentionally wipe out any old named targets here,
        # so that when a config reloads, only the new ones are there
        self.environments = {}
        for nt in self._config.named_targets.target:
            configPath = getattr(nt, 'config_path', None)
            if not configPath:
                configPath = "%s/../target/%s" % (self._configPath, str(nt.environment))
            named_target = NamedTarget(str(nt.environment), str(nt.name), configPath=configPath)
            if not str(nt.environment) in self.environments:
                self.environments[str(nt.environment)] = {}
            self.environments[str(nt.environment)][str(nt.name)] = named_target
            self.logger.log("Named Target %s available for environment %s" % (str(nt.name), str(nt.environment)))
    
    def load(self):
        """the point of this abstraction rather than doing it all in one place is to be able
           to expose this so that a release daemon can get a new config, and reload it
           for the object, without having to restart"""
        self._loadConfig()
        self.logger.log("Loaded release installer config %s from %s" % (self._configName, self._configPath))
        self._buildNamedTargets()
    
    def reload(self):
        """just for more intuitive use, same as load"""
        return self.load()


    def install(self, env, name, resource, version):
        if not name.startswith('named_target_'):
            name = 'named_target_' + name
        if env in self.environments:
            if name in self.environments[env]:
                nt = self.environments[env][name]
                nt.install(resource, version)
                return True
        return False


    def report(self, env=None, name=None):
        """report on the named targets available"""
        if name and not name.startswith('named_target_'):
            name = 'named_target_' + name
        if env and name:
            if env in self.environments:
                if name in self.environments[env]:
                    return {env : name}
            return {}
        
        if env and not name:
            if env in self.environments:
                return {env: [v for v in self.environments[env].values()]}
            return {}
        
        if name and not env:
            envs = {}
            for e in self.environments:
                for n in e.values():
                    if n.lower() == name.lower():
                        envs[e] = name
            return envs 
        
        if (not name) and (not env):
            output = {}
            for e in self.environments:
                output[e] = [str(n._config.name) for n in self.environments[e].values()]
            return output
