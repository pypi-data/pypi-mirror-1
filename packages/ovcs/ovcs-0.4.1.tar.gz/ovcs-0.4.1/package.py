from __future__ import with_statement
import sys
import os, os.path as osp
import zipfile
import shutil

from lxml import etree

from ovcs.util import normalize_xml, cut_prefix

class NotAnOdf(Exception): pass
class CorruptOdf(Exception): pass

class ODFPackage(object):
    """Provides minimal wrapper for an ODF package."""
    DIRS_BLACKLIST = frozenset(['.tags', '.svn'])
    MIN_FILES = set('content.xml meta.xml settings.xml styles.xml mimetype'.split())
    MIN_DIRS = set('META-INF Thumbnails'.split())

    @classmethod
    def frompath(cls, path, mode='r'):
        path = osp.realpath(path)
        if not osp.exists(path):
            raise ValueError('%s does not exist' % path)
        if osp.isdir(path):
            return UnzippedODFPackage(path, mode)
        else:
            return ZippedODFPackage(path, mode)

    @classmethod
    def fromstream(cls, stream):
        return StreamODFPackage(stream)

    def __init__(self, path, mode='r'):
        path = osp.realpath(path)
        if not osp.exists(path):
            raise ValueError('%s does not exist' % path)
        self.path = path

    def subelements(self):
        raise NotImplementedError

    def data(self, elt, default=None):
        raise NotImplementedError
    read = data

    def zipped(self, path):
        raise NotImplementedError

    def unzipped(self, path):
        raise NotImplementedError

    def is_zipped(self):
        return isinstance(self, ZippedODFPackage)

    def __eq__(self, other):
        if not isinstance(other, ODFPackage):
            return False
        subelts = set(self.subelements())
        if subelts != set(other.subelements()):
            return False
        for elt in subelts:
            if self.data(elt) != other.data(elt):
                return False
        return True

    def quickcheck(self):
        """a minimal integrity check:
        * some files and directories must be there
        * xml files must be valid
        """
        elts = set(self.subelements())
        fdiff = self.MIN_FILES - elts
        ddiff = self.MIN_DIRS - set(elt.split(osp.sep)[0] for elt in elts)
        if fdiff or ddiff:
            raise CorruptOdf("the package lacks : %s" % ', '.join(fdiff | ddiff))
        for elt in elts:
            if elt.endswith('.xml'):
                try:
                    self.data(elt)
                except etree.XMLSyntaxError, ex:
                    raise CorruptOdf("the file %s is not valid xml: %s" % (elt, ex))

    def diff(self, other):
        from difflib import unified_diff as udiff
        from mimetypes import guess_type
        chlist = self.changelist(other)
        out = []
        def w(*args):
            _args = ' '.join(args)
            out.append(_args)
        for cat, eltlist in chlist.items():
            if cat in ('added', 'deleted') and eltlist:
                for elt in eltlist:
                    w('%s : %s' % (cat.capitalize(),
                                   osp.join(osp.basename(self.path), elt)))
                continue
            for elt in eltlist:
                d1 = self.data(elt, default='').split('\n')
                d2 = other.data(elt, default='').split('\n')
                diff = list(udiff(d1, d2,
                                  osp.join(osp.basename(self.path), elt),
                                  osp.join(osp.basename(other.path), elt)))
                if diff:
                    w('Modified :', osp.join(osp.basename(self.path), elt))
                    dtype, encoding = guess_type(elt)
                    if dtype == 'application/xml':
                        w('\n'.join(elt.rstrip() for elt in diff))
                    else:
                        w('no visual diff for binary file of mime-type %s' % dtype)
        return out

    def changelist(self, other):
        assert isinstance(other, ODFPackage), 'diff is only computed against an odf package'
        out = {'added'   : [],
               'deleted' : [],
               'changed' : []}
        selfelts = set(self.subelements())
        otherelts = set(other.subelements())
        allelts =  sorted(selfelts | otherelts)
        for elt in allelts:
            if elt not in selfelts:
                out['added'].append(elt)
                continue
            if elt not in otherelts:
                out['deleted'].append(elt)
                continue
            d1 = self.data(elt, default='').split('\n')
            d2 = other.data(elt, default='').split('\n')
            if d1 != d2:
                out['changed'].append(elt)
        return out

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        #return '<%s (%s)>' % (self.__class__.__name__,
        #                      ', '.join(sorted(self.subelements())))
        return '<%s (%#x)>' % (self.__class__.__name__, id(self))

class UnzippedODFPackage(ODFPackage):
    """An svn-sensitive unzipped ODF package."""

    def __init__(self, path, mode='r'):
        super(UnzippedODFPackage, self).__init__(path, mode)
        if not osp.isdir(path):
            raise ValueError, "Not a directory: %s" % path
        self.mode = mode

    def subelements(self):
        for base, dirs, files in os.walk(self.path):
            for elt in self.DIRS_BLACKLIST:
                if elt in dirs:
                    dirs.remove(elt)
            for elt in files:
                elt_base = cut_prefix(base, self.path)
                yield osp.join(elt_base, elt)

    def data(self, elt, default=None):
        """get the data associated to an element
        the element must be present in self.subelements()
        if no default is provided"""
        elt_path = osp.join(self.path, elt)
        if not osp.exists(elt_path):
            if default is not None:
                return default
            raise ValueError('%s is not an existing element of %s' % (elt, self.path))
        if osp.isdir(elt_path):
            return ''
        data = open(elt_path, 'rb').read()
        if elt.endswith('.xml'):
            data = normalize_xml(data)
        return data

    def write(self, elt, bytestr):
        """write the data associated to an element
        the element must be present in self.subelements()
        """
        if self.mode == 'r':
            raise OSError('%s is open read-only' % self.path)
        elt_path = osp.join(self.path, elt)
        if osp.isdir(elt_path):
            raise TypeError('%s is a directory, not a file' % elt)
        with open(elt_path, 'wb') as out:
            out.write(bytestr)

    def remove(self, elt):
        """remove a file or a whole directory"""
        if self.mode == 'r':
            raise OSError('%s is open read-only' % self.path)
        elt_path = osp.join(self.path, elt)
        try:
            shutil.rmtree(elt_path)
        except:
            os.unlink(elt_path)

    def unzipped(self, path):
        return self

    def zipped(self, path, overwrite=False):
        "create on-disk and return a zipped odf package instance at path location"
        # usual chacks on path
        path = osp.realpath(path)
        if osp.exists(path) and not overwrite:
            raise IOError('%s alreadyt exist' % path)
        zip = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
        for elt in self.subelements():
            if elt.endswith(os.sep):
                data = ''
            else:
                data = open(osp.join(self.path, elt), 'rb').read()
            zip.writestr(elt, data)
        zip.close()
        return ZippedODFPackage(path)

class ZippedODFPackage(ODFPackage):
    """A standard zipped ODF package."""

    def __init__(self, path, mode='r'):
        super(ZippedODFPackage, self).__init__(path, mode)
        if not zipfile.is_zipfile(self.path):
            raise NotAnOdf('%s is not an odf file (it is not even a zip file)' % self.path)
        zip = zipfile.ZipFile(self.path, mode)
        corrupt = zip.testzip()
        if corrupt:
            raise CorruptOdf('%s is corrupt' % corrupt)
        self.zip = zip

    def _subelements(self):
        for elt in self.zip.namelist():
            if not elt.endswith('/'):
                yield elt

    def _read_zip(self, elt):
        return self.zip.read(elt)

    if sys.platform == 'win32':
        def subelements(self):
            for elt in self._subelements():
                yield elt.replace('/', '\\')

        def _read_zip(self, elt):
            return self.zip.read(elt.replace('\\', '/'))
        def _write_into(self, elt, bytestr):
            self.zip.writestr(elt.replace('\\', '/'), bytestr)
    else:
        subelements = _subelements

    def data(self, elt, default=None):
        """get the data associated to an element
        the element must be present in self.subelements()
        if no default is given"""
        if elt not in self.subelements():
            if default is not None:
                return default
            raise ValueError('%s is not an existing element of %s' % (elt, self.path))
        data = self._read_zip(elt)
        if elt.endswith('.xml'):
            data = normalize_xml(data)
        return data

    def unzipped(self, path, overwrite=False, mode='r'):
        "create on-disk and return an unzipped odf package instance at path location"
        path = osp.realpath(path)
        if osp.exists(path):
            if not overwrite:
                raise IOError('%s already exist' % path)
            inplace = UnzippedODFPackage(path)
            to_remove = set(inplace.subelements()) - set(self.subelements())
            if to_remove:
                to_remove = [osp.join(path, elt)
                             for elt in to_remove]
                from ovcs.vc import Repository
                vcs = Repository.frompath(path)
                if vcs is None:
                    for elt in to_remove:
                        os.unlink(elt)
                else:
                    vcs.remove(to_remove)
        return self._unzipped(path, mode)

    def _unzipped(self, path, mode):
        for elt in self._subelements():
            elt_parts = elt.split('/')
            elt_container = osp.join(*[path] + elt_parts[:-1])
            elt_basename = elt_parts[-1]
            if not osp.exists(elt_container):
                os.makedirs(elt_container)
            elt_fullpath = osp.join(elt_container, elt_basename)
            elt_file = open(elt_fullpath, 'wb')
            data = self.zip.read(elt)
            if elt_basename.endswith('.xml'):
                data = normalize_xml(data)
            elt_file.write(data)
        return UnzippedODFPackage(path, mode)

    def zipped(self, path):
        return self


class StreamODFPackage(ZippedODFPackage):

    def __init__(self, fileobj, mode='r'):
        self.path = 'a_stream'
        try:
            self.zip = zipfile.ZipFile(fileobj)
        except zipfile.BadZipfile, badzip:
            raise NotAnOdf(badzip.args[0])
        corrupt = self.zip.testzip()
        if corrupt:
            raise CorruptOdf('%s is corrupt' % corrupt)

__all__ = ["ZipODFPackage", "UnpackedODFPackage", "StreamODFPackage"]

