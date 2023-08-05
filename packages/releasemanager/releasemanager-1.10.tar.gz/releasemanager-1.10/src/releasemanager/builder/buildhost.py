import os, re
import tempfile, shutil

from releasemanager.config import ConfigLoader
from releasemanager import utils
from releasemanager.logger import ReleaseLogger
from releasemanager.builder import ReleaseBuilder


class BuildHost(object):
    def __init__(self, configName, configPath=None, configStyle='py'):
        self._configPath = configPath
        self._configName = configName
        self._configStyle = configStyle
        self.load()

    def _loadConfig(self):
        self._config = ConfigLoader(self._configPath, self._configStyle).load(self._configName)
        self.logger = ReleaseLogger(self._config, configPath=self._configPath)
    
    def _buildReleaseBuilders(self):
        """build a dict of projects available for building"""
        # we intentionally wipe out any old projects here,
        # so that when a config reloads, only the new ones are there
        self.projects = {}
        for proj in self._config.projects.project:
            name = str(proj.name)
            if not name.startswith("release_builder_"):
                name = "release_builder_" + name
            configPath = getattr(proj, 'config_path', None)
            if not configPath:
                configPath = self._configPath
            rb = ReleaseBuilder(name, configPath = configPath, logger=self.logger)
            self.projects[name] = rb
            self.logger.log("Project %s available for build" % name)
    
    def load(self):
        """the point of this abstraction rather than doing it all in one place is to be able
           to expose this so that we can get a new config, and reload it
           for the object, without having to restart"""
        self._loadConfig()
        self.logger.log("Loaded project builder config %s from %s" % (self._configName, self._configPath))
        self._buildReleaseBuilders()

    
    def reload(self):
        """just for intuitive use, really not necessary"""
        return self.load()


    def _do_build(self, name, branch=None, revision=None, url=None, tag=None, trunk=False, unique=None):
        if name in self.projects:
            rb = self.projects[name]
            components = None
            if hasattr(rb._config.output_targets, "components"):
                components = [c.strip() for c in str(rb._config.output_targets.components).split(",")]
            return rb.build(branch=branch, revision=revision, url=url, tag=tag, trunk=trunk, components=components, unique=unique)
        return False

    def build(self, name, branch=None, revision=None, url=None, tag=None, trunk=False, unique=None):
        # check the name, build try the actual build
        if not name.startswith('release_builder_'):
            name = 'release_builder_' + name        
        # get rb to use config later
        rb = self.projects[name]
        
        
        # actually do the build
        if not self._do_build(name, branch=branch, revision=revision, url=url, tag=tag, trunk=trunk, unique=unique):
            return (False, "")

        # archive the whole bit, build an index, and send it back
        archive_dir = str(rb._config.archive_output)
        if not archive_dir.startswith("/") or archive_dir[0:3] == (":\\"):
            archive_dir = os.path.join(os.path.join(self._configPath, "../../"), archive_dir)
        archive_unique = os.path.join(archive_dir, unique)
        if not os.path.isdir(archive_unique):
            os.mkdir(archive_unique)
        files = []
        for fname in rb._config.output_targets.file:
            for f in os.listdir(archive_unique):
                filename = os.path.basename(f)
                if hasattr(fname, "ignorecase") and getattr(fname, "ignorecase").lower() == "y":
                    matcher = re.compile(str(fname.name), re.IGNORECASE)
                else:
                    matcher = re.compile(str(fname.name))
                match = matcher.search(filename)
                if match:
                    target = str(fname.target)
                    files.append((target, filename))
        work_dir = str(self._config.work_dir)
        if not work_dir.startswith("/") or work_dir[0:3] == (":\\"):
            work_dir = os.path.join(os.path.join(self._configPath, "../../"), work_dir)
        tmpdir = tempfile.mkdtemp(dir=work_dir, prefix="bldhst_")
        rsrc_dir = os.path.join(tmpdir, "resource")
        os.mkdir(rsrc_dir)
        index_file = os.path.join(rsrc_dir, "index.txt")
        fh = open(index_file, 'w')
        for t, f in files:
            shutil.copy(os.path.join(archive_unique, f), rsrc_dir)
            fh.write("%s:\t%s%s" % (t, f, os.linesep))
        fh.close()
        utils.makeZip(rsrc_dir, tmpdir, str(self._config.build_file), skip_files=[str(self._config.build_file)])
        out_file = os.path.join(tmpdir, str(self._config.build_file))
        data = open(out_file, 'rb').read()
        utils.clean(tmpdir, os.path.split(rsrc_dir)[1], ignoreErrors=True)
        utils.clean(work_dir, os.path.split(tmpdir)[1], ignoreErrors=True)
        utils.clean(archive_dir, unique, ignoreErrors=True)
        return (True, data)


    def report(self, name=None):
        """report on the named targets available"""
        if name:
            if name.startswith('release_builder_'):
                name = 'release_builder_' + name
            for p in self.projects:
                if p.lower() == name.lower():
                    return True
            return False
        else:
            return [p for p in self.projects]
        
