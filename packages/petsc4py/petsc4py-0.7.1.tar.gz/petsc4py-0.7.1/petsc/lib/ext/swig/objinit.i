/* ---------------------------------------------------------------- */

%header %{
#define PY_PETSC_OBJ_INIT(PYTYPE, CTYPE, COOKIE) \
SWIGINTERN PyObject* \
PYTYPE##_init(PyObject *_self, CTYPE obj, const char* type) \
{							    \
  PetscTruth same  = PETSC_FALSE;			    \
  CTYPE      *self = PETSC_NULL;			    \
  self = Py##CTYPE##_AsPtr(_self);			    \
  if (!self && PyErr_Occurred()) return NULL;		    \
  if (obj) {						    \
    if (type && type[0] != '\0' ) {			    \
      PetscTypeCompare((PetscObject)obj, type, &same);	    \
      if (!same) {					    \
	PyErr_Format(PyExc_ValueError,			    \
                     "expecting a %s object of type '%s'",  \
		     #CTYPE, type);			    \
	return NULL;					    \
      }							    \
    }							    \
    PetscObjectReference((PetscObject)obj);		    \
  }							    \
  _obj_destroy((PetscObject)(*self));			    \
  *self = obj;						    \
  Py_RETURN_NONE;					    \
}
%}

%define %PETSC_OBJ_INIT(PYTYPE, CTYPE, COOKIE)
%header %{PY_PETSC_OBJ_INIT(PYTYPE, CTYPE, COOKIE)%}
PyObject* PYTYPE##_init(PyObject*, CTYPE OPTIONAL, const char* type);
%enddef

//%PETSC_OBJ_INIT( Object    , PetscObject            , PETSC_OBJECT_COOKIE  )
//%PETSC_OBJ_INIT( Viewer    , PetscViewer            , PETSC_VIEWER_COOKIE  )
%PETSC_OBJ_INIT( Random    , PetscRandom            , PETSC_RANDOM_COOKIE  )
//%PETSC_OBJ_INIT( IS        , IS                     , IS_COOKIE            )
//%PETSC_OBJ_INIT( LGMapping , ISLocalToGlobalMapping , IS_LTOGM_COOKIE      )
//%PETSC_OBJ_INIT( AO        , AO                     , AO_COOKIE            )
%PETSC_OBJ_INIT( Vec       , Vec                    , VEC_COOKIE           )
//%PETSC_OBJ_INIT( Scatter   , VecScatter             , VEC_SCATTER_COOKIE   )
%PETSC_OBJ_INIT( Mat       , Mat                    , MAT_COOKIE           )
//%PETSC_OBJ_INIT( NullSpace , MatNullSpace           , MAT_NULLSPACE_COOKIE )
%PETSC_OBJ_INIT( KSP       , KSP                    , KSP_COOKIE           )
%PETSC_OBJ_INIT( PC        , PC                     , PC_COOKIE            )
%PETSC_OBJ_INIT( SNES      , SNES                   , SNES_COOKIE          )
%PETSC_OBJ_INIT( TS        , TS                     , TS_COOKIE            )

/* ---------------------------------------------------------------- */


/*
 * Local Variables:
 * mode: C
 * End:
 */
