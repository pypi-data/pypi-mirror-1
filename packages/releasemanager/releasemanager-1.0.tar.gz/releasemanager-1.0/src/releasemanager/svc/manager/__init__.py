from twisted.web import xmlrpc
from twisted.internet import reactor
import logging, datetime

from releasemanager.manager import ReleaseManager
from releasemanager.svc import SvcBase


class ReleaseManagerService(SvcBase):
    """build host service"""
    prefix = "release_manager"
    action_class = ReleaseManager
    config_base = "manager"
    
    
    def xmlrpc_request_action(self, credentials, request_data):
        trans_id = self.actor.start_transaction()
        request_data['__relman_transaction__'] = trans_id
        request_data['__relman_unique_request_base__'] = "%s_%s_%s" % (credentials.get('username'), datetime.datetime.now().strftime("%Y%m%d%H%M%S"), trans_id)
        self.actor.request_action(credentials, request_data)
        return trans_id

    def xmlrpc_query_transaction(self, trans_id):
        return self.actor.query_transaction(trans_id)    


    def xmlrpc_register(self, reg_type, registration):
        logging.info("%s: Requested registration from %s with from host %s on port %s" % (self._logentry, reg_type, registration.get('host'), registration.get('port')))
        return self.actor.register(reg_type, registration)


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
    rs = ReleaseManagerService(name, configPath)
    root.putChild('RPC2', rs)
    site = server.Site(root)
    port = int(str(rs._config.listen_port))
    rs.reactor.listenTCP(port, site)
    rs.reactor.run()
