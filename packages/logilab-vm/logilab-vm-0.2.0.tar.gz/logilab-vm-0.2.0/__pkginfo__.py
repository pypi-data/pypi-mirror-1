"""logilab-vm packaging information.

:copyright: 2000-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

distname = 'logilab-vm'
modname = 'logilab-vm'
numversion = (0, 2, 0)
version = '.'.join([str(num) for num in numversion])

license = 'GPL'
copyright = '''Copyright (c) 2003-2009 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "devel@logilab.fr"

short_desc = "useful miscellaneous modules used by Logilab projects"

long_desc = """based on libvirt and virsh, it contains an API and two HMI: \
onsole and web (web comming up) all written in Python"""

web = "http://www.logilab.org/project/%s" % distname
ftp = "ftp://ftp.logilab.org/pub/%s" % modname
mailinglist = "mailto://python-projects@lists.logilab.org"

scripts = ('bin/logilab-vm',)
from os.path import join
#include_dirs = [join('test', )]
pyversions = ['2.4', '2.5']
debian_maintainer = 'Alexandre Fayolle'
debian_maintainer_email = 'afayolle@debian.org'
