# pylint: disable-msg=W0622
"""cubicweb-timesheet application packaging information"""

modname = 'timesheet'
distname = 'cubicweb-%s' % modname

numversion = (0, 2, 1)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2008-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = 'Logilab'
author_email = 'contact@logilab.fr'

short_desc = 'timesheet component for the CubicWeb framework'
long_desc = '''This CubicWeb component is for tracking resource availability
and usage (persons and their daily activities, meeting rooms and their
occupancy, etc.)
.
CubicWeb is a semantic web framework, see http://www.cubicweb.org
'''

from os import listdir as _listdir
from os.path import join, isdir

web = 'http://www.cubicweb.org/project/%s' % distname

pyversions = ['2.4']

#from cubicweb.devtools.pkginfo import get_distutils_datafiles
CUBES_DIR = join('share', 'cubicweb', 'cubes')
THIS_CUBE_DIR = join(CUBES_DIR, 'timesheet')

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')]

from glob import glob
try:
    data_files = [
        # common files
        [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
        ]
    # check for possible extended cube layout
    for dirname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'i18n', 'migration'):
        if isdir(dirname):
            data_files.append([join(THIS_CUBE_DIR, dirname), listdir(dirname)])
    # Note: here, you'll need to add subdirectories if you want
    # them to be included in the debian package
except OSError:
    # we are in an installed directory
    pass

cube_eid = None # <=== FIXME if you need direct bug-subscription
__depends_cubes__ = {'calendar':  '>= 0.1.0',
                     'workorder': '>= 0.6.0',
                     }
__depends__ = {'cubicweb': '>= 3.6.0'}
for key, value in __depends_cubes__.items():
    __depends__['cubicweb-'+key] = value
__use__ = tuple(__depends_cubes__)
__recommend__ = ()
classifiers = [
           'Environment :: Web Environment',
           'Framework :: CubicWeb',
           'Programming Language :: Python',
           'Programming Language :: JavaScript',
           ]
