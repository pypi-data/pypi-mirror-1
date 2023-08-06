# pylint: disable-msg=W0622
"""cubicweb-document application packaging information"""

modname = 'document'
distname = 'cubicweb-document'

numversion = (0, 3, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LCL'
copyright = '''Copyright (c) 2009 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr -- mailto:contact@logilab.fr'''

author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'

short_desc = 'document management services'
long_desc = '''document management services'''

from os import listdir as _listdir
from os.path import join, isdir

web = 'http://www.cubicweb.org/project/%s' % distname

pyversions = ['2.5']

#from cubicweb.devtools.pkginfo import get_distutils_datafiles
CUBES_DIR = join('share', 'cubicweb', 'cubes')
THIS_CUBE_DIR = join(CUBES_DIR, 'document')

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
__use__ = ('vcsfile', 'folder', 'i18ncontent')
__recommend__ = ()

