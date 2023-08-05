import os, sys
from releasemanager import utils
from target import InstallBehavior

class SimpleInstall(InstallBehavior):
    def _install(self, resource):
        install_target = str(self._config.install_target)
        install_final = os.path.join(self.install_path, install_target)
        os.chdir(self.install_path)
        if not os.path.isdir(install_final):
            os.mkdir(install_final)
        outfile = os.path.join(install_final, str(self._config.file_name))
        open(outfile, 'wb').write(resource)


class SimpleUnarchive(InstallBehavior):
    def _install(self, resource):
        cwd = os.getcwd()
        install_target = str(self._config.install_target)
        install_final = os.path.join(self.install_path, install_target)
        os.chdir(self.install_path)
        if not os.path.isdir(install_final):
            os.mkdir(install_final)
        try:
            utils.unzip(resource, dir=install_final)
        finally:
            os.chdir(cwd)


class TemplateInstallBehavior(SimpleUnarchive):
    """template behavior for tests.  tests are all just simple unarchives of a mock resource"""
