#if !defined(__NSI_H)
#define __NSI_H

#include "private/pcimpl.h"

typedef struct {

  PetscInt nd; /*number of physical dimensions */
  IS is[4];
  
  Vec vec1[4];
  Vec vec2[4];
  
  VecScatter scatter[4];

  Mat F[3];  /*     [ F  | B1' ] */
  Mat B1,B2; /* J = [----+-----] */
  Mat C;     /*     [ B2 | -C  ] */
  
  KSP ksp[4];

} PC_NSI;

#endif /* __NSI_H */





