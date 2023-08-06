# pylint: disable-msg=W0622
"""cubicweb-tracker application packaging information

Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
modname = 'tracker'
distname = 'cubicweb-tracker'

numversion = (1, 4, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'

author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'

short_desc = 'issue tracker component for the CubicWeb framework'
long_desc = '''Summary
-------

The `tracker` cube provides an issue tracker with projects, tickets and versions
to group tickets. You can defines roadmap for a project by planning future
versions.

A link to subscribe to rss feed for published versions of project is
located on each project toolbar.

Usage
-----

- ProjectRoadmapView, displays all version

- ProjectStatsView, displays the number of tickets for each status
  ('done', 'validation pending', and so on)
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
THIS_CUBE_DIR = join(CUBES_DIR, 'tracker')

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


__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.6.0'}
__use__ = tuple(__depends_cubes__)

