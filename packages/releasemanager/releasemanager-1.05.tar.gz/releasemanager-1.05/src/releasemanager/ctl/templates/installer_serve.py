import os, sys
from optparse import OptionParser
from twisted.internet import reactor
from releasemanager.svc.installer import ReleaseDaemonService

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conf")
DEFAULT_NAME = "template"

def main():
    usage = "usage: %prog {-n, --name} servername {-p, --path} configpath"
    parser = OptionParser(usage)
    parser.add_option("-n", "--name", dest="name", help="name of the server to start")
    parser.add_option("-p", "--path", dest="path", help="configuration path")
    (options, args) = parser.parse_args()
    name = options.name
    if not name:
        name = DEFAULT_NAME
    configPath = options.path
    if not configPath:
        configPath = CONFIG_PATH

    from twisted.web import server, resource
    """run server"""
    root = resource.Resource()
    rs = ReleaseDaemonService(name, configPath, configStyle='py')
    root.putChild('RPC2', rs)
    site = server.Site(root)
    port = int(str(rs._config.listen_port))
    rs.reactor.listenTCP(port, site)
    rs.reactor.run()

if __name__ == "__main__":
    main()