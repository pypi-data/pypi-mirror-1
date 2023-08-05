from releasemanager.config import ConfigLoader, DEFAULT_CONFIG_PATH


class Project(object):
    """simple interrogatable project object"""
    def __init__(self, configName, configPath=None):
        self._configPath = configPath
        self._configName = configName
        self.load()

    @property
    def name(self):
        return str(self._config.name)

    def _loadConfig(self):
        self._config = ConfigLoader(self._configPath).load(self._configName)
    
    def load(self):
        self._loadConfig()

    @property
    def targets(self):
        return [str(t.name) for t in self._config.targets.target]