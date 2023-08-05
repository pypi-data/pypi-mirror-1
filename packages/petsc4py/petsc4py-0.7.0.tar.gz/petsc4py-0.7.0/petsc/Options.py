# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
PETSc Options Database
======================

"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reST'

# --------------------------------------------------------------------

__all__ = ['Options']

# --------------------------------------------------------------------

import sys as _sys
from petsc4py.lib import _petsc

# --------------------------------------------------------------------


class Options(object):

    """
    PETSc Options database.
    """

    def __init__(self, prefix=None):
        self._prefix  = None
        self.setPrefix(prefix)

    def __contains__(self, item):
        return self.hasName(item)
        
    def __getitem__(self, item):
        try:
            return self.getString(item)
        except KeyError:
            raise KeyError('option not found: %s' % item)
    
    def __setitem__(self, item, value):
        self.setValue(item, value)

    def __delitem__(self, item):
        self.delValue(item)

    @staticmethod
    def insertFile(filename):
        """
        """
        _petsc.PetscOptionsInsertFile(filename)

    @staticmethod
    def insertString(string):
        """
        """
        _petsc.PetscOptionsInsertString(string)


    @staticmethod
    def setFromOptions():
        """
        Sets generic parameters from user options.
        """
        _petsc.PetscOptionsSetFromOptions()

    @staticmethod
    def setMonitor(monitor):
        """
        """
        _petsc.PetscOptionsMonitorSet(monitor)
    
    @staticmethod
    def cancelMonitor():
        """
        """
        _petsc.PetscOptionsMonitorCancel()

    def setAlias(self, newname, oldname):
        """
        """
        _, newname = self._chk_opt(None, newname)
        _, oldname = self._chk_opt(None, oldname)
        _petsc.PetscOptionsSetAlias(newname, oldname)

    def hasName(self, name, prefix=None):
        """
        """
        prefix, name = self._chk_opt(prefix, name)
        retval = _petsc.PetscOptionsHasName(prefix, name)
        return bool(retval)

    def setValue(self, name, value, prefix=None):
        """
        """
        option = self._fmt_opt(prefix, name)
        if value is not None:
            value = str(value)
        _petsc.PetscOptionsSetValue(option, value)

    def delValue(self, name, prefix=None):
        """
        """
        option = self._fmt_opt(prefix, name)
        _petsc.PetscOptionsClearValue(option)

    def clearValue(self, name, prefix=None):
        """
        """
        option = self._fmt_opt(prefix, name)
        _petsc.PetscOptionsClearValue(option)

    def getBool(self, name, default=None, prefix=None):
        """
        """
        value = self._get_opt('Truth', prefix, name, default)
        return bool(value)

    def getTruth(self, name, default=None, prefix=None):
        """
        """
        value = self._get_opt('Truth', prefix, name, default)
        return bool(value)

    def getInt(self, name, default=None, prefix=None):
        """
        """
        value = self._get_opt('Int', prefix, name, default)
        return _petsc.PetscInt(value).item()
    
    def getReal(self, name, default=None, prefix=None):
        """
        """
        value = self._get_opt('Real', prefix, name, default)
        return _petsc.PetscReal(value).item()

    def getScalar(self, name, default=None, prefix=None):
        """
        """
        value = self._get_opt('Scalar', prefix, name, default)
        return _petsc.PetscScalar(value).item()

    def getString(self, name, default=None, prefix=None):
        """
        """
        value = self._get_opt('String', prefix, name, default)
        return str(value)

    def getOption(self, otype, name, default=None, prefix=None):
        """
        """
        getter = getattr(self, 'get%s' % otype.title())
        return getter(name, default, prefix)

    def getAll(self, prefix=None):
        """
        """
        prefix = self._chk_prefix(prefix)
        prefix = prefix  or ''
        options = _petsc.PetscOptionsGetAll().split('-')
        options = [opt.strip().split(None, 1) for opt in options
                   if opt and opt.startswith(prefix)]
        for opt in options:
            opt[0] = opt[0].replace(prefix, '', 1)
            if len(opt) == 1:
                opt.append(None)
        return dict(options)

    def view(self, fileobj=None):
        """
        Prints the options that have been loaded.
        """
        if isinstance(fileobj, file):
            _petsc.PetscOptionsPrint(fileobj)
        elif fileobj is None:
            self.view(_sys.stdout)
        elif isinstance(fileobj, str):
            fd = open(fileobj, 'w')
            self.view(fd)
            fd.close()
        else:
            raise TypeError('expecting a file object or string')

    def getPrefix(self):
        """
        """
        return getattr(self, '_prefix', None) or ''

    def setPrefix(self, prefix):
        """
        """
        if prefix is not None:
            prefix = self._chk_prefix(prefix) or None
        self._prefix = prefix

    def delPrefix(self):
        """
        """
        self._prefix = None

    prefix = property(getPrefix, setPrefix, delPrefix, doc='options prefix')

    # helper methods
    
    def _chk_prefix(self, prefix):
        if prefix is None:
            prefix = getattr(self, '_prefix', None) or None
        elif isinstance(prefix, Options):
            prefix = prefix.getPrefix()
        elif isinstance(prefix, _petsc._Object):
            prefix = prefix.getOptionsPrefix()
        elif not isinstance(prefix, str):
            raise TypeError('option prefix must be string')
        if not prefix:
            return None
        if prefix.count(' '):
            raise ValueError('option prefix should not have spaces')
        if prefix.startswith('-'):
            raise ValueError('option prefix should not start with a hypen')
        return prefix
        
    def _chk_opt(self, prefix, name):
        if prefix is None and isinstance(name, (tuple, list)):
            prefix, name = name
        prefix = self._chk_prefix(prefix)
        if not isinstance(name, str):
            raise TypeError('option name must be string')
        if not name or name == '-':
            raise ValueError('option name should not be empty')
        if name.count(' '):
            raise ValueError('option name should not have spaces')
        if not name.startswith('-'):
            name = '-' + name
        return (prefix, name)
        
    def _fmt_opt(self, prefix, name):
        prefix, name = self._chk_opt(prefix, name)
        return '-%s%s' % (prefix or '', name[1:])
    
    def _get_opt(self, otype, prefix, name, default):
        getter = getattr(_petsc, 'PetscOptionsGet' + otype.title())
        prefix, name = self._chk_opt(prefix, name)
        value, found = getter(prefix, name)
        # return value if found else default if provided
        if found:
            return value
        if default is not None:
            return default
        raise KeyError('option not found and default value not provided')
