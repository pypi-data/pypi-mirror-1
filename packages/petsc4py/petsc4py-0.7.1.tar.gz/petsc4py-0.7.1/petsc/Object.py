# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
PETSc Objects
=============

"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reStructuredText'

# --------------------------------------------------------------------

__all__ = ['Object']

# --------------------------------------------------------------------

from petsc4py.lib import _petsc

# --------------------------------------------------------------------

class PETScType(type):
    """
    PETSc Object metaclass.
    """
    def __init__(mcs, name, bases, dct):
        # initialize base class of this metaclass
        super(PETScType, mcs).__init__(name, bases, dct)
        # this part registers this class in C extension module
        # for easy access of type objects in the C side
        reg_name = name + 'TypeRegister'
        reg_type = getattr(_petsc, reg_name, None)
        if reg_type is not None:
            delattr(_petsc, reg_name)
            reg_type(mcs)
        # type registration in Py module
        tp_name = '_' + name
        if not hasattr(_petsc, tp_name):
            setattr(_petsc, tp_name, mcs)
        # SWIG pointer getter
        swig_get_name = name + '__swig_this__'
        swig_get_func = getattr(_petsc, swig_get_name, None)
        if swig_get_func is not None:
            delattr(_petsc, swig_get_name)
            setattr(mcs, '__swig_this__', swig_get_func)
        # SWIG clientdata
        reg_name = name + 'SwigRegister'
        swigreg = getattr(_petsc, reg_name, None)
        if swigreg is not None:
            delattr(_petsc, reg_name)
            from_name = name + 'FromSwig'
            fromswig = getattr(_petsc, from_name, None)
            if fromswig is not None:
                delattr(_petsc, from_name)
                swigreg(fromswig)

# --------------------------------------------------------------------


class Object(_petsc.Object):

    """
    Abstract PETSc object, any object.

    .. note:: This is the base class from which all objects appear.
    """

    __metaclass__ = PETScType

    def __init__(self, *targs, **kwargs):
        super(Object, self).__init__(*targs, **kwargs)
                       
    def dispose(self):
        """
        Sets the pointer to the underlying PETSc object to NULL.
        """
        _petsc.PetscObjectDispose(self)

    def create(self, comm=None):
        """
        Creates a base PETSc object.
        """
        _petsc.PetscObjectCreate(comm, self)
        
    def destroy(self):
        """
        Destroys any PETSc object, regardless of the type.
        """
        _petsc.PetscObjectDestroy(self)

    def getOptionsPrefix(self):
        """
        Gets the prefix used for searching for all options of
        PETSc objects in the options database.
        """
        klass = _petsc.PetscObjectGetClassName(self)
        return getattr(_petsc, klass + 'GetOptionsPrefix',
                       _petsc.PetscObjectGetOptionsPrefix)(self)

    def setOptionsPrefix(self, prefix):
        """
        Sets the prefix used for searching for all options of
        PETSc objects in the options database.
        """
        klass = _petsc.PetscObjectGetClassName(self)
        getattr(_petsc, klass + 'SetOptionsPrefix',
                _petsc.PetscObjectSetOptionsPrefix)(self, prefix)
        
    def appendOptionsPrefix(self, prefix):
        """
        Appends to the prefix used for searching for all options of
        PETSc objects in the options database.
        """
        klass = _petsc.PetscObjectGetClassName(self)
        getattr(_petsc, klass + 'AppendOptionsPrefix',
                _petsc.PetscObjectAppendOptionsPrefix)(self, prefix)

    def prependOptionsPrefix(self, prefix):
        """
        Prepends to the prefix used for searching for all options of
        PETSc objects in the options database.
        """
        klass = _petsc.PetscObjectGetClassName(self)
        getattr(_petsc, klass + 'PrependOptionsPrefix',
                _petsc.PetscObjectPrependOptionsPrefix)(self, prefix)

    def setFromOptions(self):
        """
        Sets generic parameters from user options.
        """
        klass = _petsc.PetscObjectGetClassName(self)
        getattr(_petsc, klass + 'SetFromOptions',
                _petsc.PetscObjectSetFromOptions)(self)

    def setUp(self):
        """
        Sets up the internal data structures for the later use.
        """
        klass = _petsc.PetscObjectGetClassName(self)
        getattr(_petsc, klass + 'SetUp',
                _petsc.PetscObjectSetUp)(self)

    def getType(self):
        """
        Gets the type for any PETSc object.
        """
        klass = _petsc.PetscObjectGetClassName(self)
        get_type = getattr(_petsc, klass + 'GetType', None)
        if get_type is not None:
            return get_type(self)
        else:
            tpint, tpstr = _petsc.PetscObjectGetType(self)
            return tpstr or tpint

    def setType(self, otype):
        """
        Sets the type for any PETSc object.
        """
        klass = _petsc.PetscObjectGetClassName(self)
        set_type = getattr(_petsc, klass + 'SetType', None)
        if set_type is not None:
            otype = _petsc.get_type(self, otype)
            set_type(self, otype)
        else:
            _petsc.PetscObjectSetType(self, otype)

    def getCookie(self):
        """
        Gets the cookie for any PETSc object.
        """
        return _petsc.PetscObjectGetCookie(self)

    def getClassName(self):
        """
        Get the abstract class name of any PETSc object.
        """
        return _petsc.PetscObjectGetClassName(self)

    def getRefCount(self):
        """
        Gets the current reference count for any PETSc object.
        """
        return _petsc.PetscObjectGetReference(self)

    getReferenceCount = getRefCount

    def addReference(self):
        """
        Increases the reference count of this object by one.
        """
        _petsc.PetscObjectReference(self)

    def delReference(self):
        """
        Decreases the reference count of this object by one.
        """
        _petsc.PetscObjectDereference(self)

    deleteReference = delReference

    def getName(self):
        """
        Gets a string name associated with a PETSc object.
        """
        return _petsc.PetscObjectGetName(self)

    def setName(self, name):
        """
        Sets a string name associated with a PETSc object.
        """
        _petsc.PetscObjectSetName(self, name)

    def getState(self):
        """
        Gets the integer state for any PETSc object.
        """
        return _petsc.PetscObjectGetState(self)

    def setState(self, state):
        """
        Sets the integer state for any PETSc object.
        """
        return _petsc.PetscObjectSetState(self, state)
        
    def increaseState(self):
        """
        Increases the integer state for any PETSc object.
        """
        return _petsc.PetscObjectStateIncrease(self)

    def decreaseState(self):
        """
        Decreases the integer state for any PETSc object.
        """
        return _petsc.PetscObjectStateDecrease(self)

    def getComm(self):
        """
        Gets the MPI communicator for any PETSc object.
        """
        return _petsc.PetscObjectGetComm(self)

    def barrier(self):
        """
        Blocks until this routine is executed by all processors owning
        the object.

        .. note:: This routine calls ``MPI_Barrier()`` with the
           communicator of the PETSc object.
        """
        _petsc.PetscBarrier(self)

    def view(self, viewer=None):
        """
        Views any PETSc object, regardless of the type.
        """
        _petsc.PetscObjectView(self, viewer)

    def compose(self, name, obj):
        """
        Associates another PETSc object with a given PETSc object.
        """
        _petsc.PetscObjectCompose(self, name, obj)

    def query(self, name):
        """
        Gets a PETSc object associated with a given object.
        """
        obj = _petsc.PetscObjectQuery(self, name)
        return obj or None

    type   = property(getType, setType)
    cookie = property(getCookie)
    klass  = property(getClassName)

    prefix = property(getOptionsPrefix, setOptionsPrefix)

    name   = property(getName, setName)
    state  = property(getState, setState)
    comm   = property(getComm)

    refcount = property(getRefCount)


# --------------------------------------------------------------------
