/*	$Id: _isearch_obj.c,v 1.1.1.1 2008/06/27 19:21:39 dieter Exp $

"ISearch_template.c" adapter for "OBJECT" keys.
*/

#include "_isearch.h"

typedef PyObject *PyObjectP;

#define KEY_TYPE	PyObjectP
#define KEYTYPE		OBJECT
#define VALUE		value.objValue
#define COPY(src, dest) do {				\
  KEY_TYPE stmp = (src), *dtmpp = &(dest), dtmp = *dtmpp;\
  Py_INCREF(stmp); *dtmpp = stmp; Py_XDECREF(dtmp);	\
} while (0)
#define COPY_NEW(src, dest) do {				\
  KEY_TYPE stmp = (src);				\
  Py_INCREF(stmp); (dest) = stmp;			\
} while (0)
#define COMPARE(KEY1, KEY2) do {					\
  cmp = PyObject_Compare((KEY1), (KEY2));				\
  /* if (PyErr_Occurred()) return -1; / * we do not expect errors */	\
} while (0)
#define EQ() (cmp == 0)
#define GT() (cmp > 0)
#define GE() (cmp >= 0)

#define CAPI(ISEARCH) ((CAPI_TYPE *)(ISEARCH)->capi)

#define SETTYPE_MODULE "BTrees.OOBTree"
#define SETTYPE_CLASS "OOSet"

/* Sad that we cannot assume the GNU C preprocessor. Because, we must be
   prepared for stupic preprocessors, we get this collection of trivial
   name definitions.
*/
#define CAPI_TYPE ISearchCAPI_obj
#define IBTREE_CAPI_NAME DM_IncrementalSearch2_ibtree_capi_obj
#define IAND_CAPI_NAME DM_IncrementalSearch2_iand_capi_obj
#define IOR_CAPI_NAME DM_IncrementalSearch2_ior_capi_obj

#define GET_TREE DM_IncrementalSearch2_ibtree_getTree_obj
#define ESTIMATE_SIZE DM_IncrementalSearch2_ibtree_estimateSize_obj
#define AS_SET DM_IncrementalSearch2_asSet_obj
#define INIT DM_IncrementalSearch2_init_obj

/* Now include the template */
#include "_isearch_template.c"
