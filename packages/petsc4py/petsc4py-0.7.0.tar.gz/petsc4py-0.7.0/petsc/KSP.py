# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
Linear Solvers - KSP
====================

The Scalable Linear Equations Solvers (KSP) component provides an
easy-to-use interface to the combination of a Krylov subspace
iterative method and a preconditioner (in the KSP and PC components,
respectively) or a sequential direct solver. KSP users can set various
Krylov subspace options at runtime via the options database. KSP users
can also set KSP options directly in application by directly calling
the KSP routines (e.g., 'KSP.setType()'). KSP components can be used
directly to create and destroy solvers; this is not needed for users
but is intended for library developers.
"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reST'

# --------------------------------------------------------------------

__all__ = ['KSP',
           'KSPCG',
           'KSPGMRES',
           
           'PC',
           'PCNone',
           'PCLU',
           'PCILU',
           'PCShell',
           ]

# --------------------------------------------------------------------

from petsc4py.lib import _petsc
from petsc4py.lib import _numpy

from petsc4py.Object import Object

# --------------------------------------------------------------------


class KSP(Object):

    """
    Abstract PETSc object that manages all Krylov methods.
    """
    
    class Type(object):
        """
        KSP Types
        """
        RICHARDSON = _petsc.KSPRICHARDSON
        CHEBYCHEV  = _petsc.KSPCHEBYCHEV
        CG         = _petsc.KSPCG
        CGNE       = _petsc.KSPCGNE
        STCG       = _petsc.KSPSTCG
        GMRES      = _petsc.KSPGMRES
        FGMRES     = _petsc.KSPFGMRES
        LGMRES     = _petsc.KSPLGMRES
        TCQMR      = _petsc.KSPTCQMR
        BCGS       = _petsc.KSPBCGS
        BCGSL      = _petsc.KSPBCGSL
        CGS        = _petsc.KSPCGS
        TFQMR      = _petsc.KSPTFQMR
        CR         = _petsc.KSPCR
        LSQR       = _petsc.KSPLSQR
        PREONLY    = _petsc.KSPPREONLY
        QCG        = _petsc.KSPQCG
        BICG       = _petsc.KSPBICG
        MINRES     = _petsc.KSPMINRES
        SYMMLQ     = _petsc.KSPSYMMLQ
        LCD        = _petsc.KSPLCD

        def __init__(self, ksp_type):
            self._ksp_type = ksp_type
        def __call__(self, name, bases, dct):
            klass = type(KSP)(name, bases, dct)
            setattr(klass, 'TYPE', self._ksp_type)
            def __init__(self, ksp=None, *targs, **kwargs):
                """See `KSP.create()` and KSP.setType()."""
                super(KSP, self).__init__(*targs, **kwargs)
                ksp_type = getattr(type(self), 'TYPE', None)
                if isinstance(ksp, KSP):
                    _petsc.KSP_init(self, ksp, ksp_type)
                else:
                    comm = ksp
                    _petsc.KSPCreate(comm, self)
                    if ksp_type is not None:
                        _petsc.KSPSetType(self, ksp_type)
            setattr(klass, '__init__', __init__)
            return klass

    class NormType:
        """
        Norm that is passed in the Krylov convergence test routines.
        """
        # native
        NO_NORM               = _petsc.KSP_NO_NORM
        PRECONDITIONED_NORM   = _petsc.KSP_PRECONDITIONED_NORM
        UNPRECONDITIONED_NORM = _petsc.KSP_UNPRECONDITIONED_NORM
        NATURAL_NORM          = _petsc.KSP_NATURAL_NORM
        # aliases
        NONE             = NO_NORM
        PRECONDITIONED   = PRECONDITIONED_NORM
        UNPRECONDITIONED = UNPRECONDITIONED_NORM
        NATURAL          = NATURAL_NORM

    class ConvergedReason:
        """
        Reason a Krylov method was said to have converged or diverged.

        + CONVERGED_ITERATING - this only occurs if
        `KSP.getConvergedReason()` is called during `KSP.solve()`

        """
        # converged
        CONVERGED_RTOL             = _petsc.KSP_CONVERGED_RTOL
        CONVERGED_ATOL             = _petsc.KSP_CONVERGED_ATOL
        CONVERGED_ITS              = _petsc.KSP_CONVERGED_ITS
        CONVERGED_STCG_NEG_CURVE   = _petsc.KSP_CONVERGED_STCG_NEG_CURVE
        CONVERGED_STCG_CONSTRAINED = _petsc.KSP_CONVERGED_STCG_CONSTRAINED
        CONVERGED_STEP_LENGTH      = _petsc.KSP_CONVERGED_STEP_LENGTH
        #iterating
        CONVERGED_ITERATING       = _petsc.KSP_CONVERGED_ITERATING
        ITERATING                 = _petsc.KSP_CONVERGED_ITERATING
        # diverged
        DIVERGED_NULL             = _petsc.KSP_DIVERGED_NULL
        DIVERGED_ITS              = _petsc.KSP_DIVERGED_ITS
        DIVERGED_DTOL             = _petsc.KSP_DIVERGED_DTOL
        DIVERGED_BREAKDOWN        = _petsc.KSP_DIVERGED_BREAKDOWN
        DIVERGED_BREAKDOWN_BICG   = _petsc.KSP_DIVERGED_BREAKDOWN_BICG
        DIVERGED_NONSYMMETRIC     = _petsc.KSP_DIVERGED_NONSYMMETRIC
        DIVERGED_INDEFINITE_PC    = _petsc.KSP_DIVERGED_INDEFINITE_PC
        DIVERGED_NAN              = _petsc.KSP_DIVERGED_NAN
        DIVERGED_INDEFINITE_MAT   = _petsc.KSP_DIVERGED_INDEFINITE_MAT

    class ConvergenceTest(object):
        """
        Interface class for KSP ConvergenceTest objects.
        """
        DEFAULT = _petsc.KSPDefaultConverged
        SKIP    = _petsc.KSPSkipConverged
        def __call__(self, ksp, its, rnorm):
            """Calls KSP.ConvergenceTest.DEFAULT"""
            return self.DEFAULT(ksp, its, rnorm)

    class Monitor(object):
        """
        Interface class for KSP Monitor objects.
        """
        DEFAULT            = _petsc.KSPMonitorDefault
        TRUE_RESIDUAL_NORM = _petsc.KSPMonitorTrueResidualNorm
        SOLUTION           = _petsc.KSPMonitorSolution
        def __call__(self, ksp, its, rnorm):
            """Calls  KSP.Monitor.DEFAULT"""
            self.DEFAULT(ksp, its, rnorm)

    def __init__(self, *targs, **kwargs):
        super(KSP, self).__init__(*targs, **kwargs)

    def __call__(self, b, x):
        """Same as `solve()`"""
        _petsc.KSPSolve(self, b, x)

    def create(self, comm=None):
        """
        Creates a default KSP context. The type can then be set with
        `setType()` (or perhaps `setFromOptions()`).

        .. note:: The default KSP type is GMRES with a restart of 30,
           using modified Gram-Schmidt orthogonalization.

        .. note:: The default preconditioner on one processor is ILU
           with 0 fill, on more than one it is BJACOBI with ILU on
           each processor.
        """
        return _petsc.KSPCreate(comm, self)

    def getPC(self):
        """
        Returns a the preconditioner context set with `setPC()`.
        """
        return _petsc.KSPGetPC(self)

    def setPC(self, pc, side=None):
        """
        Set the preconditioner context to be used to calculate the
        application of the preconditioner on a vector.
        """
        _petsc.KSPSetPC(self, pc)
        if side is not None:
            self.setPCSide(side)
    
    def getPCSide(self):
        """
        Get the preconditioning side.
        """
        return _petsc.KSPGetPreconditionerSide(self)

    def setPCSide(self, side):
        """
        Set the preconditioning side.
        """
        side = _petsc.get_attr(PC.Side, side)
        _petsc.KSPSetPreconditionerSide(self, side)

    getPreconditionerSide = getPCSide
    setPreconditionerSide = setPCSide
    
    def getOperators(self):
        """
         Get the matrix associated with the linear system and a
         (possibly) different one associated with the preconditioner.
        """
        return _petsc.KSPGetOperators(self)

    def setOperators(self, A=None, P=None, structure=None):
        """
        Set the matrix associated with the linear system and a
        (possibly) different one associated with the preconditioner.
        """
        structure = _petsc.get_attr(PC.Structure, structure)
        _petsc.KSPSetOperators(self, A, P, structure)

    def hasOperators(self):
        """
        Determines if the matrix associated with the linear system and
        possibly a different one associated with the preconditioner
        have been set in the KSP.
        """
        return _petsc.KSPGetOperatorsSet(self)
        
    def getNullSpace(self):
        """
        Get the null space of the operator
        """
        return _petsc.KSPGetNullSpace(self)

    def setNullSpace(self, nullspace):
        """
        Set the null space of the operator
        """
        _petsc.KSPSetNullSpace(self, nullspace)

    def setNormType(self, norm_type):
        """
        Set the norm that is used for convergence testing.
        """
        norm_type = _petsc.get_attr(KSP.NormType, norm_type)
        _petsc.KSPSetNormType(self, norm_type)
        
    def getTolerances(self):
        """
        Get the relative, absolute, divergence, and maximum iteration
        tolerances used by the default KSP convergence tests.

        :Returns:
           - `rtol`: the relative convergence tolerance.
           - `atol`: the absolute convergence tolerance.
           - `divtol`: the divergence tolerance.
           - `max_it`: maximum number of iterations.
        """
        return _petsc.KSPGetTolerances(self)

    def setTolerances(self, rtol=None, atol=None, divtol=None, max_it=None):
        """
        Set the relative, absolute, divergence, and maximum iteration
        tolerances used by the default KSP convergence testers.

        :Parameters:
           - `rtol` : the relative convergence tolerance (relative
              decrease in the residual norm)
           - `atol` : the absolute convergence tolerance (absolute
             size of the residual norm)
           - `divtol` : the divergence tolerance (amount residual can
             increase before KSPDefaultConverged() concludes that the
             method is diverging)
           - `max_it`: maximum number of iterations to use
        """
        tolerances = [rtol, atol, divtol, max_it]
        for i, tol in enumerate(tolerances):
            if tol is None:
                tolerances[i] = _petsc.PETSC_DEFAULT
        _petsc.KSPSetTolerances(self, *tolerances)
        
    def getInitialGuessNonzero(self):
        """
        Determines whether the KSP solver is using a zero initial
        guess.
        """
        return bool(_petsc.KSPGetInitialGuessNonzero(self))

    def setInitialGuessNonzero(self, flag):
        """
        Tells the iterative solver that the initial guess is nonzero;
        otherwise KSP assumes the initial guess is to be zero (and
        thus zeros it out before solving).
        """
        _petsc.KSPSetInitialGuessNonzero(self, flag)

    def getInitialGuessKnoll(self):
        """
        Determines whether the KSP solver is using the Knoll trick
        (using PC.apply()) to compute the initial guess.
        """
        return bool(_petsc.KSPGetInitialGuessKnoll(self))

    def setInitialGuessKnoll(self, flag):
        """
        Tells the iterative solver to use PC.apply() to compute the
        initial guess (The Knoll trick).
        """
        _petsc.KSPSetInitialGuessKnoll(self, flag)

    def getRhs(self):
        """
        Get the right-hand-side vector for the linear system to be
        solved.
        """
        return _petsc.KSPGetRhs(self)

    def getSolution(self):
        """
        Get the location of the solution for the linear system to be
        solved.  Note that this may not be where the solution is
        stored during the iterative process; see
        `KSP.buildSolution()`.
        """
        return _petsc.KSPGetSolution(self)

    def computeExplicitOperator(self):
        """
        Computes the explicit preconditioned operator.

        .. notes:: This computation is done by applying the operators
           to columns of the identity matrix.  Currently, this routine
           uses a dense matrix format when one processor is used and a
           sparse format otherwise.  This routine is costly in
           general, and is recommended for use only with relatively
           small systems.
        """
        return _petsc.KSPComputeExplicitOperator(self)

    def buildSolution(self, sol):
        """
        Builds the approximate solution in a vector provided.
        """
        _petsc.KSPBuildSolution(self, sol)

    def buildResidual(self, res):
        """
        Builds the residual in a vector provided.
        """
        _petsc.KSPBuildResidual(self, res)

    def getIterationNumber(self):
        """
        Get the current iteration number; if the KSP.solve() is
        complete, returns the number of iterations used.
        """
        return _petsc.KSPGetIterationNumber(self)

    def getConvergedReason(self):
        """
        Get the reason the KSP iteration was stopped.

        .. note:: negative value indicates diverged,
           positive value converged.
        """
        return _petsc.KSPGetConvergedReason(self)

    def getConvergedReasonString(self):
        """
        """
        reason = _petsc.KSPGetConvergedReason(self)
        return _petsc.KSPConvergedReasonString(reason)

    def setConvergenceTest(self, convtest):
        """
        Set the function to be used to determine convergence.
        """
        _petsc.KSPSetConvergenceTest(self, convtest)
    
    def getResidualNorm(self):
        """
        Get the last (approximate, preconditioned) residual norm that
        has been computed.
        """
        return _petsc.KSPGetResidualNorm(self)

    def logResidualHistory(self, n=None, reset=True):
        """
        """
        if n is None:
            n = _petsc.PETSC_DECIDE
        return _petsc.KSPLogResidualHistory(self, n, reset)

    def getResidualHistory(self):
        """
        """
        return _petsc.KSPGetResidualHistory(self)

    def setComputeEigenvalues(self, flag):
        """
        """
        _petsc.KSPSetComputeEigenvalues(self, flag)

    def computeEigenvalues(self, neig=None):
        """
        """
        maxit = _petsc.KSPGetTolerances(self)[3]
        if neig is None or neig > maxit:
            neig = maxit
        real = _numpy.empty(neig, _petsc.PetscReal)
        imag = _numpy.empty(neig, _petsc.PetscReal)
        neig = _petsc.KSPComputeEigenvalues(self, (real, imag))
        eigv = _numpy.empty(neig, _petsc.PetscComplex)
        eigv.real = real[0:neig]
        eigv.imag = imag[0:neig]
        return eigv

    def computeEigenvaluesExplicitly(self, neig=None):
        """
        """
        A, _, _ = _petsc.KSPGetOperators(self)
        M, _ = _petsc.MatGetSize(A)
        if neig is None or neig > M:
            neig = M
        real = _numpy.empty(neig, _petsc.PetscReal)
        imag = _numpy.empty(neig, _petsc.PetscReal)
        _petsc.KSPComputeEigenvaluesExplicitly(self, (real, imag))
        eigv = _numpy.empty(neig, _petsc.PetscComplex)
        eigv.real = real[0:neig]
        eigv.imag = imag[0:neig]
        return eigv

    def setComputeSingularValues(self, flag):
        """
        """
        _petsc.KSPSetComputeSingularValues(self, flag)

    def computeExtremeSingularValues(self):
        """
        """
        return tuple(_petsc.KSPComputeExtremeSingularValues(self))

    def setMonitor(self, monitor):
        """
        Set an additional function to be called at every iteration to
        monitor the residual/error etc.
        """
        _petsc.KSPMonitorSet(self, monitor)

    def cancelMonitor(self):
        """
        Clear all monitors for a KSP object.
        """
        _petsc.KSPMonitorCancel(self)

    clearMonitor = cancelMonitor

    def solve(self, b, x):
        """
        Solve linear system.
        """
        _petsc.KSPSolve(self, b, x)
        
    def solveTranspose(self, b, x):
        """
        Solve the transpose of a linear system.
        """
        _petsc.KSPSolveTranspose(self, b, x)
    
    pc     = property(getPC, setPC)
    pcside = property(getPCSide, setPCSide)

    nullspace = property(getNullSpace, setNullSpace)

    norm_type = property(None, setNormType,
                         doc='norm type for convergence testing')

    rhs      = property(getRhs)
    solution = property(getSolution)

    reltol = rtol   = property(*_petsc.tolerance('rtol',   0))
    abstol = atol   = property(*_petsc.tolerance('atol',   1))
    divtol = dtol   = property(*_petsc.tolerance('divtol', 2))
    max_it = maxit  = property(*_petsc.tolerance('max_it', 3))

    guess_nonzero  = property(getInitialGuessNonzero,
                              setInitialGuessNonzero)
    guess_knoll    = property(getInitialGuessKnoll,
                              setInitialGuessKnoll)

    eig = property(computeEigenvalues,
                   setComputeEigenvalues)
    esv = property(computeExtremeSingularValues,
                   setComputeSingularValues)

    iternum   = property(getIterationNumber)
    resnorm   = property(getResidualNorm)
    converged = property(getConvergedReason)
    convstr   = property(getConvergedReasonString)


# --------------------------------------------------------------------

class KSPPREONLY(KSP):
    """
    Implements a stub method that applies ONLY the preconditioner.
    """
    __metaclass__ = KSP.Type(KSP.Type.PREONLY)


class KSPCG(KSP):
    """
    Implements the Conjugate Gradients method.
    """
    __metaclass__ = KSP.Type(KSP.Type.CG)


class KSPGMRES(KSP):
    """
    Implements the Generalized Minimal Residual method.
    """
    __metaclass__ = KSP.Type(KSP.Type.GMRES)
            

# --------------------------------------------------------------------


class PC(Object):

    """
    Abstract PETSc object that manages all preconditioners.
    """

    class Type(object):
        """
        PC Types
        """
        NONE       = _petsc.PCNONE
        JACOBI     = _petsc.PCJACOBI
        SOR        = _petsc.PCSOR
        LU         = _petsc.PCLU
        SHELL      = _petsc.PCSHELL
        BJACOBI    = _petsc.PCBJACOBI
        MG         = _petsc.PCMG
        EISENSTAT  = _petsc.PCEISENSTAT
        ILU        = _petsc.PCILU
        ICC        = _petsc.PCICC
        ASM        = _petsc.PCASM
        KSP        = _petsc.PCKSP
        COMPOSITE  = _petsc.PCCOMPOSITE
        REDUNDANT  = _petsc.PCREDUNDANT
        SPAI       = _petsc.PCSPAI
        NN         = _petsc.PCNN
        CHOLESKY   = _petsc.PCCHOLESKY
        SAMG       = _petsc.PCSAMG
        PBJACOBI   = _petsc.PCPBJACOBI
        MAT        = _petsc.PCMAT
        HYPRE      = _petsc.PCHYPRE
        FIELDSPLIT = _petsc.PCFIELDSPLIT
        TFS        = _petsc.PCTFS
        ML         = _petsc.PCML
        PROMETHEUS = _petsc.PCPROMETHEUS
        GALERKIN   = _petsc.PCGALERKIN

        SCHUR      = _petsc.PCSCHUR

        def __init__(self, pc_type):
            self._pc_type = pc_type
        def __call__(self, name, bases, dct):
            klass = type(PC)(name, bases, dct)
            setattr(klass, 'TYPE', self._pc_type)
            def __init__(self, pc=None, *targs, **kwargs):
                """See `PC.create()` and PC.setType()."""
                super(PC, self).__init__(*targs, **kwargs)
                pc_type = getattr(type(self), 'TYPE', None)
                if isinstance(pc, PC):
                    _petsc.PC_init(self, pc, pc_type)
                else:
                    comm = pc
                    _petsc.PCCreate(comm, self)
                    if pc_type is not None:
                        _petsc.PCSetType(self, pc_type)
            setattr(klass, '__init__', __init__)
            return klass

    class Side:
        """
        PC sides
        """
        LEFT      = _petsc.PC_LEFT
        RIGHT     = _petsc.PC_RIGHT
        SYMMETRIC = _petsc.PC_SYMMETRIC
        # aliases
        L = LEFT
        R = RIGHT
        S = SYMMETRIC

    class Structure:
        """
        Indicates if the preconditioner has the same nonzero structure
        during successive linear solves.
        """
        # native
        SAME_NONZERO_PATTERN      = _petsc.SAME_NONZERO_PATTERN
        DIFFERENT_NONZERO_PATTERN = _petsc.DIFFERENT_NONZERO_PATTERN
        SUBSET_NONZERO_PATTERN    = _petsc.SUBSET_NONZERO_PATTERN
        SAME_PRECONDITIONER       = _petsc.SAME_PRECONDITIONER
        # aliases
        SAME      = SAME_NZ      = SAME_NONZERO_PATTERN
        SUBSET    = SUBSET_NZ    = SUBSET_NONZERO_PATTERN
        DIFFERENT = DIFFERENT_NZ = DIFFERENT_NONZERO_PATTERN
        SAMEPC    = SAME_PC      = SAME_PRECONDITIONER

    def __init__(self, *targs, **kwargs):
        super(PC, self).__init__(*targs, **kwargs)

    def __call__(self, x, y):
        """Same as `apply()`"""
        _petsc.PCApply(self, x, y)

    def create(self, comm=None):
        """
        Creates a preconditioner context.. The type can then be set with
        `setType()` (or perhaps `setFromOptions()`).

        .. notes:: The default preconditioner on one processor is ILU
           with 0 fill, on more than one it is BJACOBI with ILU() on
           each processor..
        """
        return _petsc.PCCreate(comm, self)

    def createShell(self, context=None, comm=None):
        """
        Creates a shell preconditioner context.

        :Parameters:
          - `context`: user-defined context object implementig the
             preconditioner interface.
          - `comm`: MPI communicator (defaults to `COMM_WORLD`).
        """
        return _petsc.PCCreateShell(comm, context, self)
        
    def getSubKSP(self):
        """
        Get subsolvers from a PC object.
        """
        return _petsc.PCGetSubKSP(self)

    def getOperators(self):
        """
         Get the matrix associated with the linear system and a
         (possibly) different one associated with the preconditioner.
        """
        return _petsc.PCGetOperators(self)

    def setOperators(self, A=None, P=None, structure=None):
        """
        Set the matrix associated with the linear system and a
        (possibly) different one associated with the preconditioner.
        """
        structure = _petsc.get_attr(PC.Structure, structure)
        _petsc.PCSetOperators(self, A, P, structure)

    def hasOperators(self):
        """
        Determines if the matrix associated with the linear system and
        possibly a different one associated with the preconditioner
        have been set in the PC.
        """
        return _petsc.PCGetOperatorsSet(self)

    def computeExplicitOperator(self):
        """
        Computes the explicit preconditioned operator.
        """
        return _petsc.PCComputeExplicitOperator(self)

    def setDiagonalScale(self, vec):
        """
        """
        _petsc.PCDiagonalScaleSet(self, vec)

    def diagonalScaleLeft(self, vec_in, vec_out):
        """
        """
        _petsc.PCDiagonalScaleLeft(self, vec_in, vec_out)

    def diagonalScaleRight(self, vec_in, vec_out):
        """
        """
        _petsc.PCDiagonalScaleRight(self, vec_in, vec_out)
        
    def apply(self, x, y):
        """
        Applies the preconditioner to a vector.
        """
        _petsc.PCApply(self, x, y)

    def applyTranspose(self, x, y):
        """
        Applies the transpose of preconditioner to a vector.
        """
        _petsc.PCApplyTranspose(self, x, y)

    # XXX this should go to subtypes
    
    def getFactoredMatrix(self):
        """
        Gets the factored matrix from the preconditioner context.

        ..note:: This routine is valid only for the LU, incomplete LU,
                 Cholesky, and incomplete Cholesky methods.
        """
        return _petsc.PCGetFactoredMatrix(self)

    def getShellContext(self):
        """
        Get the user-provided context object associated with a shell
        preconditioner.
        """
        return _petsc.PCShellGetContext(self)

    def setShellContext(self, context):
        """
        Set the user-provided context object associated with a shell
        preconditioner.
        """
        _petsc.PCShellSetContext(self, context)
    

# --------------------------------------------------------------------


class PCNone(PC):
    """
    This is used when you wish to employ a nonpreconditioned Krylov
    method.
    """
    __metaclass__ = PC.Type(PC.Type.NONE)

class PCLU(PC):
    """
    Use a direct solver, based on LU factorization, as a
    preconditioner.
    """
    __metaclass__ = PC.Type(PC.Type.LU)

class PCILU(PC):
    """
    Incomplete LU factorization preconditioner.
    """
    __metaclass__ = PC.Type(PC.Type.ILU)

class PCCHOLESKY(PC):
    """
    Use a direct solver, based on Cholesky factorization, as a
    preconditioner.
    """
    __metaclass__ = PC.Type(PC.Type.CHOLESKY)

class PCICC(PC):
    """
    Incomplete Cholesky factorization preconditioner.
    """
    __metaclass__ = PC.Type(PC.Type.ICC)

class PCShell(PC):
    """
    A PC type to be used to define your own preconditioning
    operator.
    """
    __metaclass__ = PC.Type(PC.Type.SHELL)
            
    def getContext(self):
        """
        Get the user-provided context object associated with a shell
        preconditioner.
        """
        return _petsc.PCShellGetContext(self)

    def setContext(self, context):
        """
        Set the user-provided context object associated with a shell
        preconditioner.
        """
        _petsc.PCShellSetContext(self, context)

    def getName(self):
        """
        Get an optional name that the user has set for a shell
        preconditioner.
        """
        return _petsc.PCShellGetName(self)

    def setName(self, name):
        """
        Set an optional name to associate with a shell
        preconditioner.
        """
        _petsc.PCShellSetName(self, name)


# --------------------------------------------------------------------
