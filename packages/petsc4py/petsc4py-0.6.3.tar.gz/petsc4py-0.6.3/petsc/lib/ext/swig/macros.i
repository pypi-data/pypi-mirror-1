/* $Id$ */

%define PETSC_MANGLE(NAME)
_PyPetsc_##NAME
%enddef

%define PETSC_OVERRIDE(RETVAL, FUNCNAME, ARGS, CODE)
%wrapper %{
#undef  __FUNCT__  
#define __FUNCT__ "_PyPetsc_"#FUNCNAME
static RETVAL PETSC_MANGLE(FUNCNAME) ARGS CODE
%}
%rename(FUNCNAME) PETSC_MANGLE(FUNCNAME);
static RETVAL PETSC_MANGLE(FUNCNAME) ARGS;
%ignore FUNCNAME;
%enddef


%define %PETSC_CONFIG(PETSC_DIR, PETSC_ARCH)
%import PETSC_DIR/bmake/PETSC_ARCH/petscconf.h
%enddef


%define %PETSC_HEADER(PETSC_DIR, header)
%include PETSC_DIR/include/header
%enddef

%header %{
#define PETSC_VERSION_2_3_0_R \
    (PETSC_VERSION_MAJOR    == 2 && \
     PETSC_VERSION_MINOR    == 3 && \
     PETSC_VERSION_SUBMINOR == 0 && \
     PETSC_VERSION_RELEASE  == 1)

#define PETSC_VERSION_2_3_1_R \
    (PETSC_VERSION_MAJOR    == 2 && \
     PETSC_VERSION_MINOR    == 3 && \
     PETSC_VERSION_SUBMINOR == 1 && \
     PETSC_VERSION_RELEASE  == 1)

#define PETSC_VERSION_2_3_2_R \
    (PETSC_VERSION_MAJOR    == 2 && \
     PETSC_VERSION_MINOR    == 3 && \
     PETSC_VERSION_SUBMINOR == 2 && \
     PETSC_VERSION_RELEASE  == 1)
%}

/*
 * Local Variables:
 * mode: C
 * End:
 */
