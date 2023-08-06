# -*- coding: utf-8 -*-
import os
import sys
from unittest import TestCase, main
from ovcs.util import cut_prefix, normalize_xml

class TestUtil(TestCase):

    def test_cut_prefix(self):
        self.assertRaises(AssertionError, cut_prefix, '/a/b/c', 'd/e/f')
        self.assertEquals('foo/bar', cut_prefix('/home/auc/foo/bar', '/home/auc', sep='/'))

    def test_normalize_xml(self):
        sample = "<doc><foo>bar<quux>bla bla\n bli</quux></foo><foo><quux>omph</quux></foo></doc>"
        self.assertEquals(normalize_xml(sample), """<doc>
  <foo>bar<quux>bla bla
 bli</quux></foo>
  <foo>
    <quux>omph</quux>
  </foo>
</doc>
""")

    def test_normalize_with_non_ascii(self):
        sample = "<doc><foo>Mère Thérésa qui êtes ô cieux</foo><foo>restez-y</foo></doc>"
        self.assertEquals(normalize_xml(sample), """<doc>
  <foo>M&#232;re Th&#233;r&#233;sa qui &#234;tes &#244; cieux</foo>
  <foo>restez-y</foo>
</doc>
""")

if __name__ == '__main__':
    main()
