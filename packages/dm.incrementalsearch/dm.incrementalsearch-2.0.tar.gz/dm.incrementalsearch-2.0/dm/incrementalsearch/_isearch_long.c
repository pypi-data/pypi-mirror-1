/*	$Id: _isearch_long.c,v 1.1.1.1 2008/06/27 19:21:39 dieter Exp $

"ISearch_template.c" adapter for "LONG" keys.
*/

#include "_isearch.h"

#define KEY_TYPE	PY_LONG_LONG
#define KEYTYPE		LONG
#define VALUE		value.longValue
#define COPY(src, dest) (dest = src)
#define COPY_NEW COPY
#define COMPARE(KEY1, KEY2) ((key1 = (KEY1)), (key2 = (KEY2)))
#define EQ() (key1 == key2)
#define GT() (key1 > key2)
#define GE() (key1 >= key2)

#define CAPI(ISEARCH) ((CAPI_TYPE *)(ISEARCH)->capi)

#define SETTYPE_MODULE "BTrees.LLBTree"
#define SETTYPE_CLASS "LLSet"

/* Sad that we cannot assume the GNU C preprocessor. Because, we must be
   prepared for stupic preprocessors, we get this collection of trivial
   name definitions.
*/
#define CAPI_TYPE ISearchCAPI_long
#define IBTREE_CAPI_NAME DM_IncrementalSearch2_ibtree_capi_long
#define IAND_CAPI_NAME DM_IncrementalSearch2_iand_capi_long
#define IOR_CAPI_NAME DM_IncrementalSearch2_ior_capi_long

#define GET_TREE DM_IncrementalSearch2_ibtree_getTree_long
#define ESTIMATE_SIZE DM_IncrementalSearch2_ibtree_estimateSize_long
#define AS_SET DM_IncrementalSearch2_asSet_long
#define INIT DM_IncrementalSearch2_init_long


/* Now include the template */
#include "_isearch_template.c"

