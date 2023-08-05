# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
Time-steppers - ODE integrators - TS
====================================

The time-stepping components provide ODE integrators and
pseudo-timestepping. `TS` internally employs KSP/SNES to solve the
linear/nonlinear problems at each time step.
"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reST'

# --------------------------------------------------------------------

__all__ = ['TS']

# --------------------------------------------------------------------

from petsc4py.lib import _petsc

from petsc4py.Object import Object

# --------------------------------------------------------------------

class TS(Object):

    """
    Abstract PETSc object that manages all time-steppers (ODE
    integrators).
    """

    class ProblemType:
        """
        Determines the type of problem a TS object is to be used to
        solve.
        """
        LINEAR    = _petsc.TS_LINEAR
        NONLINEAR = _petsc.TS_NONLINEAR

    class Type:
        """
        TS types
        """
        EULER           = _petsc.TS_EULER
        BEULER          = _petsc.TS_BEULER
        PSEUDO          = _petsc.TS_PSEUDO
        CRANK_NICHOLSON = _petsc.TS_CRANK_NICHOLSON
        SUNDIALS        = _petsc.TS_SUNDIALS
        RUNGE_KUTTA     = _petsc.TS_RUNGE_KUTTA
        # alias
        CN = CRANK_NICHOLSON
        RK = RUNGE_KUTTA
        # contrib
        USER            = _petsc.TS_USER
        
    class Monitor(object):
        """
        Interface class for Monitor objects
        """
        DEFAULT = _petsc.TSMonitorDefault
        SOLUTION = _petsc.TSMonitorSolution
        def __call__(self, ts, step, time, u):
            """
            Calls TS.Monitor object
            """
            self.DEFAULT(ts, step, time, u)

    def __init__(self, *targs, **kwargs):
        super(TS, self).__init__(*targs, **kwargs)

    def __call__(self, u=None):
        """Same as `solve()`"""
        _petsc.TSSolve(self, u)

    def create(self, comm=None):
        """
        Creates an empty timestepper. The problem type can be set with
        `setProblemType()` and the type of solver can then be set with
        `setType()`.
        """
        return _petsc.TSCreate(comm, self)

    def getProblemType(self):
        """
        Gets the type of problem to be solved.
        """
        return _petsc.TSGetProblemType(self)

    def setProblemType(self, problem_type):
        """
        Sets the type of problem to be solved.
        """
        problem_type = _petsc.get_attr(TS.ProblemType, problem_type)
        _petsc.TSSetProblemType(self, problem_type)

    def getApplicationContext(self):
        """
        Gets the user-defined context for the timestepper.
        """
        return _petsc.TSGetApplicationContext(self)

    def setApplicationContext(self, context):
        """
        Sets an optional user-defined context for the timestepper.
        """
        _petsc.TSSetApplicationContext(self, context)

    def getKSP(self):
        """
        Returns the KSP (linear solver) associated with a TS
        (timestepper) object.

        .. note::
           Valid only for linear problems.

        .. note::
           The user can directly manipulate the KSP object to
           set various options, etc.  Likewise, the user can then extract
           and manipulate the PC object as well.
        """
        return _petsc.TSGetKSP(self)

    def setRHSMatrix(self, function, A, P=None):
        """
        Sets the function to compute the matrix A, where U_t = A(t) U.
        Also sets the location to store the matrix.
        """
        _petsc.TSSetRHSMatrix(self, A, P, function)

    def setLHSMatrix(self, function, A, P=None):
        """
        Sets the function to compute the matrix A, where A U_t = F(U).
        Also sets the location to store the matrix.
        """
        _petsc.TSSetLHSMatrix(self, A, P, function)

    def getSNES(self):
        """
        Returns the SNES (nonlinear solver) associated with a
        TS (timestepper) object.

        .. note::
           Valid only for nonlinear problems.

        .. note::
           The user can directly manipulate the SNES object to
           set various options, etc.  Likewise, the user can then
           extract and manipulate the KSP, and then PC objects as well.
        """
        return _petsc.TSGetSNES(self)

    def setRHSFunction(self, function):
        """
        Sets the routine for evaluating the function,
        F(t,u), where U_t = F(t,u).

        .. note::
           The calling convention for `function` is::
             function(TS ts, float time, Vec u, Vec F ) -> None
        """
        _petsc.TSSetRHSFunction(self, function)

    def computeRHSFunction(self, time, x, y):
        """
        Evaluates the right-hand-side function.
        """
        _petsc.TSComputeRHSFunction(self, time, x, y)

    setFunction     = setRHSFunction
    computeFunction = computeRHSFunction

    def getRHSJacobian(self):
        """
        Returns the Jacobian matrix at the present timestep.
        """
        return tuple(_petsc.TSGetRHSJacobian(self))

    def setRHSJacobian(self, jacobian, J, P=None):
        """
        Sets the function to compute the Jacobian of F, where U_t =
        F(U,t), as well as the location to store the Jacobian matrix.

        .. note::
           The calling convention for `jacobian` is::
             jacobian(TS ts, float time, Vec u, Mat J, Mat P) -> None
        """
        _petsc.TSSetRHSJacobian(self, J, P, jacobian)

    def computeRHSJacobian(self, time, x, J, P):
        """
        Evaluates the right-hand-side Jacobian.
        """
        _petsc.TSComputeRHSJacobian(self, time, x, J, P)

    getJacobian     = getRHSJacobian
    setJacobian     = setRHSJacobian
    computeJacobian = computeRHSJacobian

    def getTime(self):
        """
        Gets the current time.
        """
        return _petsc.TSGetTime(self)

    def setTime(self, time):
        """
        Sets the current time to be used.
        """
        _petsc.TSSetTime(self, time)

    def getTimeStep(self):
        """
        Gets the current timestep size.
        """
        return _petsc.TSGetTimeStep(self)

    def setTimeStep(self, time_step):
        """
        Allows the user to reset the timestep at any time,
        """
        _petsc.TSSetTimeStep(self, time_step)

    def setInitialTimeStep(self, initial_time, initial_time_step):
        """
        Sets the initial timestep to be used, as well as the initial time.
        """
        _petsc.TSSetInitialTimeStep(self, initial_time, initial_time_step)
    
    def getStepNumber(self):
        """
        Gets the current timestep number.
        """
        return _petsc.TSGetTimeStepNumber(self)

    getTimeStepNumber = getStepNumber

    def getMaxTime(self):
        """
        Gets the maximum time to use for iteration.
        """
        _, max_time = _petsc.TSGetDuration(self)
        return max_time

    def setMaxTime(self, max_time):
        """
        Sets the maximum time to use for iteration.
        """
        max_steps, _ = _petsc.TSGetDuration(self)
        _petsc.TSSetDuration(self, max_steps, max_time)

    def getMaxSteps(self):
        """
        Gets the maximum number of timesteps to use for iteration.
        """
        max_steps, _ = _petsc.TSGetDuration(self)
        return max_steps

    def setMaxSteps(self, max_steps):
        """
        Sets the maximum number of timesteps to use for iteration.
        """
        _, max_time = _petsc.TSGetDuration(self)
        _petsc.TSSetDuration(self, max_steps, max_time)
        
    def getDuration(self):
        """
        Gets the maximum time and maximum number of timesteps to use
        for iteration.
        """
        max_steps, max_time = _petsc.TSGetDuration(self)
        return (max_time, max_steps)

    def setDuration(self, max_time, max_steps=None):
        """
        Sets the maximum time and optionally the maximum number of
        timesteps to use for iteration.
        """
        _max_steps, _max_time = _petsc.TSGetDuration(self)
        if max_time is None:
            max_time = _max_time
        if max_steps is None:
            max_steps = _max_steps
        _petsc.TSSetDuration(self, max_steps, max_time)

    def getSolution(self):
        """
        Returns the solution at the present timestep. It is valid to
        call this routine inside the function that you are evaluating
        in order to move to the new timestep. This vector does not
        change until the solution at the next timestep has been
        calculated.
        """
        return _petsc.TSGetSolution(self)

    def setSolution(self, u):
        """
        Sets the initial solution vector.
        """
        _petsc.TSSetSolution(self, u)

    def setMonitor(self, monitor):
        """
        Sets an additional function that is to be used at every
        timestep to display the iteration's progress.

        .. note::
           The calling convention for `monitor` is::
             monitor(TS ts, int step, float time, Vec u) -> None
        
        .. note::
           There is no way to remove a single, specific monitor.
        """
        _petsc.TSMonitorSet(self, monitor)

    def cancelMonitor(self):
        """
        Clears all the monitors that have been set on a timestepper.

        .. note::
           There is no way to remove a single, specific monitor.
        """
        _petsc.TSMonitorCancel(self)

    clearMonitor = cancelMonitor

    def setPreStep(self, prestep):
        """
        Sets the general-purpose function called once at the beginning
        of time stepping.

        .. note::
           The calling convention for `prestep` is::
             prestep(TS ts) -> None
        """
        _petsc.TSSetPreStep(self, prestep)

    def setUpdate(self, update):
        """
        Sets the general-purpose update function called at the
        beginning of every time step. This function can change the
        time step returning a float value.

        .. note::
           The calling convention for `update` is::
             update(TS ts, float time, float time_step) -> None | time_step
        """
        _petsc.TSSetUpdate(self, update)

    def setPostStep(self, poststep):
        """
        Sets the general-purpose function called once at the end of
        time stepping.

        .. note::
           The calling convention for `poststep` is::
             poststep(TS ts) -> None
        """
        _petsc.TSSetPostStep(self, poststep)

    def step(self):
        """
        Steps the requested number of timesteps.

        :Return:
          - number of iterations until termination.
          - time until termination.
        """
        return tuple(_petsc.TSStep(self))

    def solve(self, u=None):
        """
        Steps the requested number of timesteps, using a solution
        vector if provided.

        :Parameters:
          - `u`: solution vector (optional).

        .. note::
           The user should initialize the provided vector with the
           initial solution prior to calling `solve()`. In particular,
           to employ an initial solution of zero, the user should
           explicitly set this vector to zero.
        """
        _petsc.TSSolve(self, u)

   
    problem_type = property(getProblemType, setProblemType)

    appctx   = property(getApplicationContext, setApplicationContext)
    
    ksp      = property(getKSP)
    snes     = property(getSNES)
    solution = property(getSolution, setSolution)

    time        = property(getTime, setTime)
    time_step   = property(getTimeStep, setTimeStep)
    step_number = property(getStepNumber)
    max_time    = property(getMaxTime,  setMaxTime)
    max_steps   = property(getMaxSteps, setMaxSteps)
