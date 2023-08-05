# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

from petsc4py.lib import _petsc

_VecType  = None

_VecDupl  = _petsc.VecDuplicate
_VecCopy  = _petsc.VecCopy
_VecAbs   = _petsc.VecAbs
_VecShift = _petsc.VecShift
_VecScale = _petsc.VecScale
_VecAXPY  = _petsc.VecAXPY
_VecPwMul = _petsc.VecPointwiseMult
_VecPwDiv = _petsc.VecPointwiseDivide
_VecRecip = _petsc.VecReciprocal

# unary operations

def __pos__(self):
    vec = _VecDupl(self)
    _VecCopy(self, vec)
    return vec

def __neg__(self):
    vec = __pos__(self)
    _VecScale(vec, -1)
    return vec
    
def __abs__(self):
    vec = __pos__(self)
    _VecAbs(vec)
    return vec


# inplace binary operations

def __iadd__(self, other):
    if isinstance(other, type(self)):
        _VecAXPY(self, 1, other)
    elif isinstance(other, (tuple, list)):
        alpha, vec = other
        _VecAXPY(self, alpha, vec)
    else:
        _VecShift(self, other)
    return self

def __isub__(self, other):
    if isinstance(other, type(self)):
        _VecAXPY(self, -1, other)
    elif isinstance(other, (tuple, list)):
        alpha, vec = other
        _VecAXPY(self, -alpha, vec)
    else:
        _VecShift(self, -other)
    return self

def __imul__(self, other):
    if isinstance(other, type(self)):
        _VecPwMul(self, self, other)
    else:
        _VecScale(self, other)
    return self

def __idiv__(self, other):
    if isinstance(other, type(self)):
        _VecPwDiv(self, self, other)
    else:
        _VecScale(self, 1.0/other)
    return self


# binary operations

def __add__(self, other):
    return __iadd__(__pos__(self), other)

def __sub__(self, other):
    return __isub__(__pos__(self), other)

def __mul__(self, other):
    return __imul__(__pos__(self), other)

def __div__(self, other):
    return __idiv__(__pos__(self), other)



# reflected binary operations

def __radd__(self, other):
    return __add__(self, other)

def __rsub__(self, other):
    vec =  __sub__(self, other)
    _VecScale(vec, -1)
    return vec

def __rmul__(self, other):
    return __mul__(self, other)

def __rdiv__(self, other):
    vec = __div__(self, other)
    _VecRecip(vec)
    return vec



# true division operations

def __truediv__(self, other):
    return __div__(self, other)

def __itruediv__(self, other):
    return __idiv__(self, other)

def __rtruediv__(self, other):
    return __rdiv__(self, other)


