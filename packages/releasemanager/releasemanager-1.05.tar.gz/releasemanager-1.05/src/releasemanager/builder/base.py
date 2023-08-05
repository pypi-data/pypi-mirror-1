import os
import pysvn, logging
from releasemanager import utils



SVN_USER = None
SVN_PASS = None
log = None

def pysvn_callback_get_login( realm, username, may_save ):
    return True, SVN_USER, SVN_PASS, False


class BuildBehavior(object):
    """base build behavior object.  all build behavior objects should
       implement the same basic clean and checkout behaviors
    """
    
    def __init__(self, config):
        self._config = config
        global SVN_PASS, SVN_USER
        SVN_USER = str(self._config.svn_user)
        SVN_PASS = str(self._config.svn_pass)
        self._create_component_markers()
    
    
    @property
    def svn_work_dir(self):
        work_dir = str(self._config.svn_work_dir)
        if not work_dir.startswith("/") or work_dir[0:3] == (":\\"):
            work_dir = os.path.join(os.path.join(self._configPath, "..%s..%s" % (os.sep, os.sep)), work_dir)
        return work_dir
    
    @property
    def archive_dir(self):
        archive_dir = str(self._config.archive_output)
        if not archive_dir.startswith("/") or archive_dir[0:3] == (":\\"):
            archive_dir = os.path.join(os.path.join(self._configPath, "..%s..%s" % (os.sep, os.sep)), archive_dir)
        return archive_dir


    def _build_unique_base_path(self, unique):
        base_path = os.path.join(self.svn_work_dir, unique)
        if not os.path.isdir(base_path):
             os.mkdir(base_path)
        return base_path
    
    def _build_unique_archive_path(self, unique):
        archive_path = os.path.join(self.archive_dir, unique)
        if not os.path.isdir(archive_path):
             os.mkdir(archive_path)
        return archive_path
            

    def clean(self, base_path=None, ignoreErrors=False):
        if not base_path:
            base_path = self.svn_work_dir
        if str(self._config.ignore_clean_error).lower == "true":
            ignoreErrors = True
        utils.clean(base_path, str(self._config.svn_target), self.svn_work_dir, ignoreErrors)


    def checkout(self, branch=None, revision=None, tag=None, url=None, trunk=False, unique=None):
        work_dir = os.path.join(self.svn_work_dir, unique)
        if not os.path.isdir(work_dir):
            os.mkdir(work_dir)
        os.chdir(work_dir)
        client = pysvn.Client()
        client.callback_get_login = pysvn_callback_get_login
        if trunk:
            client.export("%s/trunk" % str(self._config.svn_url), str(self._config.svn_target))
        elif branch:
            client.export("%s/branches/%s" % (str(self._config.svn_url), branch), str(self._config.svn_target))
        elif tag:
            client.export("%s/tags/%s" % (str(self._config.svn_url), tag), str(self._config.svn_target))
        elif revision and not url:
            client.export("%s/trunk" % str(self._config.svn_url), str(self._config.svn_target), revision=pysvn.Revision(pysvn.opt_revision_kind.number, revision))
        elif url and revision:
            client.export("%s" % url, str(self._config.svn_target), revision=pysvn.Revision(pysvn.opt_revision_kind.number, revision))
        elif url:
            client.checkout("%s" % url, str(self._config.svn_target))

    
    
    def setLogger(self, logger):
        global log
        log = logger
        
    
    def runLocalBuild(self, components=None, unique=None):
        try:
            if not components:
                funcs = self.component_markers['all']
                for func in funcs:
                    func(unique)
            else:
                # if we're given a list of components, run the functions associated
                # each in turn
                for c in components:
                    funcs = self.component_markers[c]
                    for func in funcs:
                        func(unique)
        finally:
            utils.clean(self.svn_work_dir, unique, self.svn_work_dir, True)


    def _create_component_markers(self):
        """subclasses override this method to provide their own actions"""
        raise NotImplementedError("create component markers must be established in subclass!")
    
    
    def fullBuild(self, branch=None, revision=None, url=None, tag=None, trunk=False, components=None, unique=None):
        """full build basically runs the necessary default methods, then defers to
           run the configured components of a particular build process
        """
        logging.info("Started %s Build..." % str(self._config.svn_target).capitalize())
        if not trunk:
            logging.info("Checking out new %s with branch: %s, revision: %s, url: %s, tag: %s" % (str(self._config.svn_target).capitalize(), branch, revision, url, tag))
        else:
            logging.info("Checking out %s from trunk" % str(self._config.svn_target).capitalize())
        self.checkout(branch=branch, revision=revision, url=url, tag=tag, trunk=trunk, unique=unique)
        self.runLocalBuild(components=components, unique=unique)
        logging.info("Finished %s Build." % str(self._config.svn_target).capitalize())


    def __call__(self, branch=None, revision=None, url=None, tag=None, trunk=None, components=None, unique=None):
        try:
            self.fullBuild(branch=branch, revision=revision, url=url, tag=tag, trunk=trunk, components=components, unique=unique)
            return True
        except:
            return False