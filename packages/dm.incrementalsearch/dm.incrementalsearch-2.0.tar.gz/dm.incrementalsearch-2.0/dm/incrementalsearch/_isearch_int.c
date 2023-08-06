/*	$Id: _isearch_int.c,v 1.1.1.1 2008/06/27 19:21:39 dieter Exp $

"ISearch_template.c" adapter for "INT" keys.
*/

#include "_isearch.h"

#define KEY_TYPE	int
#define KEYTYPE		INT
#define VALUE		value.intValue
#define COPY(src, dest) (dest = src)
#define COPY_NEW COPY
#define COMPARE(KEY1, KEY2) ((key1 = (KEY1)), (key2 = (KEY2)))
#define EQ() (key1 == key2)
#define GT() (key1 > key2)
#define GE() (key1 >= key2)

#define CAPI(ISEARCH) ((CAPI_TYPE *)(ISEARCH)->capi)

#define SETTYPE_MODULE "BTrees.IIBTree"
#define SETTYPE_CLASS "IISet"

/* Sad that we cannot assume the GNU C preprocessor. Because, we must be
   prepared for stupic preprocessors, we get this collection of trivial
   name definitions.
*/
#define CAPI_TYPE ISearchCAPI_int
#define IBTREE_CAPI_NAME DM_IncrementalSearch2_ibtree_capi_int
#define IAND_CAPI_NAME DM_IncrementalSearch2_iand_capi_int
#define IOR_CAPI_NAME DM_IncrementalSearch2_ior_capi_int

#define GET_TREE DM_IncrementalSearch2_ibtree_getTree_int
#define ESTIMATE_SIZE DM_IncrementalSearch2_ibtree_estimateSize_int
#define AS_SET DM_IncrementalSearch2_asSet_int
#define INIT DM_IncrementalSearch2_init_int


/* Now include the template */
#include "_isearch_template.c"

