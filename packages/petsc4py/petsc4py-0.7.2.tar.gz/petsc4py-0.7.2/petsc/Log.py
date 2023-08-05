# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
Logging Facilities
==================

"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reStructuredText'

# --------------------------------------------------------------------

__all__ = ['Log']


# --------------------------------------------------------------------

from petsc4py.lib import _petsc

# --------------------------------------------------------------------

class Log(object):

    """
    PETSc Logging.
    """
    
    @staticmethod
    def begin(all=False):
        """
        """
        if all:
            _petsc.PetscLogAllBegin()
        else:
            _petsc.PetscLogBegin()

    @staticmethod
    def logActions(flag):
        """
        """
        _petsc.PetscLogActions(flag)

    @staticmethod
    def logObjects(flag):
        """
        """
        _petsc.PetscLogObjects(flag)
    
    @staticmethod
    def printSummary(filename='stdout', comm=None):
        """
        """
        if filename is None:
            return
        _petsc.PetscLogPrintSummary(comm, filename)

    # Stages
    # ------
    
    @staticmethod
    def stageRegister(name):
        """
        """
        return _petsc.PetscLogStageRegister(name)

    @staticmethod
    def stageSetVisible(stage, flag):
        """
        """
        _petsc.PetscLogStageSetVisible(stage, flag)

    @staticmethod
    def stageSetActive(stage, flag):
        """
        """
        _petsc.PetscLogStageSetActive(stage, flag)

    @staticmethod
    def stageActivate(stage):
        """
        """
        _petsc.PetscLogStageSetActive(stage, True)

    @staticmethod
    def stageDeactivate(stage):
        """
        """
        _petsc.PetscLogStageSetActive(stage, False)

    @staticmethod
    def stagePush(stage):
        """
        """
        _petsc.PetscLogStagePush(stage)

    @staticmethod
    def stagePop():
        """
        """
        _petsc.PetscLogStagePop()

    # Classes
    # -------
    
    @staticmethod
    def classRegister(name):
        """
        """
        return _petsc.PetscLogClassRegister(name)

    @staticmethod
    def classSetActive(cookie, flag):
        """
        """
        if flag:
            _petsc.PetscLogEventActivateClass(cookie)
        else:
            _petsc.PetscLogEventDeactivateClass(cookie)

    @staticmethod
    def classActivate(cookie):
        """
        """
        _petsc.PetscLogEventActivateClass(cookie)

    @staticmethod
    def classDeactivate(cookie):
        """
        """
        _petsc.PetscLogEventDeactivateClass(cookie)

    # Events
    # ------
    
    @staticmethod
    def eventRegister(name, cookie=None):
        """
        """
        if cookie is None:
            return _petsc.PetscLogEventRegister(name)
        else:
            return _petsc.PetscLogEventRegister(name, cookie)

    @staticmethod
    def eventSetActive(event, flag):
        """
        """
        if flag:
            _petsc.PetscLogEventActivate(event)
        else:
            _petsc.PetscLogEventDeactivate(event)

    @staticmethod
    def eventActivate(event):
        """
        """
        _petsc.PetscLogEventActivate(event)

    @staticmethod
    def eventDeactivate(event):
        """
        """
        _petsc.PetscLogEventDeactivate(event)

    @staticmethod
    def eventBegin(event, *objs):
        """
        """
        _petsc.PetscLogEventBegin(event, *objs[:4])

    @staticmethod
    def eventEnd(event, *objs):
        """
        """
        _petsc.PetscLogEventEnd(event, *objs[:4])

    # Flops
    # -----
    
    @staticmethod
    def logFlops(flops):
        """
        """
        _petsc.PetscLogFlops(flops)

    # Time
    # ----
    
    @staticmethod
    def getTime():
        """
        """
        return _petsc.PetscGetTime()

    @staticmethod
    def getCPUTime():
        """
        """
        return _petsc.PetscGetCPUTime()

# --------------------------------------------------------------------
