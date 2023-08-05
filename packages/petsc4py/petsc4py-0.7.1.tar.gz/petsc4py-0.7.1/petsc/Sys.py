# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
System Routines
===============

PETSc initialization and finalization, input/output, utility
routines, etc.

"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reStructuredText'

# --------------------------------------------------------------------

__all__ = ['Sys',

           'Initialize',
           'Finalize',
           'IsInitialized',
           'IsFinalized',

           'GetVersion',

           'SetStdout',
           'Print',
           'Write',
           'SyncPrint', 'SynchronizedPrint',
           'SyncWrite', 'SynchronizedWrite',
           'SyncFlush', 'SynchronizedFlush',

           'SplitOwnership',
           'SeqPhase',

           'Sleep',
           ]


# --------------------------------------------------------------------

from petsc4py.lib import _petsc

# --------------------------------------------------------------------


def Initialize():
    """
    Initializes PETSc.

    .. note:: PETSc initialization is automatically done when PETSc
       module is imported.
    """
    if _petsc.PetscInitialized():
        return
    if _petsc.PetscFinalized():
        raise RuntimeError('PETSc has finalized')
    _petsc.PetscInitialize()


def Finalize():
    """
    Finalizes PETSc.

    .. note:: PETSc finalization is automatically registered using
       `atexit` module.
    """
    if _petsc.PetscFinalized():
        return
    if not _petsc.PetscInitialized():
        raise RuntimeError('PETSc has not initialized')
    _petsc.PetscFinalize()


def IsInitialized():
    """
    Checks if `Initialize()` has been called.
    """
    return bool(_petsc.PetscInitialized())


def IsFinalized():
    """
    Checks if `Finalize()` has been called.
    """
    return bool(_petsc.PetscFinalized())


# --------------------------------------------------------------------

def GetVersion(patch=False, date=False, author=False):
    """
    PETSc version information.
    """
    _data = _petsc.PetscGetVersion()
    _version = tuple(_data[0:3])
    out = _version
    if patch or date or author:
        out = [_version]
        if patch:
            _patch = _data[3]
            out.append(_patch)
        if date:
            if patch:
                _date = [_data[4], _data[5]]
            else:
                _date = _data[4]
            out.append(_date)
        if author:
            _author = _data[6].split('\n')
            _author = [line.strip() for line in _author if line]
            out.append(_author)
        out = tuple(out)
    return out

# --------------------------------------------------------------------

def SetStdout(fileobj):
    """
    Allows one to overwrite where standard output is sent.

    :Parameters:
      - `fileobj`: file object to use instead of standard output.
    """
    _petsc.PetscSetStdout(fileobj)

def Print(message, comm=None):
    """
    Prints to standard output, only from the first processor in the
    communicator.

    :Parameters:
      - `message`: object to print.
      - `comm` - MPI communicator (defaults to `COMM_WORLD`).

    .. note:: Standard output can be overwritten with `SetStdout()`.
    """
    _petsc.PetscPrintf(comm, str(message))

def Write(fileobj, message, comm=None):
    """
    Writes to a file, only from the first processor in the
    communicator.

    :Parameters:
      - `fileobj`: file object to use.
      - `message`: object to print.
      - `comm` - MPI communicator (defaults to `COMM_WORLD`).
    """
    _petsc.PetscFPrintf(comm, fileobj, str(message))

def SyncPrint(message, comm=None):
    """
    Prints synchronized output from several processors.  Output of the
    first processor is followed by that of the second, etc.

    :Parameters:
      - `message`: object to print.
      - `comm` - MPI communicator (defaults to `COMM_WORLD`).

    .. note:: Requires a intervening call to `SyncFlush()` for
       the information from all the processors to be printed.

    .. note:: Standard output can be overwritten with `SetStdout()`.
    """
    _petsc.PetscSynchronizedPrintf(comm, str(message))

def SyncWrite(fileobj, message, comm=None):
    """
    Writes synchronized output to the specified file from several
    processors.  Output of the first processor is followed by that of
    the second, etc.

    :Parameters:
      - `fileobj`: file object to use.
      - `message`: object to print.
      - `comm` - MPI communicator (defaults to `COMM_WORLD`).

    .. note:: Requires a intervening call to `SyncFlush()` for
       the information from all the processors to be printed.
    """
    _petsc.PetscSynchronizedFPrintf(comm, fileobj, str(message))

def SyncFlush(comm=None):
    """
    Flushes output from all processors involved in previous call to
    `SyncPrint()`/`SyncWrite()`.

    .. note:: Usage of `SyncPrint()` and `SyncWrite()` with different
       MPI communicators **requires** an intervening call to
       `SyncFlush()`.
    """
    _petsc.PetscSynchronizedFlush(comm)


SynchronizedPrint = SyncPrint
SynchronizedWrite = SyncWrite
SynchronizedFlush = SyncFlush

# --------------------------------------------------------------------


def SplitOwnership(lsize=None, gsize=None,
                   bsize=None, comm=None):
    """
    Given a global (or local) length determines a local (or global)
    length via a simple formula. Splits so each processors local size
    is divisible by the block size.

    :Parameters:
      - `lsize`: local length (or `DECIDE` to have it set).
      - `gsize`: global length (or `DECIDE`).
      - `bsize`: block size (optional, defaults to 1).
      - `comm`: MPI communicator that shares the object being divided
        (defaults to `COMM_WORLD`).

    :Returns:
      - local length.
      - global length.
    
    .. note:: Parameters `lsize` and `gsize` cannot be both `DECIDE`.
       If one processor calls this with `gsize` of `DECIDE` then all
       processors must, otherwise the program will hang.
    """
    _decide = _petsc.PETSC_DECIDE
    if lsize is None:
        lsize = _decide
    elif lsize != _decide:
        if not isinstance(lsize, int):
            raise TypeError('local size must be integer')
        elif lsize < 0:
            raise ValueError('local size must be nonnegative')
    if gsize is None:
        gsize = _decide
    elif gsize != _decide:
        if not isinstance(gsize, int):
            raise TypeError('global size must be integer')
        elif gsize < 0:
            raise ValueError('global size must be nonnegative')
    if lsize == _decide and gsize == _decide:
        raise ValueError("local and global sizes "
                         "cannot be both `DECIDE`")
    if bsize is None or bsize == _decide:
        split = _petsc.PetscSplitOwnership
        sizes = split(comm, lsize, gsize)
    else:
        if not isinstance(bsize, int):
            raise TypeError('block size must be integer')
        elif bsize <= 0:
            raise ValueError('block size must be positive')
        split = _petsc.PetscSplitOwnershipBlock
        sizes = split(comm, bsize, lsize, gsize)
    return tuple(sizes)

# --------------------------------------------------------------------

class SeqPhase(object):
    """
    Provide a way to force a section of code to be executed by the
    processes in rank order. Typically, this is done with::

        >>> seqphase = SeqPhase(comm)
        >>> seqphase.begin()
        >>> # <code to be executed sequentially>
        >>> seqphase.end()
    """
   
    def __init__(self, comm=None, npg=1):
        """
        Constructs a sequentializer object.

        :Parameters:
          - `comm` - MPI communicator (defaults to `COMM_WORLD`) to
            sequentialize.
          - `npg`: number in processor group.  This many processes are
            allowed to execute at the same time (defaults to 1)
        """
        if comm is None:
            comm = _petsc.PetscGetCommWorld()
        size = _petsc.PetscCommGetSize(comm)
        if not isinstance(npg, int):
            raise TypeError('`npg` must be integer')
        elif npg <= 0:
            raise ValueError('`npg` must be positive')
        elif npg > size:
            raise ValueError('`npg` must be less than `comm` size')
        self.comm = comm
        self.npg = npg

    def begin(self):
        """Begins a sequential section of code."""
        _petsc.PetscSequentialPhaseBegin(self.comm, self.npg)
        
    def end(self):
        """Ends a sequential section of code."""
        _petsc.PetscSequentialPhaseEnd(self.comm, self.npg)
        

# --------------------------------------------------------------------


def Sleep(seconds=1):
    """
    Sleeps some number of seconds.

    :Parameters:
      - `seconds`: number of seconds to sleep

    .. note:: If `seconds` is negative waits for keyboard input.
    """
    _petsc.PetscSleep(seconds)


# --------------------------------------------------------------------

class Sys(object):

    """
    PETSc System Routines.
    """

    @staticmethod
    def getVersion(patch=False, date=False, author=False):
        """
        Return PETSc version information.
        """
        _data = _petsc.PetscGetVersion()
        _version = tuple(_data[0:3])
        out = _version
        if patch or date or author:
            out = [_version]
            if patch:
                _patch = _data[3]
                out.append(_patch)
            if date:
                if patch:
                    _date = [_data[4], _data[5]]
                else:
                    _date = _data[4]
                out.append(_date)
            if author:
                _author = _data[6].split('\n')
                _author = [line.strip() for line in _author if line]
                out.append(_author)
            out = tuple(out)
        return out

    @staticmethod
    def isInitialized():
        """
        Check if `Initialize()` has been called.
        """
        return bool(_petsc.PetscInitialized())


    @staticmethod
    def isFinalized():
        """
        Check if `Finalize()` has been called.
        """
        return bool(_petsc.PetscFinalized())

    @staticmethod
    def sleep(seconds=1):
        """
        Sleep some number of seconds.

        :Parameters:
          - `seconds`: number of seconds to sleep

        .. note:: If `seconds` is negative waits for keyboard input.
        """
        _petsc.PetscSleep(seconds)

    @staticmethod
    def setStdOut(fileobj):
        """
        Allow to overwrite where standard output is sent.

        :Parameters:
          - `fileobj`: file object to use instead of standard output.
        """
        _petsc.PetscSetStdout(fileobj)

    @staticmethod
    def Print(message, comm=None):
        """
        Print to standard output, only from the first processor in the
        communicator.

        :Parameters:
          - `message`: object to print.
          - `comm`: MPI communicator (defaults to `COMM_WORLD`).

        .. note:: Standard output can be overwritten with `setStdOut()`.
        """
        _petsc.PetscPrintf(comm, str(message))

    @staticmethod
    def write(fileobj, message, comm=None):
        """
        Write to a file, only from the first processor in the
        communicator.

        :Parameters:
          - `fileobj`: file object to use.
          - `message`: object to print.
          - `comm`: MPI communicator (defaults to `COMM_WORLD`).
        """
        _petsc.PetscFPrintf(comm, fileobj, str(message))

    @staticmethod
    def syncPrint(message, comm=None):
        """
        Print synchronized output from several processors.  Output of
        the first processor is followed by that of the second, etc.

        :Parameters:
          - `message`: object to print.
          - `comm`: MPI communicator (defaults to `COMM_WORLD`).

        .. note:: Requires a intervening call to `syncFlush()` for
           the information from all the processors to be printed.

        .. note:: Standard output can be overwritten with `SetStdout()`.
        """
        _petsc.PetscSynchronizedPrintf(comm, str(message))

    @staticmethod
    def syncWrite(fileobj, message, comm=None):
        """
        Write synchronized output to the specified file from several
        processors.  Output of the first processor is followed by that
        of the second, etc.

        :Parameters:
          - `fileobj`: file object to use.
          - `message`: object to print.
          - `comm`: MPI communicator (defaults to `COMM_WORLD`).

        .. note:: Requires a intervening call to `syncFlush()` for
           the information from all the processors to be printed.
        """
        _petsc.PetscSynchronizedFPrintf(comm, fileobj, str(message))

    @staticmethod
    def syncFlush(comm=None):
        """
        Flush output from all processors involved in previous call to
        `syncPrint()`/`syncWrite()`.

        .. note:: Usage of `syncPrint()` and `syncWrite()` with different
           MPI communicators **requires** an intervening call to
           `syncFlush()`.
        """
        _petsc.PetscSynchronizedFlush(comm)

# --------------------------------------------------------------------
