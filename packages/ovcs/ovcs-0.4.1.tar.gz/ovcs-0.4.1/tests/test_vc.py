import os, os.path as osp
from tempfile import mkdtemp
from atexit import register
from unittest import TestCase, main
from ovcs.package import ODFPackage
from ovcs.vc import Repository
from ovcs.tests.helper import fullpath, cleanup, shutdown

CLEANUP = set()
register(shutdown, CLEANUP)

class TestVC(TestCase):

    def regpath(self, basepath):
        path = fullpath(basepath)
        self.CLEANUP.add(path)
        return path

    def setUp(self):
        self.CLEANUP = set()
        self.REPOPATH = self.regpath(mkdtemp())
        self.SVNSRVPATH = osp.join(self.REPOPATH, 'svnrepo')
        self.SVNCLIPATH = osp.join(self.REPOPATH, 'svnclirepo')
        self.HGPATH = osp.join(self.REPOPATH, 'hgrepo')
        self.svn_available = self.setup_svn()
        self.hg_available = self.setup_hg()

    def tearDown(self):
        import shutil
        cleanup(self.CLEANUP, CLEANUP)

    def setup_svn(self):
        try:
            from subprocess import call
            call(['svnadmin', 'create', self.SVNSRVPATH])
            from pysvn import Client
            svn = Client()
            svn.checkout('file://%s' % self.SVNSRVPATH, self.SVNCLIPATH)
            asubrepopath = osp.join(self.SVNCLIPATH, 'foo', 'bar')
            os.makedirs(asubrepopath)
            return True
        except (ImportError, OSError):
            return False

    def setup_hg(self):
        try:
            from mercurial import hg, ui
            hg.repository(ui.ui(), self.HGPATH, create=1)
            asubrepopath = osp.join(self.HGPATH, 'foo', 'bar')
            os.makedirs(asubrepopath)
            return True
        except ImportError:
            return False

    def checktags(self, package):
        assert osp.exists(package.path)
        assert osp.exists(osp.join(package.path, '.tags'))
        assert osp.exists(osp.join(package.path, '.tags', 'mimetype'))
        assert open(osp.join(package.path, '.tags', 'mimetype')).read() == \
            'application/vnd.oasis.opendocument.text'

    def checksubelements(self, package):
        for elt in package.subelements():
            assert '.tags' not in elt
            assert '.svn' not in elt

    def add_to_repos(self, subpath, name, overwrite=False):
        packages = []
        for repopath in (self.SVNCLIPATH, self.HGPATH):
            if not osp.exists(repopath):
                return
            asubrepopath = osp.join(repopath, subpath)
            package = ODFPackage.frompath(fullpath('%s.odt' % name))
            pvcstargetpath = osp.join(asubrepopath, name)
            packagevcs = package.unzipped(pvcstargetpath, overwrite=overwrite)
            repo = Repository.frompath(pvcstargetpath)
            assert repo is not None
            repo.add_or_update(packagevcs,
                               {'mimetype': 'application/vnd.oasis.opendocument.text'})
            packages.append(packagevcs)
            self.checksubelements(packagevcs)
            self.checktags(packagevcs)
            self.assertEquals(repo._unversioned(), [])
            repo.commit('%s commit msg' % repo.kind)
        ref = ODFPackage.frompath(fullpath('%s.odt' % name))
        for pack in packages:
            assert pack == ref

    def test_add_to_repo_top(self):
        self.add_to_repos('', 'empty')

    def test_add_to_some_repo_path(self):
        self.add_to_repos(osp.join('foo', 'bar'), 'empty')

    def test_update(self):
        hello = ODFPackage.frompath(fullpath('hello.odt'))
        for repo in (self.SVNCLIPATH, self.HGPATH):
            hellovcs = hello.unzipped(osp.join(repo, 'empty'), overwrite=True)
            assert hello == hellovcs
            repo = Repository.frompath(repo)
            repo.add_or_update(hellovcs,
                               {'mimetype': 'application/vnd.oasis.opendocument.text'})
            self.checksubelements(hellovcs)
            self.checktags(hellovcs)
            repo.commit('%s commit msg' % repo.kind)

    def test_update_removing(self):
        bogus = ODFPackage.frompath(fullpath('bogus.odt'))
        for repopath in (self.SVNCLIPATH, self.HGPATH):
            self.add_to_repos('', 'empty', overwrite=True)
            repo = Repository.frompath(repopath)
            repo.commit('%s commit msg' % repo.kind)
            if repo.kind == 'mercurial':
                assert repo.repo.status() == ([], [], [], [], [], [], []), repo.repo.status()
            bogusvcs = bogus.unzipped(osp.join(repopath, 'empty'), overwrite=True)
            self.assertEquals(bogus, bogusvcs)
            if repo.kind == 'mercurial':
                self.assertEquals(repo.repo.status(),
                                  ([], [], [], [], [], [], []))
            repo.add_or_update(bogusvcs,
                               {'mimetype': 'application/vnd.oasis.opendocument.text'})
            self.checksubelements(bogusvcs)
            self.checktags(bogusvcs)
            repo.commit('%s commit msg' % repo.kind)

if __name__ == '__main__':
    main()
