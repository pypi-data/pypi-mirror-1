 # pylint: disable-msg=W0622
"""cubicweb-mailinglist packaging information"""

modname = 'mailinglist'
distname = "cubicweb-%s" % modname

numversion = (1, 5, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = "mailing-list component for the CubicWeb framework"
long_desc = """This CubicWeb component models mailing list and allows to archive
threaded e-mail discussions. This is not a mailing list manager!

CubicWeb is a semantic web framework, see http://www.cubicweb.org
"""

from os import listdir
from os.path import join

CUBES_DIR = join('share', 'cubicweb', 'cubes')
try:
    data_files = [
        [join(CUBES_DIR, 'mailinglist'),
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        #[join(CUBES_DIR, 'mailinglist', 'data'),
        # [join('data', fname) for fname in listdir('data')]],
        [join(CUBES_DIR, 'mailinglist', 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(CUBES_DIR, 'mailinglist', 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass

# used packages
__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.6.0'}
__use__ = tuple(__depends_cubes__)
classifiers = [
            'Environment :: Web Environment',
            'Framework :: CubicWeb',
            'Programming Language :: Python',
            'Programming Language :: JavaScript',
            ]
