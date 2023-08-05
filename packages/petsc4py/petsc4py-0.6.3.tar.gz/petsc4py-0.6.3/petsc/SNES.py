# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
Nonlinear Solvers - SNES
========================

The Scalable Nonlinear Equations Solvers (SNES) component provides an
easy-to-use interface to Newton-based methods for solving systems of
nonlinear equations. SNES users can set various algorithmic options at
runtime via the options database. SNES internally employs KSP for the
solution of its linear systems. SNES users can also set KSP options
directly in application codes by first extracting the KSP context from
the SNES context via 'SNES.getKSP()' and then directly calling various
KSP (and KSP and PC) routines (e.g., 'PC.setType()').

"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reST'

# --------------------------------------------------------------------

__all__ = ['SNES']

# --------------------------------------------------------------------

from petsc4py.lib import _petsc

from petsc4py.Object import Object

# --------------------------------------------------------------------


class SNES(Object):

    """
    Abstract PETSc object that manages all nonlinear solves.
    """

    class Type:
        """
        SNES Types

        - `LS`: truncated Newton method with a line search,
        
        - `TR`: Newton based nonlinear solver that uses a trust region.
        """
        # native
        LS   = _petsc.SNESLS
        TR   = _petsc.SNESTR
        TEST = _petsc.SNESTEST
        # aliases
        LINE_SEARCH  = LS
        TRUST_REGION = TR

    class ConvergedReason:
        """
        Reason a SNES method was said to have converged or diverged

        + CONVERGED_FNORM_ABS - 2-norm(F) <= abstol

        + CONVERGED_FNORM_RELATIVE - 2-norm(F) <= rtol*2-norm(F(x_0)) where x_0
          is the initial guess

        + CONVERGED_PNORM_RELATIVE - The 2-norm of the last step <= xtol *
          2-norm(x) where x is the current solution and xtol is the
          4th argument to `SNES.setTolerances()`

        + DIVERGED_FUNCTION_COUNT - The user provided function has
          been called more times then the final argument to
          `SNES.setTolerances()`

        + DIVERGED_FNORM_NAN - the 2-norm of the current function
          evaluation is not-a-number (NaN), this is usually caused by
          a division of 0 by 0.

        + DIVERGED_MAX_IT - SNES.solve() has reached the maximum number
          of iterations requested

        + DIVERGED_LS_FAILURE - The line search has failed. This only
          occurs for a `SNES.Type` of SNESLS

        + DIVERGED_LOCAL_MIN - the algorithm seems to have stagnated
          at a local minimum that is not zero

        + CONVERGED_ITERATING - this only occurs if
          `SNES.getConvergedReason()` is called during the
          `SNES.solve()`
        """
        # converged
        CONVERGED_FNORM_ABS      = _petsc.SNES_CONVERGED_FNORM_ABS
        CONVERGED_FNORM_RELATIVE = _petsc.SNES_CONVERGED_FNORM_RELATIVE
        CONVERGED_PNORM_RELATIVE = _petsc.SNES_CONVERGED_PNORM_RELATIVE
        CONVERGED_TR_DELTA       = _petsc.SNES_CONVERGED_TR_DELTA
        # iterating
        CONVERGED_ITERATING      = _petsc.SNES_CONVERGED_ITERATING
        ITERATING                = _petsc.SNES_CONVERGED_ITERATING
        # diverged
        DIVERGED_FUNCTION_DOMAIN = _petsc.SNES_DIVERGED_FUNCTION_DOMAIN
        DIVERGED_FUNCTION_COUNT  = _petsc.SNES_DIVERGED_FUNCTION_COUNT
        DIVERGED_FNORM_NAN       = _petsc.SNES_DIVERGED_FNORM_NAN
        DIVERGED_MAX_IT          = _petsc.SNES_DIVERGED_MAX_IT
        DIVERGED_LS_FAILURE      = _petsc.SNES_DIVERGED_LS_FAILURE
        DIVERGED_LOCAL_MIN       = _petsc.SNES_DIVERGED_LOCAL_MIN

    class ConvergenceTest(object):
        """
        Interface class for SNES ConvergenceTest objects
        """
        DEFAULT = _petsc.SNESDefaultConvergenceTest
        def __call__(self, snes, its, xnorm, gnorm, fnorm):
            """Calls SNES.ConvergenceTest.DEFAULT"""
            return self.DEFAULT(snes, its, xnorm, gnorm, fnorm)
        
    class Monitor(object):
        """
        Interface class for SNES Monitor objects
        """
        DEFAULT         = _petsc.SNESMonitorDefault
        SOLUTION        = _petsc.SNESMonitorSolution
        RESIDUAL        = _petsc.SNESMonitorResidual
        SOLUTION_UPDATE = _petsc.SNESMonitorSolutionUpdate
        def __call__(self, snes, its, fnorm):
            """Calls SNES.Monitor.DEFAULT"""
            self.DEFAULT(snes, its, fnorm)

    def __init__(self, *targs, **kwargs):
        super(SNES, self).__init__(*targs, **kwargs)

    def __call__(self, x=None, b=None):
        """Same as `solve()`"""
        _petsc.SNESSolve(self, b, x)

    def create(self, comm=None):
        """
        Creates a nonlinear solver context. The type can then be set
        with `setType()` (or perhaps `setFromOptions()`).
        """
        return _petsc.SNESCreate(comm, self)

    def getApplicationContext(self):
        """
        Get the user-defined context for the nonlinear solvers.
        """
        return _petsc.SNESGetApplicationContext(self)

    def setApplicationContext(self, context):
        """
        Set the user-defined context for the nonlinear solvers.
        """
        _petsc.SNESSetApplicationContext(self, context)

    def setUpdate(self, update):
        """
        Set a general-purpose update function called at the beginning
        of every iteration of the nonlinear solve. Specifically it is
        called just before the Jacobian is evaluated.
   
        Signature for `update`::

          def Update(snes, iter):
              # <function code>
              return None
        """
        _petsc.SNESSetUpdate(self, update)

    def getFunction(self):
        """
        Returns the vector where the function is stored.
        """
        return _petsc.SNESGetFunction(self)

    def setFunction(self, function, f):
        """
        Set the function evaluation routine and function vector for
        use by the SNES routines in solving systems of nonlinear
        equations.
   
        Signature for `function`::

          def Function(snes, x, f):
              # <function code>
              return None
        """
        _petsc.SNESSetFunction(self, f, function)

    def getJacobian(self):
        """
        Returns the Jacobian matrix.
        """
        return tuple(_petsc.SNESGetJacobian(self))

    def setJacobian(self, jacobian, A, P=None):
        """
        Set the function to compute Jacobian as well as the location
        to store the matrix.

        Signature for of `jacobian`::
        
          def Jacobian(snes, x, J, P):
              # <jacobian code>
              return Mat.Structure.[SAME|DIFFERENT]_NONZERO_PATTERN
        """
        _petsc.SNESSetJacobian(self, A, P, jacobian)

    def getKSP(self):
        """
        Get the KSP context for a SNES solver.
        """
        return _petsc.SNESGetKSP(self)

    def setKSP(self, ksp):
        """
        Set the KSP context for a SNES solver.
        """
        return _petsc.SNESSetKSP(self, ksp)

    
    def computeFunction(self, x, y):
        """
        """
        _petsc.SNESComputeFunction(self, x, y)
        
    def computeJacobian(self, x, J, P=None):
        """
        """
        if P is None:
            P = J
        return _petsc.SNESComputeJacobian(self, x, J, P)

    def getRhs(self):
        """
        Get the vector for solving F(x) = rhs. If rhs is not set it
        assumes a zero right hand side.
        """
        return _petsc.SNESGetRhs(self)

    def setRhs(self, rhs):
        """
        Set the vector for solving F(x) = rhs. If rhs is not set it
        assumes a zero right hand side.
        """
        _petsc.SNESSetRhs(self, rhs)

    def getSolution(self):
        """
        Get the vector where the approximate solution is stored.
        """
        return _petsc.SNESGetSolution(self)

    def setSolution(self, x):
        """
        Set the vector where the approximate solution is stored.
        """
        _petsc.SNESSetSolution(self, x)

    def getSolutionUpdate(self):
        """
        Get the vector where the solution update is stored.
        """
        return _petsc.SNESGetSolutionUpdate(self)

    def getTolerances(self):
        """
        Get various parameters used in convergence tests.
        """
        return _petsc.SNESGetTolerances(self)

    def setTolerances(self,
                      atol=None, rtol=None, stol=None,
                      max_it=None, max_funcs=None):
        """
        Set various parameters used in convergence tests.
        """
        tolerances = [atol, rtol, stol, max_it, max_funcs]
        for i, tol in enumerate(tolerances):
            if tol is None:
                tolerances[i] = _petsc.PETSC_DEFAULT
        _petsc.SNESSetTolerances(self, *tolerances)
        
    def setTrustRegionTolerance(self, tol):
        """
        Set the trust region parameter tolerance.
        """
        _petsc.SNESSetTrustRegionTolerance(self, tol)
        
    def setMonitor(self, monitor):
        """
        """
        _petsc.SNESMonitorSet(self, monitor)

    def cancelMonitor(self):
        """
        """
        _petsc.SNESMonitorCancel(self)

    clearMonitor = cancelMonitor


    def setConvergenceTest(self, convtest):
        """
        """
        _petsc.SNESSetConvergenceTest(self, convtest)


    def solve(self, x=None, b=None):
        """
        Solves a nonlinear system F(x) = b.
        """
        _petsc.SNESSolve(self, b, x)

    def getConvergedReason(self):
        """
        """
        return _petsc.SNESGetConvergedReason(self)

    def getConvergedReasonString(self):
        """
        """
        reason = _petsc.SNESGetConvergedReason(self)
        return _petsc.SNESConvergedReasonString(reason)

    def logConvergenceHistory(self, n=None, reset=True):
        """
        """
        if n is None:
            n = _petsc.PETSC_DECIDE
        return _petsc.SNESLogConvergenceHistory(self, n, reset)

    def getConvergenceHistory(self):
        """
        """
        return _petsc.SNESGetConvergenceHistory(self)

    def getIterationNumber(self):
        """
        """
        return _petsc.SNESGetIterationNumber(self)

    def getFunctionNorm(self):
        """
        """
        return _petsc.SNESGetFunctionNorm(self)

    def getNumberLinearIterations(self):
        """
        """
        return _petsc.SNESGetNumberLinearIterations(self)

    def getNumberUnsuccessfulSteps(self):
        """
        """
        return _petsc.SNESGetNumberUnsuccessfulSteps(self)

    def setMaximumUnsuccessfulSteps(self, max_fails):
        """
        """
        _petsc.SNESSetMaximumUnsuccessfulSteps(self, max_fails)

    appctx   = property(getApplicationContext, setApplicationContext)
    
    ksp      = property(getKSP, setKSP)
    rsh      = property(getRhs, setRhs)
    solution = property(getSolution, setSolution)

    abstol    = atol  = property(*_petsc.tolerance('atol',      0))
    reltol    = rtol  = property(*_petsc.tolerance('rtol',      1))
    soltol    = stol  = property(*_petsc.tolerance('stol',      2))
    max_it    = maxit = property(*_petsc.tolerance('max_it',    3))
    max_funcs = maxf  = property(*_petsc.tolerance('max_funcs', 4))
    max_fails = property(getNumberUnsuccessfulSteps,
                         setMaximumUnsuccessfulSteps)

    iternum    = property(getIterationNumber)
    linear_its = property(getNumberLinearIterations)
    funcnorm   = property(getFunctionNorm)
    converged  = property(getConvergedReason)
    convstr    = property(getConvergedReasonString)
    

# --------------------------------------------------------------------
