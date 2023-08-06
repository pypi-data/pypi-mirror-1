/* Copyright (C) 2005 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
  see "LICENSE.txt" for details
*/
/*	$Id: _isearch.h,v 1.1.1.1 2008/06/27 19:21:39 dieter Exp $
Elementary header with basic definitions and declarations.
*/

#ifndef __ISearch_h__
#define __ISearch_h__

#include "Python.h"

typedef int bool;

/* must agree with "__init__.py" */
typedef enum Classification
  {INLIST_SUCCESS, INLIST, CANDIDATE, NOT_INLIST, AT_START, AT_END}
Classification;

typedef enum Keytype {UNDEFINED, INT, OBJECT, LONG} Keytype;

#define CAPI_HEAD					\
  int (*setup)(ISearch *isearch, PyObject *arg);	\
  int (*cleanup)(ISearch *isearch);			\
  PyObject *(*unmantle)(ISearch *isearch)


#define ISearch_HEAD				\
  PyObject_HEAD;				\
  struct CAPI_Head	*capi;			\
  Keytype		keytype;		\
  Classification	classification;		\
  long			estimatedSize;		\
  union {					\
    int	         intValue;			\
    PY_LONG_LONG longValue;			\
    PyObject 	*objValue;			\
  } 			value;			\
  void			*data;

typedef struct ISearch{
  ISearch_HEAD;
} ISearch;

typedef struct CAPI_Head {
  CAPI_HEAD;
} CAPI_Head;



#define _MakeCInterface(NAME, KEYTYPE)				\
typedef struct NAME {						\
  CAPI_HEAD;							\
  Classification (*advanceTo)(ISearch *isearch, KEYTYPE to);	\
  Classification (*advanceFrom)(ISearch *isearch,		\
				bool fromValid,			\
				KEYTYPE from,			\
				bool limitValid,		\
				KEYTYPE limit);			\
} NAME

_MakeCInterface(ISearchCAPI_int, int);
_MakeCInterface(ISearchCAPI_obj, PyObject *);
_MakeCInterface(ISearchCAPI_long, PY_LONG_LONG);

#undef _MakeCInterface

extern ISearchCAPI_int DM_IncrementalSearch2_ibtree_capi_int;
extern ISearchCAPI_int DM_IncrementalSearch2_iand_capi_int;
extern ISearchCAPI_int DM_IncrementalSearch2_ior_capi_int;
extern PyObject *DM_IncrementalSearch2_asSet_int(ISearch *isearch);
extern long DM_IncrementalSearch2_ibtree_estimateSize_int(ISearch *isearch);
/* borrowed */
extern PyObject *DM_IncrementalSearch2_ibtree_getTree_int(ISearch *isearch);
extern int DM_IncrementalSearch2_init_int(void);

extern ISearchCAPI_obj DM_IncrementalSearch2_ibtree_capi_obj;
extern ISearchCAPI_obj DM_IncrementalSearch2_iand_capi_obj;
extern ISearchCAPI_obj DM_IncrementalSearch2_ior_capi_obj;
extern PyObject *DM_IncrementalSearch2_asSet_obj(ISearch *isearch);
extern long DM_IncrementalSearch2_ibtree_estimateSize_obj(ISearch *isearch);
/* borrowed */
extern PyObject *DM_IncrementalSearch2_ibtree_getTree_obj(ISearch *isearch);
extern int DM_IncrementalSearch2_init_obj(void);

extern ISearchCAPI_long DM_IncrementalSearch2_ibtree_capi_long;
extern ISearchCAPI_long DM_IncrementalSearch2_iand_capi_long;
extern ISearchCAPI_long DM_IncrementalSearch2_ior_capi_long;
extern PyObject *DM_IncrementalSearch2_asSet_long(ISearch *isearch);
extern long DM_IncrementalSearch2_ibtree_estimateSize_long(ISearch *isearch);
/* borrowed */
extern PyObject *DM_IncrementalSearch2_ibtree_getTree_long(ISearch *isearch);
extern int DM_IncrementalSearch2_init_long(void);

#endif /* __ISearch_h__ */


