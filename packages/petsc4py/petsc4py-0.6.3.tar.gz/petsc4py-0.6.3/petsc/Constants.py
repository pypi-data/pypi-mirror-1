# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
PETSc Constants
===============

"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reST'

# --------------------------------------------------------------------

__all__ = ['Int', 'Scalar', 'Real', 'Complex',
           'DECIDE', 'DEFAULT', 'DETERMINE',           
           'Truth', 'InsertMode', 'ScatterMode', 'NormType']

# --------------------------------------------------------------------

from petsc4py.lib import _petsc

# --------------------------------------------------------------------

Int = _petsc.PetscInt
"""Integer numeric type"""
      
Scalar = _petsc.PetscScalar
"""Scalar numeric type"""

Real = _petsc.PetscReal
"""Real numeric type"""

Complex = _petsc.PetscComplex
"""Complex numeric type"""

# --------------------------------------------------------------------

DECIDE    = _petsc.PETSC_DECIDE
DEFAULT   = _petsc.PETSC_DEFAULT
DETERMINE = _petsc.PETSC_DETERMINE
"""PETSc constants for default arguments. Standard way of passing in
integer or floating point parameter where you wish PETSc to use the
default."""

# --------------------------------------------------------------------

class Truth:
    """
    Truth values.
    """
    FALSE = _petsc.PETSC_FALSE
    TRUE  = _petsc.PETSC_TRUE
    YES   = _petsc.PETSC_YES
    NO    = _petsc.PETSC_NO


class InsertMode:
    """
    Insertion modes for setting values in vectors and matrices.

    - `INSERT_VALUES`: Puts a value into a vector or matrix,
      overwrites any previous value.

    - `ADD_VALUES`: Adds a value into a vector or matrix, if there
      previously was no value, just puts the value into that location.

    - `MAX_VALUES`: Puts the maximum of the scattered/gathered values
      and the current value into each location.
    """
    # native
    NOT_SET_VALUES = _petsc.NOT_SET_VALUES
    INSERT_VALUES  = _petsc.INSERT_VALUES
    ADD_VALUES     = _petsc.ADD_VALUES
    MAX_VALUES     = _petsc.MAX_VALUES
    # aliases
    INSERT  = INSERT_VALUES
    INS     = INSERT_VALUES
    ADD     = ADD_VALUES
    MAX     = MAX_VALUES


class ScatterMode:
    """
    Scatter directions for vector scatters and gosthed vectors.

    - `FORWARD`: Scatters the values as dictated by the call to
      `Scatter.Create()`.

    - `REVERSE`: Moves the values in the opposite direction than the
      ones indicated in the call to `Scatter.Create()`.
    """
    # native
    SCATTER_FORWARD = _petsc.SCATTER_FORWARD
    SCATTER_REVERSE = _petsc.SCATTER_REVERSE
    # aliases
    FORWARD = SCATTER_FORWARD
    REVERSE = SCATTER_REVERSE


class NormType:
    """
    Norm types for vectors and matrices.

    - `NORM_1`: the one norm
      + ||v|| = sum_i | v_i | for vectors.
      + ||A|| = max_j || v_*j|| for matrices (maximum column sum).

    - `NORM_2`: the two norm
      + ||v|| = sqrt(sum_i (v_i)^2) for vectors.
      + not supported for matrices.
                
    - `NORM_FROBENIUS`: the Frobenius norm
      + same as `NORM_2` for vectors.
      + ||A|| = sqrt(sum_ij (A_ij)^2) for matrices.

    - `NORM_INFINITY`: the infinity norm
      + ||v|| = max_i |v_i| for vectors.
      + ||A|| = max_i || v_i* || for matrices (maximum row sum).

    - `NORM_MAX`: same as `NORM_INFINITY`.
    """
    # native
    NORM_1         = _petsc.NORM_1
    NORM_2         = _petsc.NORM_2
    NORM_1_AND_2   = _petsc.NORM_1_AND_2
    NORM_FROBENIUS = _petsc.NORM_FROBENIUS
    NORM_INFINITY  = _petsc.NORM_INFINITY
    NORM_MAX       = _petsc.NORM_MAX
    # aliases
    N1        = NORM_1
    N2        = NORM_2
    N12       = NORM_1_AND_2
    MAX       = NORM_MAX
    FROBENIUS = NORM_FROBENIUS
    INFINITY  = NORM_INFINITY
    # more aliases
    FRB = FROBENIUS
    INF = INFINITY
    

# --------------------------------------------------------------------

