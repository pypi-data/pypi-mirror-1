
#if !defined(__SCHUR_H)
#define __SCHUR_H

#include "private/pcimpl.h"

typedef struct {
  
  PetscTruth     seq;    /* flag for the uniprocessor case*/

  PetscInt       blocks, /* maximum subpartitions in local subdomain*/
                 ccsize, /* maximum subpartition size in local subdomain */
                 layers; /* number of layers for local strip problem */

  PetscInt       sp_count, /* sub-partitioning statistics */
                 sp_minsz,
                 sp_maxsz,
                 sp_nseps;

  /* local interior problem */
  PetscInt       n,      /* number of nodes in this subdomain           */
                 n_I,    /* number of interior nodes in this subdomain  */
                 n_B;    /* number of interface nodes in this subdomain */
  IS             is_I,   /* local (sequential) index sets for interior nodes  */
                 is_B;   /* local (sequential) index sets for interface nodes */
  Vec            vec1_I, /* local (sequential) interior work vectors  */
                 vec2_I,
                 vec3_I, 
                 vec1_B, /* local (sequential) interface work vectors */
                 vec2_B;
  VecScatter     G_to_I, /* scattering context from all global to local interior nodes        */
                 G_to_B; /* scattering context from all global to local interface nodes       */
  Mat            A,      /* local (sequential) matrix      */
                 A_II,   /* local (sequential) submatrices */
                 A_IB,
                 A_BI,
                 A_BB;
  Vec            D;      /* local diagonal scaling "matrix" (stored as a vector) */
  KSP            ksp_I;  /* local linear solver for interior problem  */
  
  /* local strip problem */
  PetscInt       n_L;    /* number of strip nodes in this subdomain  */
  IS             is_L;   /* local (sequential) index sets for strip nodes */
  Vec            vec1_L, /* local (sequential) strip work vector  */
                 vec2_L; /* local (sequential) strip work vector  */
  VecScatter     L_to_B; /* scattering context from local strip to local interface nodes */
  Mat            A_LL;   /* local (sequential) strip submatrix */
  KSP            ksp_L;  /* local linear solver for strip problem  */


  /* global interface problem */
  PetscInt       n_S,    /* local size of global interface problem  */
                 N_S;    /* global size of global interface problem */
  Vec            vec1_S, /* global interface work vectors  */
                 vec2_S; 
  VecScatter     S_to_B; /* scattering context from global interface to local interface nodes */
  Mat            mat_S;  /* global Schur complement operator */
  KSP            ksp_S;  /* global linear solver for interface problem */
  
  KSP            subksp[3];
  
} PC_Schur;


#endif /* __SCHUR_H */
