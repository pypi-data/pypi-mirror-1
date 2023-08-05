from twisted.web import xmlrpc
from twisted.internet import reactor
import logging

from releasemanager.installer.releasedaemon import ReleaseInstaller
from releasemanager.svc import SvcWorkerBase


class ReleaseDaemonService(SvcWorkerBase):
    """release daemon service"""
    prefix = "release_installer"
    action_class = ReleaseInstaller
    config_base = "installer"

    def xmlrpc_install(self, credentials, request_data):
        env = request_data.get('env', '')
        name = request_data.get('name', '')
        resource = request_data.get('resource', '')
        version = request_data.get('version', '')
        logging.info("%s: request made for user: %s, installing %s into %s at version %s" % (self._logentry, credentials.get('username'), name, env, version))
        # check that we're authenticated
        if not self.auth.authenticate(credentials):
            logging.info("%s: Not Authenticated for username: %s" % (self._logentry, credentials.get('username')))
            return False
        # clean up project name
        if not name.startswith("named_target_"):
            name = "named_target_" + name
        # check that we're authorized to go forward
        if not env in self.actor.environments:
            logging.info("%s: No such environment: %s" % (self._logentry, env))
            return False
        if not name in self.actor.environments[env]:
            logging.info("%s: No such name: %s for environment %s" % (self._logentry, name, env))
            return False
        # get the auth_role from the named target for the requested environment
        # because named targets are generic, the actual auth role assigned is
        # set up on the install behavior, since it is that which we intend to control
        auth_role = (self.actor.environments[env][name].installBehavior._config.auth_role)
        credentials['sa_role'] = auth_role
        if not self.auth.authorize(credentials):
            logging.info("%s: Not Authorized for install action %s for username: %s" % (self._logentry, auth_role, credentials.get('username')))
            return False
        success = self.actor.install(env, name, resource.data, version)
        return success
        

    def xmlrpc_report(self, credentials, request_data):
        env = request_data.get('env', '')
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
        output = self.actor.report(env=env, name=name)
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
    rs = ReleaseDaemonService(name, configPath)
    root.putChild('RPC2', rs)
    site = server.Site(root)
    port = int(str(rs._config.listen_port))
    rs.reactor.listenTCP(port, site)
    rs.reactor.run()
