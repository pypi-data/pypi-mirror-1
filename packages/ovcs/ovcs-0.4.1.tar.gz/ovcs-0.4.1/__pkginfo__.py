"""Ovcs packaging information.

:organization: Logilab
:copyright: 2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

# pylint: disable-msg=W0622

# package name
modname = 'ovcs'

# release version
numversion = (0, 4, 1)
version = '.'.join(str(num) for num in numversion)

# license and copyright
license = 'GPL'
copyright = 'Copyright (c) '+' '.join([line.split(': ')[-1]for line in __doc__.splitlines()[3:5]])

# short and long description
short_desc = "cmd line tool to zip/unzip odt files & put them under version control"
long_desc = """unzipped odt files under version control !
An utility to put odt files, unzipped, under version control (subversion & mercurial supported).
Can show the diff of two odt files, either zipped or unzipped.
"""

# author name and email
author = "Logilab"
author_email = "contact@logilab.fr"

# home page
web = "http://www.logilab.org/project/%s" % modname

# mailing list
mailinglist = 'mailto://python-projects@lists.logilab.org' 

# download place
ftp = "ftp://ftp.logilab.org/pub/%s" % modname

# is there some directories to include with the source installation
include_dirs = []

# executable

scripts = ['bin/ovcs']

pyversions = ['2.5']
