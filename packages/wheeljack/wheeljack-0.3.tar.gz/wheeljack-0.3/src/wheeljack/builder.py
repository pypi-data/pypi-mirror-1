from __future__ import with_statement
with_statement # Code checker

import base64
import time
import sys
import subprocess
import select
import signal
import os
import socket
from datetime import datetime
from optparse import OptionParser

import httplib2
import simplejson as json

from wheeljack.errors import BuildError
from wheeljack.errors import RepositoryError
from wheeljack.repositories import open_repository

build_timeout = 120 # The timeout for when a process can be considered to hang
timeout_message = '''
Build terminated by Wheeljack, reason: TIMEOUT EXCEEDED. 

The build took more than %s seconds without printing to stdout or
stderr. Wheeljack assumes this means that process is stuck and terminates it.

Process output:
===============
''' % build_timeout

command_error_message = '''
Build terminated abnormally. The build command failed:

%s
'''

repository_error_message = '''
Error trying to interact with the source repository. Please make sure the
setting is correct. Error output:

%s
'''

def log_info(message, *args):
    print message % args

def log_error(message, *args):
    print >> sys.stderr, message % args


class Report(object):
    """Report's contain the information from a build process"""

    def __init__(self, project, revision, start, end=None, output=None,
                 state='FAILED'):
        self.project = project
        self.revision = revision
        self.start = start
        if end is None:
            end = datetime.now()
        self.end = end
        if output is None:
            output = ''
        self.output = output
        self.state = state

    def to_json(self):
        """Convert the report to JSON."""
        data = {'start': self.start.isoformat(),
                'end': self.end.isoformat(),
                'output': self.output,
                'revision': self.revision,
                'state': self.state}
        return json.dumps(data)


class Project(object):
    """A project encapsulates the build requirements for a specific project.

    Project's are able to check the state of the version control system to
    indicate if they need to be built. The can also start a build process.
    """

    def __init__(self, url, name, last_revision, build_cmd, repository, vcs,
                 require_build):
        self.url = url
        self.name = name
        self.last_revision = last_revision
        self.build_cmd = build_cmd
        self.repository = repository
        self.vcs = vcs
        self.require_build = require_build

    def revision(self):
        """Return the current revision of this project."""
        try:
            return open_repository(self.repository, self.vcs).revision()
        except RepositoryError, e:
            raise BuildError(
                self.build_cmd, 'checkout-problem',
                datetime.now(), repository_error_message % str(e.msg))

    def is_updated(self):
        """Check if the project has been updated since the last build."""
        return self.last_revision != self.revision()

    def build(self, env=None):
        """Build the project.

        This returns the output from the execution as a string in case of
        success. Problems with the build are raised as a `BuildError`.
        """
        start = datetime.now()
        export = open_repository(self.repository, self.vcs)

        last_update_time = datetime.now()

        with export as build_dir:
            try:
                process = subprocess.Popen(self.build_cmd.split(' '),
                                           cwd=build_dir,
                                           env=env,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)
            except OSError, e:
                raise BuildError(self.build_cmd, self.revision(), start,
                                 command_error_message % e.strerror)
            # Build the project in a way that it won't hang the builder in case
            # of problems.
            output = []
            while process.poll() is None:
                r, w, x = select.select([process.stdout], [], [],
                                        build_timeout)
                if len(r) == 0: # The timeout was triggered
                    os.kill(process.pid, signal.SIGKILL)
                    raise BuildError(self.build_cmd, self.revision(), start,
                                     timeout_message + ''.join(output))
                else:
                    output.append(r[0].read(1))

                now = datetime.now()
                interval = now - last_update_time
                if interval.seconds > 1:
                    last_update_time = now
                    yield Report(self, self.revision(), start,
                                 datetime.now(), ''.join(output),
                                 state='BUILDING')

            output.append(process.stdout.read())

        if process.returncode==0:
            state = 'OK'
        else:
            state = 'FAILED'

        yield Report(
            self, self.revision(), start, datetime.now(), ''.join(output),
            state=state)
        return

class BuildLog(object):

    def __init__(self, server, url):
        self.server = server
        self.url = url

    def update(self, report):
        """ Update the build report."""
        self.server.request(self.url, method='PUT', body=report.to_json())


class Server(object):

    def __init__(self, url, user, passwd):
        self.url = url
        self.user = user
        self.passwd = passwd

    def request(self, url, **kwargs):
        """Do a HTTP request against the server.

        This returns a tuple of response and content."""
        auth = 'basic %s' % (base64.b64encode('%s:%s' % (self.user,
                                                         self.passwd)))
        http = httplib2.Http()
        return http.request(url, headers={'authorization': auth}, **kwargs)

    def load_projects(self):
        """Return an iterable of project objects."""
        response, content = self.request(self.url)
        if response.status != 200:
            log_error('Error connecting to the server: %s', content)
            return []

        projects = []
        for project in json.loads(content)['projects']:
            r, c = self.request(project['href'])
            projects.append(
                Project(**dict([(str(key), value) for (key, value) in
                                json.loads(c).iteritems()])))
        return projects

    def submit_build_report(self, report):
        """Submit the build report to the server."""
        response, content = self.request(report.project.url, method='POST',
                                         body=report.to_json())
        assert response.status == 200
        return BuildLog(self, json.loads(content)['url'])


def build_projects(server):
    try:
        projects = server.load_projects()
    except socket.error, e:
        log_error('Error connecting to the server: %s', e)
        return
    for project in projects:
        log_info('Building project: %s', project.name)
        log_info('\tChecking version: %s', project.repository)

        try:
            if not (project.require_build or project.is_updated()):
                log_info('\tProject is up-to-date, skipping build')
                continue
        except BuildError, e:
            server.submit_build_report(
                Report(project, e.revision, e.start,
                       datetime.now(), e.output))
        log_info('\tStarting build for project')
        # Create a log entry which we can update
        buildlog = server.submit_build_report(
            Report(project, project.revision(), datetime.now(),
                   state='BUILDING'))
        try:
            for report in project.build():
                buildlog.update(report)
        except BuildError, e:
            report = Report(project, e.revision, e.start,
                            datetime.now(), e.output)
            buildlog.update(report)


def main():
    from bzrlib.plugin import load_plugins
    load_plugins()

    parser = OptionParser(usage='usage: %prog [options] username password')
    parser.add_option("-l", "--url", dest="url",
                       default='http://localhost:8000/api/',
                       help="The URL for the server API [default: %default]")
    parser.add_option(
        "-c", "--continuous",
        action="store_true", dest="continuous", default=False,
        help="After building all projects pause and then run again.")
    parser.add_option(
        "-s", "--sleep", dest="sleep", metavar='MINUTES',
        default=60, type="int",
        help="Sleep the specified amount of time in between build runs.")

    options, args = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        sys.exit(1)

    log_info('Starting builds')
    server = Server(options.url, *args)

    if options.continuous:
        while True:
            build_projects(server)
            time.sleep(options.sleep * 60) # Let the system relax for a bit
    else:
        build_projects(server)


if __name__ == '__main__':
    main()
