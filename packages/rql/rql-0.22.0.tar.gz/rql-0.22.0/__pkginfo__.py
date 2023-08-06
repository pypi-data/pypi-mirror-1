# pylint: disable-msg=W0622
"""RQL packaging information.

:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

modname = "rql"
numversion = (0, 22, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LCL'
copyright = '''Copyright (c) 2003-2009 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Sylvain Thenault"
author_email = "devel@logilab.fr"

short_desc = "relationship query language (RQL) utilities"
long_desc = """A library providing the base utilities to handle RQL queries,
such as a parser, a type inferencer.
"""
web = "" #"http://www.logilab.org/projects/rql"
#ftp = "ftp://ftp.logilab.org/pub/rql"


# debianize info
debian_maintainer = 'Sylvain Thenault'
debian_maintainer_email = 'sylvain.thenault@logilab.fr'
pyversions = ['2.4']


from distutils.core import Extension

include_dirs = []

ext_modules = [ Extension('rql_solve',
                          ['gecode_solver.cpp'],
                          libraries=['gecodeint', 'gecodekernel', 'gecodesearch'],
                          
                          ) ]
