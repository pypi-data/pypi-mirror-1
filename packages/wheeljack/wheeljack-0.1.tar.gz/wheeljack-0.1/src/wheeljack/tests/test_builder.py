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
                                       '/some/repo')
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
                                       '/some/repo')
        from wheeljack.builder import BuildError
        self.assertRaises(BuildError, project.is_updated)

    @mock.patch('wheeljack.builder.BzrExport.__enter__')
    @mock.patch('wheeljack.builder.BzrExport.__exit__')
    @mock.patch('wheeljack.builder.Project.revision')
    @mock.patch('subprocess.Popen')
    def test_build(self, bzrexport_enter, bzrexport_exit, revision, Popen):
        # Projects know how to build themselves.
        project = self.project_factory('url', 'build-test', 'rev-info', 'cmd',
                                       '/some/repo')
        # The build system uses subprocess to do the actual work. It polls the
        # program to see when it is done.
        bzrexport_enter.return_value = '/some/tmp/dir'
        Popen().poll.return_value = 0
        Popen().stdout.read.return_value = ''
        report = project.build()
        import subprocess
        self.assertEqual(Popen.call_args,
                         ((['cmd'],), {'stderr': subprocess.STDOUT,
                                       'stdout': subprocess.PIPE,
                                       'cwd': '/some/tmp/dir',
                                       'env': None}))
        # The build returns the output from the process (if there was any).
        self.assertEqual(report.output, '')

    @mock.patch('wheeljack.builder.BzrExport.__enter__')
    @mock.patch('wheeljack.builder.BzrExport.__exit__')
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
                                       '/some/repo')
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
        self.assertRaises(BuildError, project.build)
        # The process should have been killed by the builder.
        import signal
        self.assertEqual(kill.call_args[0][1], signal.SIGKILL)

    @mock.patch('wheeljack.builder.BzrExport.__enter__')
    @mock.patch('wheeljack.builder.BzrExport.__exit__')
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
                                       '/some/repo')
        # The OSError will be converted into a BuildError for better reporting.
        from wheeljack.builder import BuildError
        self.assertRaises(BuildError, project.build)


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
                    '{"url": "url", "name": "Autobot City", "last_revision": "", "build_cmd": "", "repository": "/some/repo"}')
        Http().request = request
        projects = list(server.load_projects())
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, 'Autobot City')

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
                self.success = False

        class Project(object):
            url = 'http://some/project'

        from wheeljack.builder import Server
        server = Server('http://cybertron/api/', 'ultra', 'magnus')
        server.submit_build_report(Report(Project(), '1',
                                          datetime(1984, 9, 17),
                                          datetime(1987, 11, 11),
                                          'build output'))
        self.assertEqual(
            request.call_args,
            (('http://some/project',),
             {'body': '{"start": "1984-09-17T00:00:00", "revision": "1", "end": "1987-11-11T00:00:00", "success": false, "output": "build output"}', 'headers': {'authorization': 'basic dWx0cmE6bWFnbnVz'}, 'method': 'PUT'}))


class TestBzrExport(unittest.TestCase):

    @property
    def manager(self):
        from wheeljack.builder import BzrExport
        return BzrExport

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('bzrlib.branch.Branch.open_containing')
    @mock.patch('bzrlib.export.export')
    def test_enter(self, mkdtemp, open_containing, export):
        # The bzr export manager creates a temp directory on enter.
        mkdtemp.return_value = '/some/tmp'
        manager = self.manager('/some/repo')
        open_containing.return_value = (mock.Mock(), None)
        self.assertEqual(manager.__enter__(), '/some/tmp/build')
        # It also tried to create an export
        self.assertEqual(open_containing.call_args, (('/some/repo',), {}))
        self.assertEqual(export.call_args[0][1], '/some/tmp/build')

    @mock.patch('shutil.rmtree')
    def test_exit(self, rmtree):
        # When the __exit__ method is called the manager will clean up the
        # export directory.
        manager = self.manager('/some/repo')
        # This is normally done by the __enter__ method.
        manager.build_container = '/tmp'
        manager.__exit__(None, None, None)
        self.assertEqual(rmtree.call_args, (('/tmp',), {}))


def test_suite():
    return unittest.TestSuite([
     unittest.makeSuite(TestProject),
     unittest.makeSuite(TestServer),
     unittest.makeSuite(TestBzrExport),
     ])
