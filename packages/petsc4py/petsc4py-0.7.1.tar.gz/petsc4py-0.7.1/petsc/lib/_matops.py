# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

from petsc4py.lib import _petsc

_VecType  = _petsc._Vec
_MatType  = None

_ADD_VALS = _petsc.ADD_VALUES
_INS_VALS = _petsc.INSERT_VALUES
_CPY_VALS = _petsc.MAT_COPY_VALUES
_DIFF_NZP = _petsc.DIFFERENT_NONZERO_PATTERN

_MatDupl = lambda A: _petsc.MatDuplicate(A, _CPY_VALS)

_MatShift   = lambda Y, a:    _petsc.MatShift(Y, a)
_MatScale   = lambda Y, a:    _petsc.MatScale(Y, a)
_MatAXPY    = lambda Y, a, X: _petsc.MatAXPY(Y, a, X, _DIFF_NZP)
_MatDiagAdd = lambda Y, D:    _petsc.MatDiagonalSet(Y, D, _ADD_VALS)

def _MatVecMult(A, x):
    y = _petsc.MatGetVecLeft(A)
    _petsc.MatMult(A, x, y)
    return y

def _MatMatMult(A, B):
    return _petsc.MatMatMult(A, B, 1, None)

# unary operations

def __pos__(self):
    return _MatDupl(self)

def __neg__(self):
    mat = __pos__(self)
    _MatScale(mat, -1)
    return mat
    
# inplace binary operations

def __iadd__(self, other):
    if isinstance(other, type(self)):
        _MatAXPY(self, 1, other)
    elif isinstance(other, (tuple, list)):
        alpha, mat = other
        _MatAXPY(self, alpha, mat)
    elif isinstance(other, _VecType):
        _MatDiagAdd(self, other)
    else:
        _MatShift(self, other)
    return self

def __isub__(self, other):
    if isinstance(other, type(self)):
        _MatAXPY(self, -1, other)
    elif isinstance(other, (tuple, list)):
        alpha, mat = other
        _MatAXPY(self, -alpha, mat)
    elif isinstance(other, _VecType):
        diag = _petsc.VecDuplicate(other)
        _petsc.VecCopy(other, diag)
        _petsc.VecScale(diag, -1)
        _MatDiagAdd(self, diag)
        _petsc.VecDestroy(diag)
    else:
        _MatShift(self, -other)
    return self

def __imul__(self, other):
    if isinstance(other, (tuple, list)):
        L, R = other
        _petsc.MatDiagonalScale(self, L, R)
    else:    
        _MatScale(self, other)
    return self

def __idiv__(self, other):
    _MatScale(self, 1.0/other)
    return self



# binary operations

def __add__(self, other):
    return __iadd__(__pos__(self), other)

def __sub__(self, other):
    return __isub__(__pos__(self), other)

def __mul__(self, other):
    if isinstance(other, type(self)):
        return _MatMatMult(self, other)
    elif isinstance(other, _VecType):
        return _MatVecMult(self, other)
    else:
        return __imul__(__pos__(self), other)

def __div__(self, other):
    return __idiv__(__pos__(self), other)


# reflected binary operations

def __radd__(self, other):
    return __add__(self, other)

def __rsub__(self, other):
    mat = __sub__(self, other)
    _MatScale(mat, -1)
    return mat

def __rmul__(self, other):
    return __mul__(self, other)



# true division operations

def __truediv__(self, other):
    return __div__(self, other)

def __itruediv__(self, other):
    return __idiv__(self, other)

