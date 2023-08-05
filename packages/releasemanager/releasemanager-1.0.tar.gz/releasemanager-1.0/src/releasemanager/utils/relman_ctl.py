#!/usr/bin/env python

import os, sys
from releasemanager.ctl.generate import ManagerCreator, BuilderCreator, \
    InstallerCreator, PluginCreator
from optparse import OptionParser

valid_commands = ["generate"]
valid_targets = {
    "installer" : InstallerCreator, 
    "builder" : BuilderCreator, 
    "manager" : ManagerCreator,
}
builtin_auth_plugins = ["simpleauth"]

def main():
    usage = "usage: %prog [generate] [installer|builder|manager] [name] [options]"
    parser = OptionParser(usage)
    parser.add_option("-a", "--auth-plugin", dest="auth", help="use a builtin auth plugin")
    (options, args) = parser.parse_args()
    
    if len(args) != 3:
        parser.error("Requires a command, a target, and a new name")
    command, target, name = args
    command = command.lower()
    target = target.lower()
    auth = options.auth
    if command not in valid_commands:
        parser.error("Command %s is not a valid command" % command)
    if target not in valid_targets:
        parser.error("Target %s is not a valid target" % target)
    
    base_path = os.getcwd()
    gen = valid_targets[target](base_path, name)
    gen.generate()
    
    # now for plugins
    if auth:
        pl = PluginCreator("auth", auth, install_base=os.path.join(base_path, name))
        pl.install()


if __name__ == "__main__":
    main()
