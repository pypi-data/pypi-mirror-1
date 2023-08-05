# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
Access to PETSc extension module.
"""

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'


def Import(arch=None):
    """
    Imports PETSc extension module for a given configuration name.
    """
    import sys, os, imp
    # test if extension module was imported before
    modname = __name__ + '._petscext'
    petscext = sys.modules.get(modname)
    if petscext is not None:
        # if provided argument is 'None', do nothing; otherwise this
        # call may be invalid if extension module for other arch has
        # been already imported.
        if arch is not None and arch != petscext.__arch__:
            raise ImportError("%s already imported" % petscext)
        return petscext
    # determine PETSC_ARCH value
    if arch is None:
        arch = os.environ.get('PETSC_ARCH')
        if not arch:
            petsc_cfg = open(os.path.join(__path__[0], 'petsc.cfg'))
            lines = petsc_cfg.read().replace(' ', '').splitlines()
            petsc_cfg.close()
            petsc_cfg = dict(line.split('=') for line in lines)
            arch = petsc_cfg['PETSC_ARCH'].split(',')[0]
        mpath = os.path.join(__path__[0], arch)
        if not os.path.isdir(mpath):
            raise ImportError("invalid 'PETSC_ARCH': '%s'" % arch)
    else:
        if not isinstance(arch, str):
            raise TypeError("'arch' argument must be string")
        mpath = os.path.join(__path__[0], arch)
        if not os.path.isdir(mpath):
            raise ImportError("invalid 'arch': '%s'" % arch)
    # import appropriate extension module
    mpath = os.path.join(__path__[0], arch)
    mname = __name__ + '._petscext'
    fo, fn, stuff = imp.find_module('_petscext', [mpath])
    petscext = imp.load_module(mname, fo, fn, stuff)
    petscext.__arch__ = arch
    sys.modules[__name__]._petscext = petscext
    return petscext 


if False:
    _petsc = None
    _petsc = Import()
