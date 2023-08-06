# Copyright (c) 2008,2009  Mediamatic Lab
# See LICENSE for details.

"""
cli.py

Command-line access to the AnyMeta API and registry.
"""

# regular imports
import sys
import re
from optparse import OptionParser

from anymeta                import __version__
from anymeta.api            import AnyMetaAPI
from anymeta.api.registry   import AnyMetaRegistry, AnyMetaRegistryException


def usage():
    """
    Show usage message and exit.
    """
    print "any-registry %s" % __version__
    print "Usage %s [opts] <command> [cmdoptions]" % sys.argv[0]
    print
    print "Command is one of:"
    print " list           - List all registry entries"
    print " gui            - Show graphical user interface (linux only)"
    print " add <id> <url> - Add API endpoint"
    print " del <id>       - Remove API endpoint"
    print " cli <id>       - Commandline interface"
    print
    sys.exit(1)


def print_list(r):
    """
    Print a list entries in the given registry.
    """
    all = r.getAll()
    for entry in all.keys():
        print "%-20s- %s" % (entry, all[entry]['entrypoint'])
    print


def main():
    """
    Main entry point for cli access.
    """
    parser = OptionParser()
    parser.add_option("-f", "--file", help="Registry file", action='store')

    (options, args) = parser.parse_args()

    registry = AnyMetaRegistry(options.file)

    if len(args) < 1:
        usage()

    cmd = args[0]
    args = args[1:]

    print "Registry: %s" % registry.cfgfile
    print

    if cmd == "list":
        print_list(registry)
        print "OK"
    elif cmd == "gui":
        from anymeta.gtk import registry
        d = registry.RegistryDialog()
        d.run_as_main()

    elif cmd == "cli":

        try:
            id,  = tuple(args)
        except Exception, e:
            usage()

        try:
            r = registry.get(id)
        except AnyMetaRegistryException, e:
            print "No such entry"
            exit()

        welcomemsg = "Use the 'api' python variable to access %s (%s)" % (id, r['entrypoint'])

        api = AnyMetaAPI.from_registry(id)
        result = api.doMethod("anymeta.user.info", {})
        welcomemsg += "\n\nLogged in as %s." % result['title']
        
        try:
            raise ImportError()
            from twisted.conch import stdio
            from twisted.internet import reactor, stdio as sio
            from twisted.conch.insults.insults import ServerProtocol

            class WelcomeManhole(stdio.ConsoleManhole):
                def initializeScreen(self):
                    self.terminal.reset()
                    self.terminal.write("\n%s\n\n" % welcomemsg)
                    self.terminal.write(self.ps[self.pn])
                    self.setInsertMode()


            import tty, termios, os

            fd = sys.__stdin__.fileno()
            oldSettings = termios.tcgetattr(fd)
            tty.setraw(fd)
            try:
                p = stdio.ServerProtocol(WelcomeManhole, {'api': api})
                sio.StandardIO(p)
                reactor.run()
            finally:
                termios.tcsetattr(fd, termios.TCSANOW, oldSettings)
                os.write(fd, "\r\x1bc\r")

        except ImportError,e :
            import os
            print welcomemsg
            os.system("python -i -c\"from anymeta.api import AnyMetaAPI; api = AnyMetaAPI.from_registry('%s');\"" % id)

        print "Bye!"
        print

    elif cmd == "add":

        try:
            id, url = tuple(args)
        except Exception, e:
            usage()

        if not re.match(r'^https?://', url):
            url = "http://" + url

        if url[-1:] != "/":
            url += "/"

        if not re.match(r'^.*services/rest/', url):
            url += "services/rest/"

        try:
            r = registry.get(id)
            print "Already registered"
            print
            print "'%s' is already linked, to %s" % (id, r['entrypoint'])
            print
            sys.exit(1)
        except AnyMetaRegistryException, e:
            pass

        try:
            registry.register_interactive(id, url)
        except Exception, e:
            print "Error registering: ", e
            print
            print "Please provide a valid AnyMeta endpoint as second argument."
            print
            sys.exit(1)
        print "OK"


    elif cmd == "del":
        try:
            (id,) = tuple(args)
        except Exception, e:
            usage()

        try:
            r = registry.get(id)
        except AnyMetaRegistryException, e:
            print "Unknown id: " + id
            print
            sys.exit(1)

        registry.delete(id)
        registry.save()
        print "OK"

    else:
        usage()
