import os
from releasemanager.config import KlassBuilder, ConfigLoader
from releasemanager import utils
from releasemanager.logger import ReleaseLogger

class NamedTarget(object):
    def __init__(self, env, configName, configPath=None):
        self._configPath = configPath
        self._configName = configName
        self.load()

    def _loadConfig(self):
        self._config = ConfigLoader(self._configPath).load(self._configName)
        self.logger = ReleaseLogger(self._config, configPath=self._configPath)
    
    def _buildInstallBehavior(self):
        install_behavior = str(self._config.install_behavior)
        install_behavior_configpath = self._configPath
        if hasattr(self._config, 'install_behavior_configpath'):
            install_behavior_configpath = str(self._config.install_behavior_configpath)
        self.installBehavior = KlassBuilder(install_behavior, configPath=install_behavior_configpath)(instantiate=True)
        self.installBehavior.setLogger(self.logger)
        self.installBehavior._configPath = install_behavior_configpath
    
    def load(self):
        """the point of this abstraction rather than doing it all in one place is to be able
           to expose this so that a release daemon can get a new config, and reload it
           for the object, without having to restart"""
        self._loadConfig()
        self.logger.log("Loaded config %s from %s" % (self._configName, self._configPath))
        self._buildInstallBehavior()
    
    def reload(self):
        """just for intuitive use, really not necessary"""
        return self.load()
    
    def install(self, resource, version):
        return self.installBehavior(resource, version)
    
    def getVersion(self):
        return self.installBehavior.version
    
    def resetVersion(self):
        self.installBehavior.resetVersion()


class InstallBehavior(object):
    """base install behavior"""
    def __init__(self, config):
        self._config = config
    
    def setLogger(self, logger):
        self.logger = logger
        

    def run(self, resource, version):
        """run's the install process.  cleans, establishes version, runs the subclass's overridden _install method"""
        self.logger.log("Cleaning version %s from %s" % (self.version, str(self._config.install_path)))
        self.clean()
        self.logger.log("Installing version %s in %s" % (version, str(self._config.install_path)))
        self._install(resource)
        self.version = version

    
    @property
    def install_path(self):
        install_path = str(self._config.install_path)
        if not install_path.startswith("/") or install_path[0:3] == (":\\"):
            install_path = os.path.join(os.path.join(self._configPath, "../../../"), install_path)
        return install_path


    @property
    def work_dir(self):
        work_dir = str(self._config.work_dir)
        if not work_dir.startswith("/") or work_dir[0:3] == (":\\"):
            work_dir = os.path.join(os.path.join(self._configPath, "../../../"), work_dir)
        return work_dir


    def clean(self):
        install_target = str(self._config.install_target)
        if hasattr(self._config, 'destroy_target') and str(self._config.destroy_target).lower() == 'true':
            utils.clean(self.install_path, install_target, self.work_dir, str(self._config.ignore_clean_error))

    def resetVersion(self):
        """reset version file to none"""
        version_file = "%s%s%s" % (os.path.join(self.install_path, str(self._config.install_target)), os.sep, ".release_manager_version")
        try:
            os.unlink(version_file)
        except:
            pass
    
    def getVersion(self):
        """look at the local .release_manager_version file created at install"""
        version_file = "%s%s%s" % (os.path.join(self.install_path, str(self._config.install_target)), os.sep, ".release_manager_version")
        try:
            version = open(version_file).read()
        except IOError:
            version = 'None'
        return version


    def setVersion(self, version):
        version_file = "%s%s%s" % (os.path.join(self.install_path, str(self._config.install_target)), os.sep, ".release_manager_version")
        try:
            fh = open(version_file, 'w')
            fh.write(version)
            fh.close()
        except Exception, e:
            self.logger.log("Unable to write version file for version %s! error:" % (version, e))
    
    version = property(getVersion, setVersion)

    
    def _install(self, resource):
        """subclass implements"""
        raise NotImplementedError("Must implement _install in subclass")


    def __call__(self, resource, version):
        return self.run(resource, version)