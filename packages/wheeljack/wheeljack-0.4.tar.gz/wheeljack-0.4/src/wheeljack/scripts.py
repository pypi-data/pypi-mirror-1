from optparse import OptionParser
import sys
import os
import logging
import logging.handlers
import time

from wheeljack.builder import Server
from wheeljack.builder import build_projects

log = logging.getLogger('Wheeljack')
sth = logging.StreamHandler()
sth.setFormatter(logging.Formatter(
        "[%(asctime)s] - %(message)s", "%x %X"))
log.addHandler(sth)
log.setLevel(logging.DEBUG)

def use_settings(option, opt_str, value, parser):
    # Setup the environment so that Django can load the settings.
    os.environ['DJANGO_SETTINGS_MODULE'] = value
    from django.conf import settings
    username  = settings.BUILDER_USER
    password  = settings.BUILDER_PASSWORD
    parser.values.username = settings.BUILDER_USER
    parser.values.password = settings.BUILDER_PASSWORD

def show_help(parser):
    parser.print_help()
    sys.exit(1)

def build_project(command):
    """This builds a single project based on command line arguments."""
    parser = OptionParser(
        usage=('usage: %prog ' + command + ' [username password] url\n'
               'User name and password are not required when a settings '
               'file is specified.'))
    parser.add_option(
        '--settings', action='callback', type='string',
        help="Python path to the settings file, example: 'autobot.settings'",
        callback=use_settings)
    options, args = parser.parse_args()

    # Get the username and password, either from a config file or from the
    # commandline args.
    if getattr(options, 'username', None) is not None:
        username  = options.username
        password  = options.password
        if len(args) != 1:
            show_help(parser)
        project = args[0]
    elif len(args) == 3:
        username, password, project = args
    else:
        show_help(parser)

    server = Server(None, username, password)
    print 'Starting build'
    ok = server.build(server.load_project(project))
    # Let the process calling us know we failed.
    if not ok:
        log.error('Project failed to build')
        sys.exit(1)

def continuous_build(command):
    parser = OptionParser(
        usage='usage: %prog ' + command +' [options] username password')
    parser.add_option("-l", "--url", dest="url",
                       default='http://localhost:8000/api/',
                       help="The URL for the server API [default: %default]")
    parser.add_option(
        '--settings', action='callback', type='string',
        help="Python path to the settings file, example: 'autobot.settings'",
        callback=use_settings)
    parser.add_option(
        "-s", "--sleep", dest="sleep", metavar='MINUTES',
        default=60, type="int",
        help="Sleep the specified amount of time in between build runs.")

    options, args = parser.parse_args()

    if getattr(options, 'username', None) is not None:
        username  = options.username
        password  = options.password
    elif len(args) == 2:
        username, password = args
    else:
        show_help(parser)

    log.info('Starting builds')
    server = Server(options.url, username, password)

    if command == 'continuous':
        while True:
            build_projects(server)
            time.sleep(options.sleep * 60) # Let the system relax for a bit
    else:
        build_projects(server)

commands = {
    'build': build_project,
    'continuous': continuous_build,
    'build-all': continuous_build,
}

def main():
    from bzrlib.plugin import load_plugins
    load_plugins()
    script = sys.argv[0]
    if len(sys.argv) < 2:
        print 'Usage %s subcommand [options] [args]:' % script
        print ''
        print "Type '%s subcommand --help' for help on a specific subcommand" % script
        print 'Available subcommands:'
        for command in sorted(commands):
            print '  ', command
        sys.exit(1)
    command = sys.argv.pop(1)
    try:
        handler = commands[command]
    except KeyError:
        print "Unknown command: '%s'" % command
        print "Type '%s' for usage" % script
        sys.exit(1)
    handler(command)

if __name__ == '__main__':
    main()
