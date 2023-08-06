# -*- coding: utf-8 -*-

# pylint: disable-msg=W0622
"""cubicweb-forge application packaging information

Copyright (c) 2003-2009 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
modname = 'forge'
distname = 'cubicweb-forge'

numversion = (1, 2, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'

author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'

short_desc = 'forge component for the CubicWeb framework'
long_desc = '''This CubicWeb component provides a Forge application
that supports the process of collaborative developing software.

CubicWeb is a semantic web framework, see http://www.cubicweb.org
'''

from os import listdir as _listdir
from os.path import join, isdir

web = 'http://www.cubicweb.org/project/%s' % distname
classifiers = [
          'Environment :: Web Environment',
          'Framework :: CubicWeb',
          'Programming Language :: Python',
          'Programming Language :: JavaScript',
          'Topic :: Software Development :: Bug Tracking',
          ]

pyversions = ['2.4']

#from cubicweb.devtools.pkginfo import get_distutils_datafiles
CUBES_DIR = join('share', 'cubicweb', 'cubes')
THIS_CUBE_DIR = join(CUBES_DIR, 'forge')

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]

from glob import glob
try:
    data_files = [
        # common files
        [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
        ]
    # check for possible extended cube layout
    for dirname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'i18n', 'migration', 'wdoc'):
        if isdir(dirname):
            data_files.append([join(THIS_CUBE_DIR, dirname), listdir(dirname)])
    # Note: here, you'll need to add subdirectories if you want
    # them to be included in the debian package
except OSError:
    # we are in an installed directory
    pass


__depends_cubes__ = {'card': None,
                     'comment': '>= 1.2.0',
                     'email': '>= 1.2.1',
                     'file': '>= 1.2.0',
                     'folder': '>= 1.1.0',
                     'mailinglist': '>= 1.1.0',
                     'tag': '>= 1.2.0',
                     'tracker': '>= 1.1.0',
                     'nosylist': None,
                     }
__depends__ = {'cubicweb': '>= 3.5.0',
               }
for key,value in __depends_cubes__.items():
    __depends__['cubicweb-'+key] = value
__use__ = tuple(__depends_cubes__)



