#       $Id: setup.py,v 1.1.1.1 2008/06/27 19:21:39 dieter Exp $
from os import environ
from os.path import join, exists
from sys import exit
from distutils.core import Extension

ZODB_HOME = environ.get('ZODB_HOME')
if not ZODB_HOME:
  exit("""This package depends on the ZODB3 source. 
    You must make this source available and then let the environment variable
    'ZODB_HOME' point to it.
    If you use the ZODB source within a Zope2 source tree, let 'ZODB_HOME'
    point to the 'lib/python' subdirectory of your Zope2 source tree.
    """)
# normalize a bit
#  the 'easy_install -e' download contains the source code inside an 'src'
#  subdirectory. ZODB sources which are part of "Zope2" lack this 'src'.
if exists(join(ZODB_HOME, 'src')): ZODB_HOME = join(ZODB_HOME, 'src')

if not exists(join(ZODB_HOME, "persistent", "cPersistence.h")):
  exit("cannot recognize the ZODB source")

from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup, Extension
  setupArgs = dict(
      install_requires=[], # we need the ZODB3 source but do not know how to express this
      include_package_data=True,
      namespace_packages=['dm'],
      zip_safe=False, # to let the tests work
      )
except ImportError:
  # use distutils
  from distutils import setup
  from distutils.core import Extension
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'incrementalsearch')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()


setup(name = "dm.incrementalsearch",
      version=pread('VERSION.txt').split('\n')[0],
      description='An efficient low level search execution engine on top of ZODB.BTrees.',
      long_description=pread('README.txt'),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Framework :: ZODB',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: C',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://www.dieter.handshake.de/pyprojects/zope',
      packages=['dm', 'dm.incrementalsearch', 'dm.incrementalsearch.tests'],
      keywords='search, efficient, ZODB, incremental, BTrees',
      license='BSD (see "dm/incrementalsearch/LICENSE.txt", for details)',
      ext_modules = [
         Extension("dm.incrementalsearch._isearch",
            [join('dm', 'incrementalsearch', f)
             for f in ("_isearch.c", "_isearch_int.c", "_isearch_obj.c", "_isearch_long.c")],
            include_dirs = [ZODB_HOME,],
            ),
         ],
      **setupArgs
      )
