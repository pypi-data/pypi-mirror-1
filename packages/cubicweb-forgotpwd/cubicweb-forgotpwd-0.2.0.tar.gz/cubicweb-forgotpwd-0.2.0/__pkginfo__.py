# pylint: disable-msg=W0622
"""cubicweb-forgotpwd application packaging information"""

modname = 'forgotpwd'
distname = 'cubicweb-forgotpwd'

numversion = (0, 2, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LCL'
copyright = '''Copyright (c) 2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr -- mailto:contact@logilab.fr'''

author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'

short_desc = 'password recovery component for the CubicWeb framework'
long_desc = """\
Summary
-------

The `forgotpwd` cube cube provides an easy way to generate a new
password for an user.

Depends
-------

You must use the cube `registration`.

Usage
-----

This cube creates a new entity called `Fpasswd`. This is an internal
entity: managers and users can't read/delete or modify this kink of
entity.

The workflow of password recovery is defined below :

1. ask for a new password, the user must have a valid primary email
   associated to his account.

2. An email has been sent. This email contains a generated url associated to an
   user. This link is valid during a short period. This time limit can be
   configured in the all-in-one.conf file:

   .. sourcecode:: ini

      [FORGOTPWD]
      revocation-limit=30 # minutes

3. If the link is valid, the user can change his password in a new form.

There is an automatic task that delete periodically all old Fpasswd which are
stored in the database. This task is started at the launching of the
application.
"""

web = 'http://www.cubicweb.org/project/%s' % distname


from os import listdir as _listdir
from os.path import join, isdir, exists
from glob import glob

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]

data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
    ]
# check for possible extended cube layout
for dname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'i18n', 'migration'):
    if isdir(dname):
        data_files.append([join(THIS_CUBE_DIR, dname), listdir(dname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package

__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.6.1',
               'python-crypto': None,
               'PIL': None,
               }
__use__ = tuple(__depends_cubes__)
__recommend__ = ()

