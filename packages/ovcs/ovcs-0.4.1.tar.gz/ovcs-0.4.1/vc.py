import os
import os.path as osp
from ovcs.util import cut_prefix

class NotARepository(Exception): pass

class Repository(object):
    kind = 'abstract'

    def __init__(self, path):
        self.workingpath = osp.realpath(path)
        root = self.compute_root_path()
        if root is None:
            raise NotARepository('%s is not a valid %s repository' % (path, self.kind))
        self.rootpath = root

    @classmethod
    def frompath(cls, path):
        try:
            return SVNRepository(path)
        except: # NotARepository:
            try:
                return HGRepository(path)
            except: # NotARepository, well d'uh
                return None

    def compute_root_path(self):
        raise NotImplementedError

    def add_or_update(self, package, tags):
        """ensures version control of a full odf package,
        providing a tag key:value
        """
        raise NotImplementedError

    def commit(self):
        """commits every pending modification
        XXX a more subtle commit might be needed
        """
        raise NotImplementedError

    def remove(self, files):
        raise NotImplementedError

    def set_tag(self, package_path, key, value):
        tagcontainerpath = osp.join(self.workingpath, package_path, '.tags')
        if not osp.exists(tagcontainerpath):
            os.mkdir(tagcontainerpath)
        tagpath = osp.join(tagcontainerpath, key)
        tagfile = open(tagpath, 'w')
        tagfile.write(value)
        tagfile.close()

try:
    from pysvn import Client, ClientError

    class SVNRepository(Repository):
        kind = 'subversion'

        def __init__(self, path):
            super(SVNRepository, self).__init__(path)

        def compute_root_path(self):
            """
            the root is the topmost directory containing
            an .svn entry
            """
            self.repo = repo = Client()
            path = self.workingpath
            root = None
            while True:
                svnpath = osp.join(path, '.svn')
                if osp.exists(svnpath) and osp.isdir(svnpath): # good enough ?
                    root = path
                path, leaf = osp.split(path)
                if not leaf:
                    return root

        def _make_working_path_a_working_copy(self):
            path_to_add = cut_prefix(self.workingpath, self.rootpath).split(os.sep)
            path = self.rootpath
            for pathelt in path_to_add:
                path = osp.join(path, pathelt)
                self.repo.add(path, recurse=False)

        def _unversioned(self, path=None):
            """
            return absolute unversioned paths
            for the working path
            """
            try:
                self.repo.status(self.workingpath)
            except ClientError, ce:
                if 'not a working copy' not in ce.args[0]:
                    raise
                self._make_working_path_a_working_copy()
            return [elt.path for elt in self.repo.status(self.workingpath)
                    if not elt.is_versioned]

        def add_or_update(self, package, tags={}):#tagkey, tagvalue):
            path = package.path
            assert self.workingpath in path, 'odf package %s is not located in %s' % (path, self.path)
            for tkey, tvalue in tags.items():
                self.set_tag(path, tkey, tvalue)
            unversioned = self._unversioned()
            for path in unversioned:
                self.repo.add(path)
            return unversioned

        def commit(self, text=''):
            assert isinstance(text, basestring)
            self.repo.checkin([self.rootpath], text)

        def remove(self, files):
            for file in files:
                self.repo.remove(file)

except ImportError:
    print 'pysvn extension appears to be missing; we can\'t deal with subversion repositories without it'
    class SVNRepository(object):

        def __init__(self, path):
            raise NotARepository


class match_wrapper(object):
    __slots__ = ('matchfn', 'files')
    def __init__(self, fun, files=lambda : ()):
        self.matchfn = fun
        self.files = files

try:
    from mercurial import hg, ui, repo, commands as cmd

    class HGRepository(Repository):
        kind = 'mercurial'

        def compute_root_path(self):
            path = self.workingpath
            while True:
                try:
                    self.repo = hg.repository(ui.ui(), path)
                except repo.RepoError, re:
                    if 'not found' not in re.args[0]:
                        raise
                else:
                    return path
                path, leaf = osp.split(path)
                if not leaf:
                    return None

        def _unversioned(self, path=None):
            """
            return unversioned paths
            for the working path
            relative to the root path
            """
            if path is None:
                path = self.workingpath
            def fname_matcher(fname):
                return fname.startswith(path)
            m, a, r, d, unknown, i, c = self.repo.status(match=match_wrapper(fname_matcher))
            return unknown

        def add_or_update(self, package, tags={}):#tagkey, tagvalue):
            path = package.path
            assert self.workingpath in path, 'odf package %s is not located in %s' % (path, self.workingpath)
            for tkey, tvalue in tags.items():
                self.set_tag(path, tkey, tvalue)
            relative_package_path = cut_prefix(path, self.rootpath)
            unversioned = self._unversioned(relative_package_path)
            self.repo.add(unversioned)
            return unversioned

        def commit(self, text=''):
            self.repo.commit(text)

        def remove(self, files):
            self.repo.remove([cut_prefix(file, self.rootpath) for file in files],
                             unlink=True)

except ImportError:
    print 'mercurial extension appears to be missing; we can\'t deal with mercurial repositories without it'
    class HGRepository(Repository):

        def __init__(self, path):
            raise NotARepository
