import unittest
from datetime import datetime

import mock

class TestProject(unittest.TestCase):

    @property
    def project_factory(self, *args, **kwargs):
        from wheeljack.builder import Project
        return Project

    @mock.patch('bzrlib.branch.Branch.open_containing')
    def test_is_updated(self, bzropen_containing):
        # The project can determine if a project has been updated.
        project = self.project_factory('url', 'update-test', '1', 'cmd',
                                       '/some/repo', 'bzr', False)
        # To demonstrate the functionality we can use the mocked bzrlib
        # objects.
        branch = mock.Mock()
        branch.last_revision.return_value = 'last-revision'
        bzropen_containing.return_value = (branch, None)
        self.assert_(project.is_updated())
        # The check returns a different value if bazaar returns the same value
        # for the revision info.
        branch.revno.return_value = 1
        self.failIf(project.is_updated())

    @mock.patch('bzrlib.branch.Branch.open_containing')
    def test_is_updated_error(self, bzropen_containing):
        # When the project encounters an error during it's status check it
        # should raise a build error.
        from bzrlib.errors import NotBranchError
        def error():
            raise NotBranchError, 'error'
        bzropen_containing.side_effect = error
        project = self.project_factory('url', 'update-test', '1', 'cmd',
                                       '/some/repo', 'bzr', False)
        from wheeljack.builder import BuildError
        self.assertRaises(BuildError, project.is_updated)

    @mock.patch('wheeljack.repositories.BzrRepository.__enter__')
    @mock.patch('wheeljack.repositories.BzrRepository.__exit__')
    @mock.patch('wheeljack.builder.Project.revision')
    @mock.patch('subprocess.Popen')
    def test_build(self, bzrexport_enter, bzrexport_exit, revision, Popen):
        # Projects know how to build themselves.
        project = self.project_factory('url', 'build-test', 'rev-info', 'cmd',
                                       '/some/repo', 'bzr', False)
        # The build system uses subprocess to do the actual work. It polls the
        # program to see when it is done.
        bzrexport_enter.return_value = '/some/tmp/dir'
        Popen().poll.return_value = 0
        Popen().stdout.read.return_value = ''
        reports = list(project.build())
        import subprocess
        self.assertEqual(Popen.call_args,
                         ((['cmd'],), {'stderr': subprocess.STDOUT,
                                       'stdout': subprocess.PIPE,
                                       'cwd': '/some/tmp/dir',
                                       'env': None}))
        # The build returns the output from the process (if there was any).
        self.assertEqual(reports[0].output, '')

    @mock.patch('wheeljack.repositories.BzrRepository.__enter__')
    @mock.patch('wheeljack.repositories.BzrRepository.__exit__')
    @mock.patch('wheeljack.builder.Project.revision')
    @mock.patch('subprocess.Popen')
    def test_successful_build(self, bzrexport_enter, bzrexport_exit, revision, Popen):
        # A successful state is set in the build report when the build program
        # executes without problems.
        project = self.project_factory('url', 'build-test', 'rev-info', 'cmd',
                                       '/some/repo', 'bzr', False)
        bzrexport_enter.return_value = '/some/tmp/dir'
        Popen().poll.return_value = 0
        Popen().stdout.read.return_value = ''
        Popen().returncode = 0
        reports = list(project.build())
        self.assertEqual(reports[0].state, 'SUCCESS')

    @mock.patch('wheeljack.repositories.BzrRepository.__enter__')
    @mock.patch('wheeljack.repositories.BzrRepository.__exit__')
    @mock.patch('subprocess.Popen')
    @mock.patch('os.kill')
    def test_build_hang_detection(self,  bzrexport_enter, bzrexport_exit,
                                  Popen, kill):
        # A build could potentially have a problem that would hang the
        # builder. To overcome this the builder tries to detect these kind of
        # situations.
        bzrexport_enter.return_value = '/some/tmp/dir'
        bzrexport_exit.return_value = False # Avoid exception swallowing.

        project = self.project_factory('url', 'build-test', 'rev-info', 'cmd',
                                       '/some/repo', 'bzr', False)
        # We will make it look like the stdout pipe never changes.
        Popen().stdout.fileno.return_value = 1
        # A None value form a poll call means the process is still running.
        Popen().poll.return_value = None
        # Before we build the project we need to set a reasonable build
        # timeout.
        from wheeljack import builder
        builder.build_timeout = 0.001
        # Building the project will raise an exception.
        from wheeljack.builder import BuildError
        self.assertRaises(BuildError, lambda: list(project.build()))
        # The process should have been killed by the builder.
        import signal
        self.assertEqual(kill.call_args[0][1], signal.SIGKILL)

    @mock.patch('wheeljack.repositories.BzrRepository.__enter__')
    @mock.patch('wheeljack.repositories.BzrRepository.__exit__')
    @mock.patch('subprocess.Popen')
    def test_build_subprocess_error(self, bzrexport_enter, bzrexport_exit,
                                    Popen):
        # Calling programs which do not exist should be converted into build
        # errors.
        bzrexport_enter.return_value = '/some/tmp/dir'
        bzrexport_exit.return_value = False # Avoid exception swallowing.	
        def trigger_error():
            raise OSError
        Popen.side_effect = trigger_error
        project = self.project_factory('url', 'build-test', 'rev-info', 'cmd',
                                       '/some/repo', 'bzr', False)
        # The OSError will be converted into a BuildError for better reporting.
        from wheeljack.builder import BuildError
        self.assertRaises(BuildError, lambda: list(project.build()))

    @mock.patch('wheeljack.repositories.BzrRepository.__enter__')
    @mock.patch('wheeljack.repositories.BzrRepository.__exit__')
    @mock.patch('subprocess.Popen')
    @mock.patch('wheeljack.builder.Project.revision')
    def test_output_capture(self, bzrexport_enter, bzrexport_exit,
                            Popen, revision):
        # The builder captures the output from the subprocess. It does this by
        # reading bytes from the output stream.
        popen = Popen()

        bzrexport_enter.return_value = '/some/tmp/dir'
        bzrexport_exit.return_value = False # Avoid exception swallowing.	
        revision.return_value = '1'

        popen.poll.return_value = True
        popen.stdout.read.return_value = 'x'

        project = self.project_factory('url', 'build-test', 'rev-info', 'cmd',
                                       '/some/repo', 'bzr', False)
        self.assertEqual(list(project.build())[0].output, 'x')

    @mock.patch('wheeljack.repositories.BzrRepository.__enter__')
    @mock.patch('wheeljack.repositories.BzrRepository.__exit__')
    @mock.patch('subprocess.Popen')
    @mock.patch('wheeljack.builder.Project.revision')
    @mock.patch('select.select')
    def test_output_capture_during_build(
        self, bzrexport_enter, bzrexport_exit, Popen, revision, select):
        # During the build the builder will collect the output.
        class FakePoll:
            def __init__(self, counter):
                self.counter = counter
            def __call__(self):
                self.counter -= 1
                if self.counter == 0:
                    return False

        bzrexport_enter.return_value = '/some/tmp/dir'
        bzrexport_exit.return_value = False # Avoid exception swallowing.	
        revision.return_value = '1'

        popen = Popen()
        popen.poll = FakePoll(3)
        stdout = mock.Mock()
        stdout.read.return_value = 'x'
        popen.stdout.read.return_value = 'o'
        select.return_value = [[stdout], None, None] 
        # Create the project with some dummy variables
        project = self.project_factory('url', 'build-test', 'rev-info', 'cmd',
                                       '/some/repo', 'bzr', False)
        # The output clearly indicates two reads of x (during the time the
        # process was supposed to be alive according to the fake poll). It also
        # has the final o which indicates that it read any remaining data after
        # the process terminated.
        self.assertEqual(list(project.build())[0].output, 'xxo')

    @mock.patch('wheeljack.repositories.BzrRepository.__enter__')
    @mock.patch('wheeljack.repositories.BzrRepository.__exit__')
    @mock.patch('subprocess.Popen')
    @mock.patch('wheeljack.builder.Project.revision')
    @mock.patch('select.select')
    def test_build_sends_updates(self, bzrexport_enter, bzrexport_exit,
                                 Popen, revision, select):
        # During a build the server will be frequently informed of the
        # progress.
        bzrexport_enter.return_value = '/some/tmp/dir'
        bzrexport_exit.return_value = False # Avoid exception swallowing.
        class FakePoll:
            def __init__(self, counter):
                self.counter = counter
            def __call__(self):
                self.counter -= 1
                if self.counter == 0:
                    return False
        popen = Popen()
        popen.poll = FakePoll(3)
        popen.stdout.read.return_value = 'last line\n'

        stdout = mock.Mock()
        stdout.read.return_value = 'output\n'
        select.return_value = [[stdout], None, None] 

        project = self.project_factory('url', 'build-test', 'rev-info',
                                       'cmd', '/some/repo', 'bzr', False)
        self.assertEqual(len(list(project.build())), 3)
        

class TestServer(unittest.TestCase):

    @mock.patch('httplib2.Http')
    def test_load_projects(self, Http):
        # The project loader calls the server and retrieves the JSON
        # data. Let's create some sample JSON.
        response = mock.Mock()
        response.status = 200
        Http().request.return_value = (response, '{"projects": []}')
        from wheeljack.builder import Server
        server = Server('http://cybertron/api/', 'ultra', 'magnus')
        self.assertEqual(list(server.load_projects()), [])
        # When there is data we should get an iterable of project's.
        def request(url, headers):
            if url.endswith('/api/'):
                return (
                    response,
                    '{"projects": [{"href": "pass", "name": "Autobot City"}]}')
            return (response,
                    '{"url": "url", "name": "Autobot City", "last_revision": "", "build_cmd": "", "repository": "/some/repo", "vcs": "bzr", "require_build": false}')
        Http().request = request
        projects = list(server.load_projects())
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, 'Autobot City')

    @mock.patch('httplib2.Http')
    @mock.patch('wheeljack.builder.log.error')
    def test_load_projects_http_problem(self, Http, log_error):
        # The code will log an error if there is a problem trying to load the
        # projects.
        response = mock.Mock()
        response.status = 500
        Http().request.return_value = (response, 'Error info')
        from wheeljack.builder import Server
        server = Server('http://cybertron/api/', 'ultra', 'magnus')
        # Loading the projects will give us no error but just an empty list.
        self.assertEqual(list(server.load_projects()), [])
        # The code has triggered a log message.
        self.assertEqual(
            log_error.call_args,
            (('Error connecting to the server: %s', 'Error info'), {}))

    @mock.patch('httplib2.Http.request')
    def test_submit_build_report(self, request):
        # The server class can submit reports about the build to the server. We
        # need a fake report and project to send to the server.
        class Report(object):
            def __init__(self, project, revision, start, end, output):
                self.project = project
                self.revision = revision
                self.start = start
                self.end = end
                self.output = output
                self.state = 'FAILURE'

            def to_json(self):
                return 'JSON'

        class Project(object):
            url = 'http://some/project'

        response = mock.Mock()
        response.status = 200
        request.return_value = (response, '{"url": ""}')

        from wheeljack.builder import Server
        server = Server('http://cybertron/api/', 'ultra', 'magnus')
        server.submit_build_report(Report(Project(), '1',
                                          datetime(1984, 9, 17),
                                          datetime(1987, 11, 11),
                                          'build output'))
        self.assertEqual(
            request.call_args,
            (('http://some/project',),
             {'body': 'JSON', 'method': 'POST',
              'headers': {'authorization': 'basic dWx0cmE6bWFnbnVz'}}))


    @mock.patch('wheeljack.builder.log.info')
    @mock.patch('wheeljack.builder.Server.submit_build_report')
    def test_handle_build_error(self, log_info, submit_build_report):
        # Build errors resulting from the build should be converted to a
        # report.
        project = mock.Mock()
        project.is_updated.return_value = True
        from wheeljack.builder import BuildError
        def raise_build_error():
            raise BuildError('cmd', 'rev', 'start', 'output')
        project.build.side_effect = raise_build_error

        from wheeljack.builder import Server
        server = Server('url', 'user', 'pass')
        server.build(project)

        # The build report should report an unsuccessful build.
        buildlog_update = submit_build_report().update
        self.assertEqual(buildlog_update.call_args[0][0].state,
                         'FAILURE')
        self.assertEqual(buildlog_update.call_args[0][0].output,
                         'output')

    @mock.patch('wheeljack.builder.log.info')
    @mock.patch('wheeljack.builder.Server.submit_build_report')
    def test_build_error_with_forced_build(self, log_info, 
                                           submit_build_report):
        # Build errors resulting from the build should be converted to a
        # report.
        project = mock.Mock()
        project.require_build = True
        from wheeljack.builder import BuildError
        def raise_build_error():
            raise BuildError('cmd', 'rev', 'start', 'output')
        project.is_updated.side_effect = raise_build_error

        from wheeljack.builder import Server
        server = Server('url', 'user', 'pass')
        server.build(project)

        # The build report should report an unsuccessful build.
        self.assertEqual(submit_build_report.call_args[0][0].state,
                         'FAILURE')

    @mock.patch('wheeljack.builder.log.info')
    def test_no_build_of_up_to_date_project(self, log_info):
        # Project's without any modifications should not be build.
        from wheeljack.builder import Server
        server = Server('url', 'user', 'pass')
        project = mock.Mock()
        project.require_build = False
        project.is_updated.return_value = False
        # A non build is indicated by a None return value.
        self.assert_(server.build(project) is None)

    @mock.patch('wheeljack.builder.Server.submit_build_report')
    def test_error_on_up_to_date_check(self, submit_build_report):
        # A build error report is submitted when a error is detected during the
        # up-to-date check of the project (because of version control system
        # errors).
        project = mock.Mock()
        project.require_build = False
        from wheeljack.builder import BuildError
        def raise_build_error():
            raise BuildError('cmd', 'rev', 'start', 'output')
        project.is_updated.side_effect = raise_build_error
        from wheeljack.builder import Server
        server = Server('url', 'user', 'pass')
        # The build state should indicate an unsuccessful build.
        self.assert_(server.build(project) is False)
        # A build report should have been submitted as well.
        self.assert_(submit_build_report.called)

    @mock.patch('wheeljack.builder.Server.submit_build_report')
    def test_submit_reports_during_build(self, submit_build_report):
        # When reports become available during a build they are submitted to
        # the server.
        project = mock.Mock()
        # The build method normally returns an iterator, a list will do for our
        # test.
        project.build.return_value = [None, None]
        from wheeljack.builder import Server
        server = Server('url', 'user', 'pass')
        server.build(project)
        # The buildlog should be updated twice.
        buildlog_update = submit_build_report().update
        self.assertEqual(len(buildlog_update.call_args_list), 2)

    @mock.patch('wheeljack.builder.Server.submit_build_report')
    def test_return_build_success(self, submit_build_report):
        # Successful builds should indicate this by returning True.
        project = mock.Mock()
        # The build method normally returns an iterator, a list will do for our
        # test.
        report = mock.Mock()
        report.state = 'SUCCESS'
        project.build.return_value = [report]
        from wheeljack.builder import Server
        server = Server('url', 'user', 'pass')
        self.assert_(server.build(project))


class TestBuildError(unittest.TestCase):

    def test_str(self):
        # The exception knows how to generate an informative message.
        from wheeljack.builder import BuildError
        self.assertEqual(
            str(BuildError('cmd', 'rev', None, 'output')),
            'Command: cmd failed. Output from executiion:\n\noutput')


class TestBuildProjects(unittest.TestCase):

    @mock.patch('wheeljack.builder.log.info')
    def test_build_updated_projects(self, log_info):
        # The builder will build all the projects that have changes.
        server = mock.Mock()
        project = mock.Mock()
        project.is_updated.return_value = True
        project.build.return_value = []
        server.load_projects.return_value = [project]

        from wheeljack.builder import build_projects
        build_projects(server)

        self.assert_(server.build.called)
        server.build.assert_called_with(project)

    @mock.patch('wheeljack.builder.log.info')
    def test_no_updates(self, log_info):
        # When a project has no updates the build will be skipped.
        server = mock.Mock()
        project = mock.Mock()
        project.is_updated.return_value = False
        project.require_build = False
        server.load_projects.return_value = [project]

        from wheeljack.builder import build_projects
        build_projects(server)

        self.failIf(project.build.called)

    def test_socket_error(self):
        # The function should just return without complaints when the server
        # cannot be reached.
        from wheeljack.builder import build_projects
        import socket
        server = mock.Mock()
        def load():
            raise socket.error
        server.load_projects = load
        build_projects(server)

    def test_unsuccessful_project(self):
        # When projects fail to build it should be logged.
        import logging
        log = logging.getLogger('Wheeljack')
        log.error = mock.Mock()

        server = mock.Mock()
        project = mock.Mock()
        server.load_projects.return_value = [project]
        server.build.return_value = False
        from wheeljack.builder import build_projects
        build_projects(server)

        self.assert_(log.error.called)

class TestReport(unittest.TestCase):

    def test_to_json(self):
        # Reports know how to convert themselves to JSON.
        from wheeljack.builder import Report
        report = Report(None, 'rev', datetime(2009, 1, 4), datetime(2009, 1, 5))
        self.assertEqual(
            report.to_json(),
            '{"start": "2009-01-04T00:00:00", "state": "FAILURE", "revision":'
            ' "rev", "end": "2009-01-05T00:00:00", "output": ""}')

class TestBuildLog(unittest.TestCase):

    def test_update(self):
        # The build log can update the log entry on the server.
        from wheeljack.builder import BuildLog
        server = mock.Mock()
        report = mock.Mock()
        report.to_json.return_value = 'JSON'
        log = BuildLog(server, None)
        log.update(report)
        server.request.assert_called_with(None, method='PUT', body='JSON')

def test_suite():
    return unittest.TestSuite([
            unittest.makeSuite(TestProject),
            unittest.makeSuite(TestServer),
            unittest.makeSuite(TestBuildError),
            unittest.makeSuite(TestBuildProjects),
            unittest.makeSuite(TestReport),
            unittest.makeSuite(TestBuildLog),
     ])
