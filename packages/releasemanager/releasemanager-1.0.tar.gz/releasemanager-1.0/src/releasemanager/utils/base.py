import os
from releasemanager.builder import ReleaseBuilder
from optparse import OptionParser
import datetime

def util_build(name):
    usage = "usage: %prog {-b, --branch} branch {-r, --rev} revision {-u, --url} url {-t, --trunk} trunk"
    parser = OptionParser(usage)
    parser.add_option("-b", "--branch", dest="branch", help="branch to check out and build")
    parser.add_option("-r", "--revision", dest="rev", help="revision to check out and build")
    parser.add_option("-u", "--url", dest="url", help="url to use instead of default")
    parser.add_option("-t", "--trunk", dest="trunk", help="use trunk, true/false")
    parser.add_option("-a", "--tag", dest="tag", help="tag name")
    (options, args) = parser.parse_args()

    branch = options.branch
    revision = options.rev
    url = options.url
    tag = options.tag
    trunk = options.trunk
    use_trunk = False
    if trunk and trunk.lower() == 'true':
        use_trunk = True
    if not (branch or revision or url or trunk or tag):
        parser.error("Must pass in a specific branch, revision, url, or just trunk")
    local_conf = os.path.join(os.getcwd(), "conf")
    if not os.path.isdir(local_conf):
        local_conf = os.path.join(os.getcwd(), "..%sconf" % os.sep)
        if not os.path.isdir(local_conf):
            raise LookupError("Could not find configuration directory!")
    configPath = "%s%sbuilder" % (local_conf, os.sep)
    rb = ReleaseBuilder("release_builder_%s" % name, configPath = configPath)
    unique = "interactive_%s_%s" % (datetime.datetime.now().strftime("%Y%m%d%H%M%S"), "FALSE")
    rb.build(branch=branch, revision=revision, url=url, tag=tag, trunk=use_trunk, unique=unique)
