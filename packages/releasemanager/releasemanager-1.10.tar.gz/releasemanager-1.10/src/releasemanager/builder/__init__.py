from releasemanager.config import KlassBuilder, DEFAULT_CONFIG_PATH
from releasemanager.logger import ReleaseLogger

class ReleaseBuilder(object):
    """base release builder"""
    def __init__(self, configName, configPath=None, logger=None):
        self.buildBehavior = KlassBuilder(configName, configPath=configPath)(instantiate=True)
        # release builders really don't know anything about themselves, only their behaviors do
        # but the framework expects objects to have a _config, esp for lookup
        self._config = self.buildBehavior._config
        self.buildBehavior._configPath = configPath
        if not logger:
            rl = ReleaseLogger(self.buildBehavior._config, configPath=configPath)
            logger = rl.logger
        self.buildBehavior.setLogger(logger)
    
    def build(self, *args, **kwargs):
        return self.buildBehavior(*args, **kwargs)
    