
/* IS */
typedef struct _p_IS* IS;

/* ISType */
typedef enum {IS_GENERAL=0,IS_STRIDE=1,IS_BLOCK = 2} ISType;

/* ISLocalToGlobalMapping */
typedef struct _p_ISLocalToGlobalMapping* ISLocalToGlobalMapping;

/* ISGlobalToLocalMappingType */
typedef enum {
  IS_GTOLM_MASK,
  IS_GTOLM_DROP
} ISGlobalToLocalMappingType;

/*
 * Local Variables:
 * mode: C
 * End:
 */
