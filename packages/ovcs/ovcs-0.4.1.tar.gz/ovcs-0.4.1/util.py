# only lxml.etree has a tostring
# that takes a pretty_print argument
from lxml import etree

import os.path as osp

def normalize_xml(xmlstr):
    "outputs properly line-breaked, indented xml string from xml-like string"
    if len(xmlstr) == 0:
        return xmlstr
    tree = etree.fromstring(xmlstr)
    data = etree.tostring(tree, pretty_print=True)
    return data

def cut_prefix(path, prefix, sep=None):
    """
    >>> cut_prefix('/home/auc/foo/bar', '/home/auc')
    'foo/bar'
    """
    if sep is None:
        sep = osp.sep
    assert path.startswith(prefix), 'path %s must start with prefix %s' % (path, prefix)
    return path.rpartition(prefix)[-1].lstrip(sep)
