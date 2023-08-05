#!/bin/env python

"""
PETSc for Python
================

Python bindings for PETSc libraries.
"""


## try:
##     import setuptools
## except ImportError:
##     pass


# --------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------

from configure import metadata

name     = 'petsc4py'
version  = open('VERSION.txt').read().strip()
descr    = __doc__.strip().split('\n'); del descr[1:3]
devstat  = ['Development Status :: 3 - Alpha']
download = 'http://cheeseshop.python.org/packages/source/%s/%s/%s-%s.tar.gz'

metadata['name'] = name
metadata['version'] = version
metadata['description'] = descr.pop(0)
metadata['long_description'] = '\n'.join(descr)
metadata['classifiers'] += devstat
metadata['download_url'] = download % (name[0], name, name, version)

# --------------------------------------------------------------------
# Extension modules
# --------------------------------------------------------------------

def get_ext_modules(Extension):
    from os   import walk
    from glob import glob
    from os.path import join, sep as pathsep, extsep, abspath

    # generare dependencies
    extroot = join('petsc', 'lib', 'ext')
    depends = []
    for pth, dirs, files in walk(join(extroot, 'swig')):
        depends += glob(join(pth, '*%si' % extsep))
    for pth, dirs, files in walk(join(extroot, 'src')):
        depends += glob(join(pth, '*%s[h,c]' % extsep))
    #import pprint
    #pprint.pprint( depends)
    seprepl = lambda p: p.replace(pathsep,'/').replace(extsep,'.')
    depends = map(seprepl, depends)
    extdir  = 'petsc/lib/ext'
    petsc_c   = Extension('petsc4py.lib._petscext',
                          sources=[extdir + '/' + 'petscext_c.i',
                                   extdir + '/' + 'petsclib.c'],
                          depends=depends,
                          include_dirs=[extdir],
                          language='c')
    petsc_cxx = Extension('petsc4py.lib._petscext',
                          sources=[extdir + '/' + 'petscext_cpp.i',
                                   extdir + '/' + 'petsclib.cpp'],
                          depends=depends,
                          include_dirs=[extdir],
                          language='c++')
    return [petsc_c, petsc_cxx]


# --------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------

from configure import setup
from configure import Extension
from configure import config
from configure import build
from configure import build_src
from configure import build_py
from configure import build_ext
from configure import sdist

def main():
    setup(packages     = ['petsc4py',
                          'petsc4py.lib'],
          package_dir  = {'petsc4py'     : 'petsc',
                          'petsc4py.lib' : 'petsc/lib'},
          package_data = {'petsc4py.lib': ['petsc.cfg']},
          ext_modules  = get_ext_modules(Extension),
          cmdclass     = {'config'     : config,
                          'build'      : build,
                          'build_py'   : build_py,
                          'build_src'  : build_src,
                          'build_ext'  : build_ext,
                          'sdist'      : sdist},
          **metadata)

# --------------------------------------------------------------------

if __name__ == '__main__':
    from distutils import sysconfig
    cvars = sysconfig.get_config_vars()
    cflags = cvars['OPT'].split()
    for flag in ('-g', '-g3', '-Wstrict-prototypes'):
        try:
            cflags.remove(flag)
        except ValueError:
            pass
    cvars['OPT'] = str.join(' ', cflags) 

if __name__ == '__main__':
    ## from distutils import log
    ## log.set_verbosity(log.DEBUG)
    main()
