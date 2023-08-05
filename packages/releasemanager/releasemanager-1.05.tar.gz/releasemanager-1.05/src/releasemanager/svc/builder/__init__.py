from twisted.web import xmlrpc
from twisted.internet import reactor
import logging

from releasemanager.builder.buildhost import BuildHost
from releasemanager.svc import SvcWorkerBase


class BuildHostService(SvcWorkerBase):
    """build host service"""
    prefix = "build_host"
    action_class = BuildHost
    config_base = "builder"
    
    def xmlrpc_build(self, credentials, request_data):
        name = request_data.get('project', '')
        branch = request_data.get('branch', '')
        revision = request_data.get('revision', '')
        url = request_data.get('url', '')
        tag = request_data.get('tag', '')
        trunk = request_data.get('trunk', False)
        unique_base = request_data.get('__relman_unique_request_base__', '')
        if not self.auth.authenticate(credentials):
            logging.info("%s: Not Authenticated for username: %s" % (self._logentry, credentials.get('username')))
            return (False, '')

        # clean up project name
        if not name.startswith("release_builder_"):
            name = "release_builder_" + name
        # check that we're authorized to go forward
        auth_role = str(self.actor.projects[name]._config.auth_role)
        credentials['sa_role'] = auth_role
        if not self.auth.authorize(credentials):
            logging.info("%s: Not Authorized for build action %s for username: %s" % (self._logentry, auth_role, credentials.get('username')))
            return (False, '')
        status, resource = self.actor.build(name, branch=branch, revision=revision, url=url, tag=tag, trunk=trunk, unique=unique_base)
        if not isinstance(resource, xmlrpc.Binary):
            resource = xmlrpc.Binary(resource)
        logging.info("%s: Status of build for %s is %s" % (self._logentry, name, status))
        return (status, resource)
        

    def xmlrpc_report(self, credentials, request_data):
        name = request_data.get('project', '')
        # check that we're authenticated
        if not self.auth.authenticate(credentials):
            logging.info("%s: Not Authenticated for username: %s" % (self._logentry, credentials.get('username')))
            return False
        svc_role = str(self._config.svc_role)
        credentials['sa_role'] = svc_role
        if not self.auth.authorize(credentials):
            logging.info("%s: Not Authorized for build action %s for username: %s" % (self._logentry, svc_role, credentials.get('username')))
            return False
        output = self.actor.report(name=name)
        logging.info("%s: Report output %s" % (self._logentry, output))
        return output


if __name__ == "__main__":
    from optparse import OptionParser
    usage = "usage: %prog {-n, --name} servername {-p, --path} configpath"
    parser = OptionParser(usage)
    parser.add_option("-n", "--name", dest="name", help="name of the server to start")
    parser.add_option("-p", "--path", dest="path", help="configuration path")
    (options, args) = parser.parse_args()
    name = options.name
    configPath = options.path

    from twisted.web import server, resource
    """run server"""
    root = resource.Resource()
    rs = BuildHostService(name, configPath)
    root.putChild('RPC2', rs)
    site = server.Site(root)
    port = int(str(rs._config.listen_port))
    rs.reactor.listenTCP(port, site)
    rs.reactor.run()
