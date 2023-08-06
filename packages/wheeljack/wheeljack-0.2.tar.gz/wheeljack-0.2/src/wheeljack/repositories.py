import os
import subprocess
import shutil
import tempfile
from xml.etree import ElementTree

import bzrlib.branch
import bzrlib.export

from wheeljack.errors import RepositoryError

_repositories = {}

def open_repository(uri, type):
    factory = _repositories[type][1]
    return factory(uri)

def register_repository(key, name, factory):
    _repositories[key] = (name, factory)

class RepositoryBase(object):
    """Base class for repository implementations."""

    def __init__(self, repository):
        self.repository = repository

    def __exit__(self, type, value, traceback):
        """Remove the export directory."""
        shutil.rmtree(self.build_container)

    def __enter__(self):
        """Needed to implement the context manager protocol."""
        raise NotImplementedError

class BzrRepository(RepositoryBase):
    """An wrapper around bzrlib to support bzr operatations.

    The wrapper can be used as a context manager to create a bzr export. This
    context manager creates an export and returns it's path from __enter__. The
    export is created within a temporary directory. Regardless of errors this
    directory is cleared upon __exit__.
    """

    def __enter__(self):
        """Return the path used for the export."""
        self.build_container = tempfile.mkdtemp()
        build_dir = os.path.join(self.build_container, 'build')

        branch, subdir = bzrlib.branch.Branch.open_containing(self.repository)
        tree = branch.basis_tree()
        bzrlib.export.export(tree, build_dir)
        return build_dir

    def revision(self):
        """Return the current revision."""
        try:
            branch, subdir = bzrlib.branch.Branch.open_containing(
                self.repository)
        except bzrlib.errors.BzrError, e:
            raise RepositoryError(str(e))
        return str(branch.revno())

register_repository('bzr', 'Bazaar', BzrRepository)


class SvnRepository(RepositoryBase):
    """An wrapper around svn to support svn operatations.

    The wrapper can be used as a context manager to create a svn export. This
    context manager creates an export and returns it's path from __enter__. The
    export is created within a temporary directory. Regardless of errors this
    directory is cleared upon __exit__.
    """

    def _svn(self, cmd, *args, **kwargs):
        """Execute Subversion."""
        cmd = ['/usr/bin/svn'] + cmd
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if process.wait() != 0:
            raise RepositoryError(process.stdout.read())
        return process

    def __enter__(self):
        """Return the path used for the export."""
        self.build_container = tempfile.mkdtemp()
        build_dir = os.path.join(self.build_container, 'build')
        self._svn(['export', self.repository, build_dir])
        return build_dir

    def revision(self):
        """Return the current revision."""
        process = self._svn(['info', self.repository, '--xml'])
        tree = ElementTree.fromstring(process.stdout.read())
        commit_node = tree.find('.//commit')
        if commit_node is None:
            raise RepositoryError(tree.text)
        return tree.find('.//commit').attrib['revision']

register_repository('svn', 'Subversion', SvnRepository)

supported_repositories = [(key, name) for key, (name, factory) in
                          _repositories.iteritems()]
