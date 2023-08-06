import sys
import os, os.path as osp
from atexit import register
from unittest import TestCase, main
from ovcs.package import ODFPackage, ZippedODFPackage, UnzippedODFPackage, \
    NotAnOdf, CorruptOdf

from ovcs.tests.helper import fullpath, cleanup, shutdown

CLEANUP = set()
register(shutdown, CLEANUP)

class TestPackage(TestCase):

    def regpath(self, basepath):
        path = fullpath(basepath)
        self.CLEANUP.add(path)
        return path

    def setUp(self):
        self.CLEANUP = set()

    def tearDown(self):
        cleanup(self.CLEANUP, CLEANUP)

    def test_empty(self):
        if sys.platform == 'win32':
            return
        empty = ZippedODFPackage(fullpath('empty.odt'))
        self.assertEquals(['mimetype', 'content.xml', 'styles.xml', 'meta.xml',
                           'Thumbnails/thumbnail.png', 'Configurations2/accelerator/current.xml',
                           'settings.xml', 'META-INF/manifest.xml'],
                          list(empty.subelements()))

    def test_safety(self):
        empty = ZippedODFPackage(fullpath('empty.odt'))
        unzipped = empty.unzipped(self.regpath('empty'))
        self.assertRaises(IOError, empty.unzipped, fullpath('empty'))
        unzipped = empty.unzipped(self.regpath('empty'), overwrite=True)
        newzipped = unzipped.zipped(self.regpath('newempty.odt'))
        self.assertRaises(IOError, unzipped.zipped, fullpath('newempty.odt'))
        newzipped = unzipped.zipped(self.regpath('newempty.odt'), overwrite=True)

    def test_zip_unzip(self):
        hello = ZippedODFPackage(fullpath('hello.odt'))
        unzipped = hello.unzipped(self.regpath('hello'))
        self.assertEquals(sorted(hello.subelements()), sorted(unzipped.subelements()))
        zipped = unzipped.zipped(self.regpath('newhello.odt'))
        self.assertTrue(zipped.is_zipped())
        self.assertEquals(zipped, unzipped)
        self.assertFalse(unzipped.is_zipped())
        self.assertEquals(unzipped, hello)
        self.assertTrue(hello.is_zipped())
        self.assertEquals(zipped, hello)

    def test_zip_unzip(self):
        hello = ZippedODFPackage(fullpath('hello.odt'))
        unzipped = hello.unzipped(self.regpath('hello'))
        self.assertRaises(OSError, unzipped.remove, 'content.xml')
        unzipped = hello.unzipped(self.regpath('hello'), mode='w', overwrite=True)
        unzipped.remove('content.xml')
        unzipped.remove('META-INF')
        self.assertEquals(unzipped.data('content.xml', default='toto'), 'toto')
        self.assertRaises(ValueError, unzipped.data, 'META-INF/manifest.xml')

    def test_frompath(self):
        hello = ODFPackage.frompath(fullpath('hello.odt'))
        self.assertTrue(hello.is_zipped())
        unzipped = hello.unzipped(self.regpath('hello'), overwrite=True)
        self.assertFalse(unzipped.is_zipped())
        self.assertEquals(unzipped, hello)

    def test_bogus(self):
        # missing meta.xml
        bogus = ODFPackage.frompath(fullpath('bogus.odt'))
        self.assertRaises(CorruptOdf, bogus.quickcheck)
        # invalid content.xml
        corrupt = ODFPackage.frompath(fullpath('corrupt.odt'))
        self.assertRaises(CorruptOdf, corrupt.quickcheck)

    def test_diff(self):
        hello = ZippedODFPackage(fullpath('hello.odt'))
        bogus = ZippedODFPackage(fullpath('bogus.odt'))
        self.assertEquals(hello.diff(bogus),
                          ['Deleted : hello.odt/meta.xml',
                           'Modified : hello.odt/Thumbnails/thumbnail.png',
                           'no visual diff for binary file of mime-type image/png',
                           'Modified : hello.odt/content.xml',
                           '--- hello.odt/content.xml\n+++ bogus.odt/content.xml\n@@ -14,7 +14,7 @@\n         <text:sequence-decl text:display-outline-level="0" text:name="Text"/>\n         <text:sequence-decl text:display-outline-level="0" text:name="Drawing"/>\n       </text:sequence-decls>\n-      <text:p text:style-name="Standard">Hello !</text:p>\n+      <text:p text:style-name="Standard"/>\n     </office:text>\n   </office:body>\n </office:document-content>',
                           'Modified : hello.odt/settings.xml',
                           '--- hello.odt/settings.xml\n+++ bogus.odt/settings.xml\n@@ -10,7 +10,7 @@\n       <config:config-item-map-indexed config:name="Views">\n         <config:config-item-map-entry>\n           <config:config-item config:name="ViewId" config:type="string">view2</config:config-item>\n-          <config:config-item config:name="ViewLeft" config:type="long">4189</config:config-item>\n+          <config:config-item config:name="ViewLeft" config:type="long">3002</config:config-item>\n           <config:config-item config:name="ViewTop" config:type="long">3002</config:config-item>\n           <config:config-item config:name="VisibleLeft" config:type="long">1002</config:config-item>\n           <config:config-item config:name="VisibleTop" config:type="long">0</config:config-item>'])
        self.assertEquals(hello.changelist(bogus),
                          {'deleted': ['meta.xml'],
                           'added': [],
                           'changed': ['Thumbnails/thumbnail.png', 'content.xml', 'settings.xml']})

if __name__ == '__main__':
    main()
