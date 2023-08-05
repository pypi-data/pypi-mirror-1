# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
Viewers
=======

Viewers export information and data from PETSc objects.
"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reStructuredText'

# --------------------------------------------------------------------

__all__ = ['Viewer',
           'ViewerFile',
           'ViewerASCII',
           'ViewerBinary',
           'ViewerDraw',
           'ViewerString',
           ]

# --------------------------------------------------------------------

from petsc4py.lib import _petsc

from petsc4py.Object import Object

# --------------------------------------------------------------------


class Viewer(Object):

    """
    Abstract PETSc object that helps view (in ASCII, binary,
    graphically, etc.) other PETSc objects.
    """

    class Type:
        """
        Viewer types.
        """
        ASCII  = _petsc.PETSC_VIEWER_ASCII 
        BINARY = _petsc.PETSC_VIEWER_BINARY
        STRING = _petsc.PETSC_VIEWER_STRING
        DRAW   = _petsc.PETSC_VIEWER_DRAW  
        SOCKET = _petsc.PETSC_VIEWER_SOCKET
        ## VU          = _petsc.PETSC_VIEWER_VU
        ## MATHEMATICA = _petsc.PETSC_VIEWER_MATHEMATICA
        ## SILO        = _petsc.PETSC_VIEWER_SILO
        ## NETCDF      = _petsc.PETSC_VIEWER_NETCDF
        ## HDF4        = _petsc.PETSC_VIEWER_HDF4
        ## MATLAB      = _petsc.PETSC_VIEWER_MATLAB

    class Format:
        """
        Viewer formats.
        """
        ASCII_DEFAULT     = _petsc.PETSC_VIEWER_ASCII_DEFAULT
        ASCII_MATLAB      = _petsc.PETSC_VIEWER_ASCII_MATLAB
        ASCII_MATHEMATICA = _petsc.PETSC_VIEWER_ASCII_MATHEMATICA
        ASCII_IMPL        = _petsc.PETSC_VIEWER_ASCII_IMPL
        ASCII_INFO        = _petsc.PETSC_VIEWER_ASCII_INFO
        ASCII_INFO_DETAIL = _petsc.PETSC_VIEWER_ASCII_INFO_DETAIL
        ASCII_COMMON      = _petsc.PETSC_VIEWER_ASCII_COMMON
        ASCII_SYMMODU     = _petsc.PETSC_VIEWER_ASCII_SYMMODU
        ASCII_INDEX       = _petsc.PETSC_VIEWER_ASCII_INDEX
        ASCII_DENSE       = _petsc.PETSC_VIEWER_ASCII_DENSE
        ASCII_FACTOR_INFO = _petsc.PETSC_VIEWER_ASCII_FACTOR_INFO
        BINARY_DEFAULT    = _petsc.PETSC_VIEWER_BINARY_DEFAULT
        BINARY_NATIVE     = _petsc.PETSC_VIEWER_BINARY_NATIVE
        DRAW_BASIC        = _petsc.PETSC_VIEWER_DRAW_BASIC
        DRAW_LG           = _petsc.PETSC_VIEWER_DRAW_LG
        DRAW_CONTOUR      = _petsc.PETSC_VIEWER_DRAW_CONTOUR 
        DRAW_PORTS        = _petsc.PETSC_VIEWER_DRAW_PORTS
        NATIVE            = _petsc.PETSC_VIEWER_NATIVE
        NOFORMAT          = _petsc.PETSC_VIEWER_NOFORMAT
        ASCII_FACTOR_INFO = _petsc.PETSC_VIEWER_ASCII_FACTOR_INFO

    def __init__(self, *targs, **kwargs):
        """See `create()`"""
        super(Viewer, self).__init__(*targs, **kwargs)
        
    def __call__(self, obj):
        """Same as `view()`."""
        self.view(obj)

    def create(self, comm=None):
        """
        Creates a generic viewer object.
        """
        return _petsc.PetscViewerCreate(comm, self)
    
    def createASCII(self, name='', mode=None, format=None, comm=None):
        """
        Opens a file for ASCII input/output.

        :Parameters:
          - `name`: name of file (optional, defaults to 'stdout')
          - `mode`: mode of file (optional, see `ViewerFile.FileMode`)
          - `format`: viewer ASCII format (optional, see
            `ViewerASCII.Format`).
          - `comm`: MPI communicator
        """
        viewer = _petsc.PetscViewerASCIIOpen(comm, name, self)
        if mode is not None:
            mode = _petsc.get_attr(ViewerFile.FileMode, mode)
            _petsc.PetscViewerFileSetMode(viewer, mode)
        if format is not None:
            format = _petsc.get_attr(ViewerASCII.Format, format)
            _petsc.PetscViewerSetFormat(viewer, format)
        return viewer
        

    def createBinary(self, name=None, mode=None, format=None, comm=None):
        """
        Opens a file for binary input/output.

        :Parameters:
          - `name`: name of file
          - `mode`: mode of file (see `ViewerFile.FileMode`)
          - `format`: viewer binary format (optional)
          - `comm`: MPI communicator

        .. note:: For reading files, the filename may begin with
           ``ftp://`` or ``http://`` and/or end with ``.gz``; in this
           case file is brought over and uncompressed.  For creating
           files, if the file name ends with ``.gz`` it is
           automatically compressed when closed.  For writing files it
           only opens the file on processor 0 in the communicator.
           For readable files it opens the file on all nodes that have
           the file. If node 0 does not have the file it generates an
           error even if other nodes do have the file.
        """
        if name is None or mode is None:
            viewer = _petsc.PetscViewerBinaryCreate(comm, self)
            if mode is not None:
                mode = _petsc.get_attr(ViewerFile.FileMode, mode)
                _petsc.PetscViewerFileSetMode(viewer, mode)
            if name is not None:
                _petsc.PetscViewerFileSetName(viewer, name)
        else:
            fmode = ViewerFile.FileMode
            mode = _petsc.get_attr(fmode, mode, fmode.WRITE)
            viewer = _petsc.PetscViewerBinaryOpen(comm, name,
                                                  mode, self)
        if format is not None:
            format = _petsc.get_attr(ViewerBinary.Format, format)
            _petsc.PetscViewerSetFormat(viewer, format)

    def createDraw(self, title=None, position=None, size=None,
                   display=None, comm=None):
        """
        Opens an X window for use as a viewer
        
        :Parameters:
          - `title`: the title to put in the title bar, or 'None'
            for no title.
          - `position`: tuple '(x, y)' specifying the screen
            coordinates of the upper left corner of window, or use
            `DECIDE`.
          - `size`: tuple '(w, h)' specifying window width and height
            in pixels, or may use `DECIDE`, or see
            `ViewerDraw.WinSize` for other possibilities.
          - `display`: the X display on which to open, or 'None'
            for the local machine.
          - `comm` - communicator that will share window.
        """
        if title is None:
            title   = ''
        if position is None or position == _petsc.PETSC_DECIDE:
            x = y = _petsc.PETSC_DECIDE
        else:
            x, y = position
        if size is None or size == _petsc.PETSC_DECIDE:
            w = h = _petsc.PETSC_DECIDE
        else:
            size = _petsc.get_attr(ViewerDraw.WinSize, size)
            if type(size) is int:
                w = h = size
            else:
                w, h = size
        if display is None:
            display = ''
        return _petsc.PetscViewerDrawOpen(comm, display, title,
                                          x, y, w, h, self)

    def createString(self, length, comm=None):
        """
        Create a string viewer
        """
        return _petsc.PetscViewerStringOpen(comm, length, self)

    def getFormat(self):
        """
        Gets the format for viewers.
        """
        return _petsc.PetscViewerGetFormat(self)

    def setFormat(self, format):
        """
        Sets the format for viewers.
        """
        format = _petsc.get_attr(self.Format, format)
        _petsc.PetscViewerSetFormat(self, format)

    def popFormat(self):
        """
        Resets the format for file viewers.
        """
        _petsc.PetscViewerPopFormat(self)
           
    def pushFormat(self, format):
        """
        Sets the format for viewers.
        """
        format = _petsc.get_attr(self.Format, format)
        _petsc.PetscViewerPushFormat(self, format)

    def view(self, obj=None):
        """
        Views any PETSc object.
        """
        if obj is None:
            _petsc.PetscViewerView(self, None)
        elif isinstance(obj, Viewer):
            _petsc.PetscViewerView(obj, self)
        else:
            _petsc.PetscObjectView(obj, self)

    def flush(self):
        """
        Flushes a viewer (i.e. tries to dump all the data that has
        been printed through a viewer).
        """
        _petsc.PetscViewerFlush(self)
        
    format   = property(getFormat, setFormat)

    @staticmethod
    def STDOUT(comm=None):
        """
        Returns a ASCII Viewer shared by all processors in a
        communicator.
        """
        return _petsc.PETSC_VIEWER_STDOUT_(comm)

    @staticmethod
    def STDERR(comm=None):
        """
        Returns a ASCII Viewer shared by all processors in a
        communicator.
        """
        return _petsc.PETSC_VIEWER_STDERR_(comm)

    @staticmethod
    def BINARY(comm=None):
        """
        Returns a Binary Viewer shared by all processors in a
        communicator.
        """
        return _petsc.PETSC_VIEWER_BINARY_(comm)

    @staticmethod
    def DRAW(comm=None):
        """
        Returns a Draw Viewer shared by all processors in a
        communicator.
        """
        return _petsc.PETSC_VIEWER_DRAW_(comm)


# --------------------------------------------------------------------


class ViewerFile(Viewer):

    """
    Base class for file-based viewers (ASCII and Binary).
    """
    
    class FileMode:
        """
        Access mode for a file.
        
        - `READ`:  open a file at its beginning for reading.
        - `WRITE`: open a file at its beginning for writing (will
          create if the file does not exist).
        - `APPEND`: open a file at end for writing.
        - `UPDATE`: open a file for updating (reading and writing).
        - `APPEND_UPDATE`: open a file for updating, (reading and
          writing), at the end.
        """
        # native
        READ          = _petsc.FILE_MODE_READ
        WRITE         = _petsc.FILE_MODE_WRITE
        APPEND        = _petsc.FILE_MODE_APPEND
        UPDATE        = _petsc.FILE_MODE_UPDATE
        APPEND_UPDATE = _petsc.FILE_MODE_APPEND_UPDATE
        # aliases
        R, W, A, U = READ, WRITE, APPEND, UPDATE
        AU = UA    = APPEND_UPDATE

    def getFileMode(self):
        """
        Gets the mode of file to be open.
        """
        return _petsc.PetscViewerFileGetMode(self)

    def setFileMode(self, mode):
        """
        Sets the mode of file to be open.
        """
        mode = _petsc.get_attr(ViewerFile.FileMode, mode)
        _petsc.PetscViewerFileSetMode(self, mode)

    def getFileName(self):
        """
        Gets the name of the file the viewer uses.
        """
        return _petsc.PetscViewerFileGetName(self)

    def setFileName(self, name):
        """
        Sets the name of the file the viewer uses.
        """
        _petsc.PetscViewerFileSetName(self, name)

    filename = property(getFileName, setFileName)
    filemode = property(getFileMode, setFileMode)


class ViewerASCII(ViewerFile):

    """
    ASCII Viewer.
    """

    class Format:
        """
        ASCII formats.
        """
        DEFAULT     = _petsc.PETSC_VIEWER_ASCII_DEFAULT
        MATLAB      = _petsc.PETSC_VIEWER_ASCII_MATLAB 
        MATHEMATICA = _petsc.PETSC_VIEWER_ASCII_MATHEMATICA
        IMPL        = _petsc.PETSC_VIEWER_ASCII_IMPL
        INFO        = _petsc.PETSC_VIEWER_ASCII_INFO
        INFO_DETAIL = _petsc.PETSC_VIEWER_ASCII_INFO_DETAIL
        COMMON      = _petsc.PETSC_VIEWER_ASCII_COMMON
        SYMMODU     = _petsc.PETSC_VIEWER_ASCII_SYMMODU
        INDEX       = _petsc.PETSC_VIEWER_ASCII_INDEX
        DENSE       = _petsc.PETSC_VIEWER_ASCII_DENSE
        FACTOR_INFO = _petsc.PETSC_VIEWER_ASCII_FACTOR_INFO

    def __init__(self, *targs, **kwargs):
        """
        See `Viewer.createASCII()`
        """
        super(ViewerASCII, self).__init__(*targs, **kwargs)
        self.createASCII(*targs, **kwargs)
                

class ViewerBinary(ViewerFile):

    """
    Binary Viewer.
    """

    class Format:
        """
        Binary formats.
        """
        DEFAULT    = _petsc.PETSC_VIEWER_BINARY_DEFAULT
        NATIVE     = _petsc.PETSC_VIEWER_BINARY_NATIVE

    def __init__(self, *targs, **kwargs):
        """
        See `Viewer.createBinary()`
        """
        super(ViewerBinary, self).__init__(*targs, **kwargs)
        self.createBinary(*targs, **kwargs)
        

class ViewerDraw(Viewer):

    """
    Opens an X window for use as a viewer.
    """

    class Format:
        """
        Draw formats.
        """
        BASIC   = _petsc.PETSC_VIEWER_DRAW_BASIC
        LG      = _petsc.PETSC_VIEWER_DRAW_LG
        CONTOUR = _petsc.PETSC_VIEWER_DRAW_CONTOUR 
        PORTS   = _petsc.PETSC_VIEWER_DRAW_PORTS

    class WinSize:
        """
        Window sizes
        """
        # native
        FULL_SIZE    = _petsc.PETSC_DRAW_FULL_SIZE
        HALF_SIZE    = _petsc.PETSC_DRAW_HALF_SIZE
        THIRD_SIZE   = _petsc.PETSC_DRAW_THIRD_SIZE
        QUARTER_SIZE = _petsc.PETSC_DRAW_QUARTER_SIZE
        # alias
        FULL    = FULL_SIZE
        HALF    = HALF_SIZE
        THIRD   = THIRD_SIZE
        QUARTER = QUARTER_SIZE

    def __init__(self, *targs, **kwargs):
        """
        See `Viewer.createDraw()`
        """
        super(ViewerDraw, self).__init__(*targs, **kwargs)
        self.createDraw(*targs, **kwargs)

        
    def setInfo(self, title=None, position=None, size=None, display=None):
        """
        Configures the X window to be opened
        
        :Parameters:
          - `title`: the title to put in the title bar, or 'None'
            for no title.
          - `position`: tuple '(x, y)' specifying the screen
            coordinates of the upper left corner of window, or use
            `DECIDE`.
          - `size`: tuple '(w, h)' specifying window width and height
            in pixels, or may use `DECIDE`, or see
            `ViewerDraw.WinSize` for other possibilities.
          - `display`: the X display on which to open, or 'None'
            for the local machine.
        """
        if title is None:
            title   = ''
        if position is None or position == _petsc.PETSC_DECIDE:
            x = y = _petsc.PETSC_DECIDE
        else:
            x, y = position
        if size is None or size == _petsc.PETSC_DECIDE:
            w = h = _petsc.PETSC_DECIDE
        else:
            size = _petsc.get_attr(ViewerDraw.WinSize, size)
            if type(size) is int:
                w = h = size
            else:
                w, h = size
        if display is None:
            display = ''
        _petsc.PetscViewerDrawSetInfo(self, display, title,
                                      x, y, w, h)

    def clear(self):
        """
        Clears a graphic associated with a viewer.
        """
        _petsc.PetscViewerDrawClear(self)

        
class ViewerString(Viewer):

    """
    String Viewer.
    """

    def __init__(self, *targs, **kwargs):
        """
        See `Viewer.createString()`
        """
        super(ViewerString, self).__init__(*targs, **kwargs)
        self.createString(*targs, **kwargs)

    def getString(self):
        """
        Get the contents of a string viewer
        """
        return _petsc.PetscViewerStringGetString(self)



# --------------------------------------------------------------------
