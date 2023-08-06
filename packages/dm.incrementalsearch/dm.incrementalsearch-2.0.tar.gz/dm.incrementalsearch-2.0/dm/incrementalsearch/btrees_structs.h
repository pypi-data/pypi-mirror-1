/* This code is mostly a copy of Zope code and therefore is covered by
   the ZPL (Zope Public License).
*/
/*	$Id: btrees_structs.h,v 1.1.1.1 2008/06/27 19:21:39 dieter Exp $
Copy of the BTrees structure definitions from "BTrees.BTreeModuleTemplate.c".

Unfortunately, the structure definitions are not packaged to be reuseable
externally. Therefore, we had to copy them.

Note, that it may become necessary to fetch a new copy, in case
the original definitions are changed in a significant way.


The header file has 'KEY_TYPE' as a free variable. It assumes
that the including context defines a 'KEY_TYPE' macro specifying
the type of keys in this btrees.

We are uninterested in values and define 'VALUE_TYPE' as void.
We also define "PERSISTENT" because we are only interested in
uses within the ZODB.
*/

#ifndef __BTrees_Structs_h__
#define __BTrees_Structs_h__

#define VALUE_TYPE void
#define PERSISTENT

/* here starts the copy */

#ifdef PERSISTENT
#include "persistent/cPersistence.h"
#else
#define PER_USE_OR_RETURN(self, NULL)
#define PER_ALLOW_DEACTIVATION(self)
#define PER_PREVENT_DEACTIVATION(self)
#define PER_DEL(self)
#define PER_USE(O) 1
#define PER_ACCESSED(O) 1
#define PER_CHANGED(O) 0
#endif

/* So sue me.  This pair gets used all over the place, so much so that it
 * interferes with understanding non-persistence parts of algorithms.
 * PER_UNUSE can be used after a successul PER_USE or PER_USE_OR_RETURN.
 * It allows the object to become ghostified, and tells the persistence
 * machinery that the object's fields were used recently.
 */
#define PER_UNUSE(OBJ) do {             \
    PER_ALLOW_DEACTIVATION(OBJ);        \
    PER_ACCESSED(OBJ);                  \
} while (0)

static void PyVar_Assign(PyObject **v, PyObject *e) { Py_XDECREF(*v); *v=e;}
#define ASSIGN(V,E) PyVar_Assign(&(V),(E))
#define ASSIGNC(V,E) (Py_INCREF((E)), PyVar_Assign(&(V),(E)))
#define UNLESS(E) if (!(E))
#define UNLESS_ASSIGN(V,E) ASSIGN(V,E); UNLESS(V)
#define LIST(O) ((PyListObject*)(O))
#define OBJECT(O) ((PyObject*)(O))
#define SameType_Check(O1, O2) ((O1)->ob_type==(O2)->ob_type)


/* Various kinds of BTree and Bucket structs are instances of
 * "sized containers", and have a common initial layout:
 *     The stuff needed for all Python objects, or all Persistent objects.
 *     int size:  The maximum number of things that could be contained
 *                without growing the container.
 *     int len:   The number of things currently contained.
 *
 * Invariant:  0 <= len <= size.
 *
 * A sized container typically goes on to declare one or more pointers
 * to contiguous arrays with 'size' elements each, the initial 'len' of
 * which are currently in use.
 */
#ifdef PERSISTENT
#define sizedcontainer_HEAD         \
    cPersistent_HEAD                \
    int size;                       \
    int len;
#else
#define sizedcontainer_HEAD         \
    PyObject_HEAD                   \
    int size;                       \
    int len;
#endif

/* Nothing is actually of type Sized, but (pointers to) BTree nodes and
 * Buckets can be cast to Sized* in contexts that only need to examine
 * the members common to all sized containers.
 */
typedef struct Sized_s {
    sizedcontainer_HEAD
} Sized;

#define SIZED(O) ((Sized*)(O))

/* A Bucket wraps contiguous vectors of keys and values.  Keys are unique,
 * and stored in sorted order.  The 'values' pointer may be NULL if the
 * Bucket is used to implement a set.  Buckets serving as leafs of BTrees
 * are chained together via 'next', so that the entire BTree contents
 * can be traversed in sorted order quickly and easily.
 */
typedef struct Bucket_s {
  sizedcontainer_HEAD
  struct Bucket_s *next;    /* the bucket with the next-larger keys */
  KEY_TYPE *keys;           /* 'len' keys, in increasing order */
  VALUE_TYPE *values;       /* 'len' corresponding values; NULL if a set */
} Bucket;

#define BUCKET(O) ((Bucket*)(O))

/* A BTree is complicated.  See Maintainer.txt.
 */

typedef struct BTreeItem_s {
  KEY_TYPE key;
  Sized *child; /* points to another BTree, or to a Bucket of some sort */
} BTreeItem;

typedef struct BTree_s {
  sizedcontainer_HEAD

  /* firstbucket points to the bucket containing the smallest key in
   * the BTree.  This is found by traversing leftmost child pointers
   * (data[0].child) until reaching a Bucket.
   */
  Bucket *firstbucket;

  /* The BTree points to 'len' children, via the "child" fields of the data
   * array.  There are len-1 keys in the 'key' fields, stored in increasing
   * order.  data[0].key is unused.  For i in 0 .. len-1, all keys reachable
   * from data[i].child are >= data[i].key and < data[i+1].key, at the
   * endpoints pretending that data[0].key is minus infinity and
   * data[len].key is positive infinity.
   */
  BTreeItem *data;
} BTree;


#define BTREE(O) ((BTree*)(O))

#endif /* __BTrees_Structs_h__ */
