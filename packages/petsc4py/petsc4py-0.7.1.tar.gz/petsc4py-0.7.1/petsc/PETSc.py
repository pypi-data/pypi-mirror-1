# Author:    Lisandro Dalcin
# Contact:   dalcinl@users.sourceforge.net
# Copyright: This module has been placed in the public domain.
# Id: $Id$

"""
PETSc main module.
"""

# --------------------------------------------------------------------

__date__     = '$Date$'
__version__  = '$Version$'
__revision__ = '$Revision$'

__docformat__ = 'reStructuredText'

# --------------------------------------------------------------------

from petsc4py.Error     import *
from petsc4py.Constants import *
from petsc4py.Comm      import *
from petsc4py.Sys       import *
from petsc4py.Options   import *
from petsc4py.Log       import *
from petsc4py.Object    import *
from petsc4py.Viewer    import *
from petsc4py.Random    import *
from petsc4py.DM        import *
from petsc4py.IS        import *
from petsc4py.Vec       import *
from petsc4py.Mat       import *
from petsc4py.KSP       import *
from petsc4py.SNES      import *
from petsc4py.TS        import *

# --------------------------------------------------------------------
