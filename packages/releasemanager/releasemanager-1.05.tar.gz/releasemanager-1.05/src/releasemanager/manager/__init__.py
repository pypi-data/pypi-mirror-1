import os, sys
import xmlrpclib, socket
from twisted.web import xmlrpc
import tempfile, datetime

from releasemanager.config import ConfigLoader, DEFAULT_CONFIG_PATH
from releasemanager import utils
from releasemanager.logger import ReleaseLogger
from releasemanager.project import Project
from releasemanager.persist import Persistence


class ReleaseManager(object):
    """the brains of the operation ;) """
    def __init__(self, configName, configPath=None, configStyle='py'):
        self._configPath = configPath
        self._configName = configName
        self._configStyle = configStyle
        self.load()


    def _cleanPaths(self):
        work_dir = str(self._config.work_dir)
        if not work_dir.startswith("/") or work_dir[0:3] == (":\\"):
            work_dir = os.path.join(os.path.join(self._configPath, "..%s..%s" % (os.sep, os.sep)), work_dir)
        self.work_dir = work_dir


    def _loadConfig(self):
        self._config = ConfigLoader(self._configPath, self._configStyle).load(self._configName)
        self.logger = ReleaseLogger(self._config, configPath=self._configPath)
    
    def _buildPersistence(self):
        persist_dir = os.path.join(os.path.join(self._configPath, "..%s..%s" % (os.sep, os.sep)), "plugins%spersist" % os.sep)
        self.persistence = Persistence(self._config, persist_dir)
        

    def _loadProjects(self):
        # intentionally obliterative
        self.projects = {}
        projects = []
        load_from = str(self._config.projects.dir).lower()
        if len(load_from) == 0:
            load_from = "%s/../project/" % self._configPath
        if str(self._config.projects.all).lower() == "true":
            for f in os.listdir(load_from):
                if f.startswith("project_definition_"):
                    projects.append(f.replace(".xml", ""))
        else:
            for proj in self._config.projects.project:
                fname = "%s%s.xml" % ("project_definition_", str(proj.name))
                if os.path.isfile(os.path.join(load_from, fname)):
                    projects.append(fname.replace(".xml", ""))
            
        for p_name in projects:
            proj = Project(p_name, load_from)
            self.projects[proj.name] = proj
            self.logger.log("ReleaseManager: Loaded project %s" % p_name)
            

    def baseErrback(self, error, history):
        msg = "ReleaseManager: error %s" % str(error)
        self.logger.log(msg)
        self.save_history(history, False, msg)
        return False
    
    def load(self):
        """the point of this abstraction rather than doing it all in one place is to be able
           to expose this so that we can reload our config for the object, without having to restart"""
        self._loadConfig()
        self._cleanPaths()
        self.logger.log("Loaded release installer config %s from %s" % (self._configName, self._configPath))
        self._buildPersistence()
        self._build_registrations()
        self._loadProjects()
        
    
    def getTransaction(self, request_data):
        return request_data.get('__relman_transaction__', '')
    
    
    def getUniqueBase(self, request_data):
        return request_data.get('__relman_unique_request_base__', '')
    
    
    def _build_registrations(self):
        if not hasattr(self, 'registrations'):
            self.registrations = {}
        if not hasattr(self, 'use_cache'):
            self.use_cache = {}
        for t in self._config.registration:
            if not str(t.name) in self.registrations:
                self.registrations[str(t.name)] = {}
            if not str(t.name) in self.use_cache:
                self.use_cache[str(t.name)] = {}
        db_regs = self.persistence.Registration.select()
        for reg in db_regs:
            # if the registration is greater than a day old, check it, then get rid of it
            if not self.check_registration(reg, kill=True):
                continue
            if reg.type in self.registrations:
                self.registrations[reg.type][reg.location] = reg.load()
                if not reg.type in self.use_cache:
                    self.use_cache[reg.type] = {}
                if not reg.location in self.use_cache[reg.type]:
                    self.use_cache[reg.type][reg.location] = 0


    def check_registration(self, reg, kill=False):
        s = socket.socket()
        host, port = reg.location.split(":")
        connected = True
        try:
            s.connect((host, int(port)))
        except:
            connected = False
        if connected:
            return True
        # if not connected, check if we should just wipe it
        # we're going to return false regardless, since it just said
        # it wasn't connected
        if kill:
            yesterday = datetime.datetime.now() - datetime.timedelta(0, 86400)
            if reg.registered_at > yesterday:
                reg.delete()
                reg.flush()
        return False

    
    def start_transaction(self):
        trans = self.persistence.Transaction()
        trans.status = "STARTED"
        trans.started_at = datetime.datetime.now()
        trans.save()
        trans.flush()
        trans_id = trans.id
        trans.expunge()
        return trans_id

    
    def save_transaction(self, trans_id, status):
        trans = self.persistence.Transaction.get_by(id=trans_id)
        trans.status = status
        trans.completed_at = datetime.datetime.now()
        trans.save()
        trans.flush()
        trans.expunge()


    def query_transaction(self, trans_id):
        trans = self.persistence.Transaction.get_by(id=trans_id)
        status = trans.status
        trans.expunge()
        return status


    def make_history(self, credentials, request_data):
        """creates a history record with some defaults"""
        username = credentials.get('username', 'anonymous')
        action = request_data.get('action', 'unknown action')
        project = request_data.get('project', 'unknown project')
        occurred = datetime.datetime.now()
        trans_id = self.getTransaction(request_data)
        hist = self.persistence.History()
        hist.username = username
        hist.action = action
        hist.project = project
        hist.occurred = occurred
        hist.transaction_id = trans_id
        hist.success = False
        hist.message = "New Request"
        hist.save()
        hist.flush()
        hist_id = hist.id
        hist.expunge()
        return hist_id

    def save_history(self, hist_id, success, message):
        hist = self.persistence.History.get_by(id=hist_id)
        hist.success = success
        if len(message) > 255:
            message = message[0:255]
        hist.message = message
        hist.save()
        hist.flush()
        hist.expunge()

    def register(self, type, data):
        allowed_type = False
        for t in self._config.registration:
            if str(t.name).lower() == type.lower():
                allowed_type = t
                break
        if not allowed_type:
            return False
        for param in allowed_type.param:
            if param.required.lower() == "true":
                if not str(param.name).lower() in data:
                    return False
        # our registrations are held in a dict, key of ip_or_host:port pair
        location = "%s:%s" % (data['host'], data['port'])
        self.registrations[str(allowed_type.name)][location] = data
        self.use_cache[str(allowed_type.name)][location] = 0
        reg = self.persistence.Registration.get_by(type=str(allowed_type.name), location=location)
        if not reg:
            reg = self.persistence.Registration()
            reg.location = location
            reg.type = str(allowed_type.name)
        reg.registered_at = datetime.datetime.now()
        reg.store(data)
        reg.save()
        reg.flush()
        return True


    def report_registrations(self):
        self._build_registrations()
        data = {'projects' : [{k : [nt for nt in v.targets]} for k, v in self.projects.items()]}
        data.update(self.registrations)
        return data

    
    def request_action(self, credentials, request_data):
        """returns tuple of status, payload"""
        self.logger.log("ReleaseManager: user %s requested action %s with data %s" % (credentials.get('username'), request_data.get('action'), request_data))
        hist = self.make_history(credentials, request_data)
        allowed_action = False
        action_type = request_data.get('action')
        if not action_type:
            msg = "No action type given in request! request data was %s" % request_data
            self.logger.log(msg)
            self.save_history(hist, False, msg)
            return False
        for reg in self._config.registration:
            if action_type.lower() == str(reg.action):
                allowed_action = reg
                break
        if not allowed_action:
            msg = "ReleaseManager: user %s requested action %s with but we only have %s available" % (credentials.get('username'), request_data.get('action'), [str(reg.action) for reg in self._config.registration])
            self.logger.log(msg)
            self.save_history(hist, False, msg)
            return False
        # this abstraction is done so that we can easily extend the base release manager later
        # by simply adding _run_ methods
        func = getattr(self, "_run_%s" % action_type.lower())
        if not func:
            raise NotImplementedError("There is a problem with your configuration for allowed actions!  action requested %s" % action_type.lower())
        func(credentials, request_data, history=hist)


    def _run_build(self, credentials, request_data, from_install=False, extra=None, history=None):
        project = request_data.get('project')
        if not project:
            msg = "ReleaseManager: No project given"
            self.logger.log(msg)
            return False
        if not project.lower() in self.projects:
            self.logger.log("%s: Requested build of %s, but configured projects are only %s" % ("ReleaseManager", project, [p for p in self.projects.keys()]))
            return False
        registered_project = 'release_builder_' + project
        build_host = None
        available_hosts = []
        for loc in self.registrations['build_host']:
            reg_data = self.registrations['build_host'][loc]
            if registered_project in reg_data['payload']:
                used_times = self.use_cache['build_host'][loc]
                available_hosts.append((used_times, loc))
        min_used = 0
        for used_times, loc in available_hosts:
            if used_times <= min_used:
                min_used = used_times
                build_host = loc
        if not build_host:
            self.logger.log("ReleaseManager: attempted build for project %s, no build host found.  build hosts are %s" % (project, [(loc, self.registrations['build_host'][loc]) for loc in self.registrations['build_host']]))
            return False
        url = "http://%s/RPC2" % loc
        self.remote_build(credentials, request_data, url, from_install=from_install, extra=extra, history=history)
        


    def remote_build(self, credentials, request_data, url, from_install=False, extra=None, history=None):
        builder = xmlrpc.Proxy(url)
        d = builder.callRemote('build', credentials, request_data)
        if from_install:
            print "Exiting remote_build with from_install set to true"
            d.addCallback(self.builderCallback, history, request_data).addCallback(self.installerAfterBuildCallback, credentials, request_data, extra, history).addErrback(self.baseErrback, history)
        else:
            print "Exiting remote_build with from_install set to false"
            d.addCallback(self.builderCallback, history, request_data).addErrback(self.baseErrback, history)
            


    def builderCallback(self, data, history, request_data):
        status, resource = data
        hist = self.persistence.History.get_by(id=history)
        msg = "ReleaseManager: returned status %s for action %s on project %s " % (status, hist.action, hist.project)
        hist.expunge()
        self.logger.log(msg)
        self.save_history(history, status, msg)
        trans_id = self.getTransaction(request_data)
        self.save_transaction(trans_id, 'BUILD_STARTED')
        trans_status = "BUILD_FAILED"
        if status:
            trans_status = "BUILD_COMPLETED"
            self.save_transaction(trans_id, trans_status)
            return resource
        self.save_transaction(trans_id, trans_status)
        return False

    
    def _run_install(self, credentials, request_data, history=None):
        project = request_data.get('project')
        self.logger.log("ReleaseManager: user %s requested install for %s" % (credentials.get('username'), project))
        if not project:
            return False
        env = request_data.get('env', '').lower()
        if len(env) == 0:
            self.logger.log("ReleaseManager: attempted install for project %s, invalid environment provided" % project)
            return False
        # what needs to happen here is that we need to find all the targets
        # that a particular project has, and build daemons for each
        proj = self.projects.get(project)
        if not proj:
            return False
        # endpoints will contain a dict of targets that will point to a dict of
        # resource binary and rd's that get it
        endpoints = {}
        # build rd's per target
        for target in proj.targets:
            release_daemons = []
            for loc in self.registrations['release_installer']:
                inst = self.registrations['release_installer'][loc]['payload']
                if env in inst:
                    inst_targets = inst[env]
                    if target in inst_targets:
                        release_daemons.append(loc)
            endpoints[target] = {'release_daemons' : release_daemons}
            # if we found no available release daemons, return broken
            if len(release_daemons) == 0:
                self.logger.log("ReleaseManager: attempted install for project %s, in environment %s,  no release daemons found" % (project, env))
                self.logger.log("ReleaseManager: release daemons are %s" % [(loc, self.registrations['release_installer'][loc]) for loc in self.registrations['release_installer']])
                return False        

        # get the indexed resource
        self._run_build(credentials, request_data, from_install=True, extra={'project' : proj, 'endpoints' : endpoints}, history=history)
        


    def installerAfterBuildCallback(self, resource, credentials, request_data, extra, history):
        endpoints = extra.get('endpoints')
        proj = extra.get('project')
        if not resource:
            msg = "ReleaseManager: Failed to install %s, no resource returned from build" % (proj.name)
            self.logger.log(msg)
            self.save_history(history, False, msg)
            return False
        # build a dict of the new data, split by resource
        split_resources = self.split_resource(resource)
        for target in split_resources:
            endpoints[target]['resource'] = split_resources[target]
        # run the real installs against all known release daemons
        trans_id = self.getTransaction(request_data)
        self.save_transaction(trans_id, 'INSTALL_STARTED')            
        try:
            trans_status = "INSTALL_COMPLETED"
            for target in proj.targets:
                release_daemons = endpoints[target]['release_daemons']
                data = endpoints[target]['resource']
                if not isinstance(data, xmlrpc.Binary):
                    data = xmlrpc.Binary(data)
                for rd in release_daemons:
                    url = "http://%s/RPC2" % rd
                    self.remote_install(credentials, request_data, (data, target), url, history)
        except Exception, e:
            self.logger.log("ReleaseManager: Failure to install, error was %s" % str(e))
            trans_status = "INSTALL_FAILED"
        self.save_transaction(trans_id, trans_status)


    def remote_install(self, credentials, request_data, data, url, history):
        installer = xmlrpc.Proxy(url)
        resource, name = data
        # building what version should look like
        branch = request_data.get('branch')
        revision = request_data.get('revision')
        svn_url = request_data.get('url')
        tag = request_data.get('tag')
        trunk = request_data.get('trunk')
        version = request_data.get('version')
        if not version:
            version_base = "%s: " % name
            if trunk:
                version = version_base + " from trunk"
            else:
                if svn_url:
                    version_base += " from svn url: %s" % svn_url
                if branch:
                    version_base += " from branch: %s" % branch
                if tag:
                    version_base += " from tag: %s" % tag
                if revision:
                    version_base += " from revision: %s" % revision
                version = version_base  
        
        request_data['name'] = name
        request_data['version'] = version
        request_data['resource'] = resource
        self.logger.log("ReleaseManager: about to attempt to install %s at version %s requested by user %s" % (name, version, credentials.get('username')))
        d = installer.callRemote('install', credentials, request_data)
        d.addCallback(self.installerCallback, history).addErrback(self.baseErrback, history)


    def installerCallback(self, data, history):
        msg = "ReleaseManager: install returned status %s" % (data)
        self.logger.log(msg)
        self.save_history(history, data, msg)
        return data

    
    def split_resource(self, original_resource):
        """splits the original resource into a group of files and an index file
           reads the index file, and builds a dict of targets and data"""
        split_resources = {}
        cwd = os.getcwd()
        try:
            os.chdir(self.work_dir)
            tmp_dir = tempfile.mkdtemp(prefix="rlsmgr_", dir=self.work_dir)
            if not os.path.isdir(tmp_dir):
                os.mkdir(tmp_dir)
            utils.unzip(original_resource.data, dir=tmp_dir)
            index_data = open(os.path.join(tmp_dir, "index.txt")).readlines()
            for line in index_data:
                target, rsrc_fname = line.split("\t")
                target = target.replace(":", "")
                split_resources[target] = open(os.path.join(tmp_dir, rsrc_fname.strip()), 'rb').read()
                self.logger.log("ReleaseManager: extracted resource %s to install to target %s" % (rsrc_fname, target))
            utils.clean(self.work_dir, os.path.split(tmp_dir)[1], ignoreErrors=True)
        finally:
            os.chdir(cwd)
        return split_resources
