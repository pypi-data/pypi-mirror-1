import unittest

import mock


class TestBzrRepository(unittest.TestCase):

    @property
    def repository(self):
        from wheeljack.repositories import BzrRepository
        return BzrRepository

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('bzrlib.branch.Branch.open_containing')
    @mock.patch('bzrlib.export.export')
    def test_enter(self, mkdtemp, open_containing, export):
        # The bzr export repository creates a temp directory on enter.
        mkdtemp.return_value = '/some/tmp'
        repository = self.repository('/some/repo')
        open_containing.return_value = (mock.Mock(), None)
        self.assertEqual(repository.__enter__(), '/some/tmp/build')
        # It also tried to create an export
        self.assertEqual(open_containing.call_args, (('/some/repo',), {}))
        self.assertEqual(export.call_args[0][1], '/some/tmp/build')

    @mock.patch('shutil.rmtree')
    def test_exit(self, rmtree):
        # When the __exit__ method is called the repository will clean up the
        # export directory.
        repository = self.repository('/some/repo')
        # This is normally done by the __enter__ method.
        repository.build_container = '/tmp'
        repository.__exit__(None, None, None)
        self.assertEqual(rmtree.call_args, (('/tmp',), {}))


    @mock.patch('bzrlib.branch.Branch.open_containing')
    def test_revision(self, open_containing):
        # The repository can get the current revision.
        branch = mock.Mock()
        branch.revno.return_value = 1
        open_containing.return_value = (branch, '')
        repository = self.repository('/some/repo')
        self.assertEqual(repository.revision(), '1')

    @mock.patch('bzrlib.branch.Branch.open_containing')
    def test_revision_error(self, open_containing):
        # The repository can get the current revision. In case there is an
        # error it will raise a repository error.
        from bzrlib.errors import BzrError
        def raise_error():
            raise BzrError(msg='Some bzr error message')
        open_containing.side_effect = raise_error
        repository = self.repository('/some/repo')
        from wheeljack.errors import RepositoryError
        self.assertRaises(RepositoryError, repository.revision)


class TestSvnRepository(unittest.TestCase):

    @property
    def repository(self):
        from wheeljack.repositories import SvnRepository
        return SvnRepository

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('subprocess.Popen')
    def test_enter(self, mkdtemp, Popen):
        # The svn export repository creates a temp directory on enter.
        mkdtemp.return_value = '/some/tmp'
        repository = self.repository('/some/repo')
        Popen().wait.return_value = 0
        self.assertEqual(repository.__enter__(), '/some/tmp/build')
        # It also tried to create an export
        Popen.assert_called_with(
            ['/usr/bin/svn', 'export', '/some/repo', '/some/tmp/build'],
            stderr=-2, stdout=-1)

    @mock.patch('shutil.rmtree')
    def test_exit(self, rmtree):
        # When the __exit__ method is called the repository will clean up the
        # export directory.
        repository = self.repository('/some/repo')
        # This is normally done by the __enter__ method.
        repository.build_container = '/tmp'
        repository.__exit__(None, None, None)
        self.assertEqual(rmtree.call_args, (('/tmp',), {}))


    @mock.patch('subprocess.Popen')
    def test_revision(self, Popen):
        # The repository can get the current revision.
        Popen().wait.return_value = 0
        Popen().stdout.read.return_value = '''
<?xml version="1.0"?>
<info>
<entry kind="dir" path="svn" revision="20013">
<url>https://zopedev.pareto.nl/svn</url>
<repository>
<root>http://cybertron/svn</root>
<uuid>bd7150c687c8</uuid>
</repository>
<commit
   revision="20013">
<author>Wheeljack</author>
<date>2008-12-28T22:50:09.351953Z</date>
</commit>
</entry>
</info>
'''.strip()
        repository = self.repository('/some/repo')
        self.assertEqual(repository.revision(), '20013')

    @mock.patch('subprocess.Popen')
    def test_revision_error(self, Popen):
        # The repository can get the current revision. In case there is an
        # error it will raise a repository error.
        Popen().wait.return_value = 0
        Popen().stdout.read.return_value = '''
<?xml version="1.0"?>
<info>
http://earth/svn:  (Not a valid URL)

</info>
'''.strip()
        repository = self.repository('/some/repo')
        from wheeljack.errors import RepositoryError
        self.assertRaises(RepositoryError, repository.revision)

    @mock.patch('subprocess.Popen')
    def test_svn_execution_error(self, Popen):
        # An error will be raised when the svn subprocess returns with a non
        # zero exit code error it will raise a repository error.
        Popen().wait.return_value = 1
        repository = self.repository('/some/repo')
        from wheeljack.errors import RepositoryError
        self.assertRaises(RepositoryError, repository.revision)


def test_suite():
    return unittest.TestSuite([
     unittest.makeSuite(TestBzrRepository),
     unittest.makeSuite(TestSvnRepository),
     ])
