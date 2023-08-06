/* Copyright (C) 2005 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
  see "LICENSE.txt" for details
*/
/*	$Id: _isearch_template.c,v 1.1.1.1 2008/06/27 19:21:39 dieter Exp $
Generic implementation of 'BTrees' ISearches, 'IAnd' and 'IOr'.

This module is designed to be included into another 'C' souce module
which defines a set of macros used in this module.
These macros specialize the generic code to a keytype of either 
'int' or 'object'.
*/


#include <assert.h>

#include "btrees_structs.h"



/****************************************************************************
*****************************************************************************

Auxiliaries

*****************************************************************************
****************************************************************************/

static void *mycalloc(size_t size) {
  void *block;

  if ((block = malloc(size))) memset(block, 0, size);
  return block;
}

int INIT(void) {
  cPersistenceCAPI=PyCObject_Import("persistent.cPersistence","CAPI");
  if (! cPersistenceCAPI) {
    /* maybe pre Zope 2.8? */
    PyErr_Clear();
    cPersistenceCAPI=PyCObject_Import("cPersistence","CAPI");
  }
  return (cPersistenceCAPI) ? 0 : -1;
}
  



/****************************************************************************
'BTrees' as ISearches
****************************************************************************/

/* prepare access to "tree" and assign the "btree" */
#define ACCESS(tree)						\
do { assert(!btree); PER_USE_OR_RETURN(tree, -1); btree = tree; } while (0)
#define OACCESS(tree)						\
do { assert(!btree); PER_USE_OR_RETURN(tree, NULL); btree = tree; } while (0)
#define UNACCESS()					\
do { PER_UNUSE(btree); btree = NULL; } while (0)

/* An 'IBTree' essentially represents a path from the root to a key
   in the leaf. */

typedef struct BTNode {
  bool is_leaf;		/* whether this is a leaf or an internal node */
  BTree *tree;		/* (new) reference to 'BTree' or 'Bucket' */
  int	current;	/* current position */
} BTNode;

typedef struct IBTree {
  /* path related fields */
  BTNode	*path;
  int		path_size, path_len;
  /* size calculation */
  long		mean_node_size, mean_bucket_size;
  /* optimizations */
  bool		is_deep;
  BTNode	*current_leaf, current_leaf_storage;
} IBTree;

/* current leaf optimization auxiliaries */
static BTNode *setIndependentCurrentLeaf(IBTree *ib, BTree* tree) {
  ib->current_leaf = &ib->current_leaf_storage;
  ib->current_leaf->current = 0;
  Py_XDECREF(ib->current_leaf->tree); Py_INCREF(tree);
  ib->current_leaf->tree = tree;
  return ib->current_leaf;
}

static void unsetIndependentCurrentLeaf(IBTree *ib) {
  if (ib->current_leaf == &ib->current_leaf_storage) {
    Py_DECREF(ib->current_leaf_storage.tree);
    ib->current_leaf_storage.tree = NULL;
    ib->current_leaf = NULL;
  }
}

/* path manipulation */
static BTNode *pushPath(IBTree *ib, BTree* tree) {
  int len, old_len, size; bool is_leaf; BTNode *pe;
  len = (old_len = ib->path_len) + 1;
  if (len > ib->path_size) {
    /* need to grow */
    size = ib->path_size = len<<1;
    ib->path = realloc(ib->path, size * sizeof(BTNode)); /* hope, it handles NULL */
    if (! ib->path) return (BTNode *) PyErr_NoMemory();
  }
  pe = &ib->path[ib->path_len++];
  if (old_len)
    is_leaf = !SameType_Check(ib->path[old_len-1].tree, tree);
  else {
    BTree	*btree = NULL; /* for ACCESS */;
    OACCESS(tree);
    if (! btree->firstbucket)
      /* this is a bucket or empty tree - not a (non empty) tree */
      is_leaf = 1;
    else {
      /* this is in principle a non empty tree */
      if (btree->len==1 && BUCKET(btree->data[0].child) == btree->firstbucket) {
	/* but one with a single bucket - replace with this one */
	is_leaf = 1; tree = BTREE(btree->firstbucket);
      } else is_leaf = 0; /* a deeper tree */
    }
    UNACCESS();
  }
  pe->is_leaf = is_leaf;
  pe->current = 1 - is_leaf;
  Py_INCREF(tree); pe->tree = tree;
  if (is_leaf) {
    /* we could optimize here, in case an indepentent current leaf references
       the same tree */
    unsetIndependentCurrentLeaf(ib);
    ib->current_leaf = pe;
  }
  return pe;
}

static void cropPath(IBTree *ib, int level) {
  int len; BTNode *path;
  if ((len = ib->path_len) > level) {
    path = ib->path;
    while (len > level) {
      BTree *tree = path[--len].tree;
      Py_DECREF(tree);
    }
    ib->path_len = level;
  }
}
  
/* ibtree capi */

#define EXTRACT_LEAF_KEY(index) (BUCKET(btree)->keys[index]) 
#define EXTRACT_NODE_KEY(index) (btree->data[index].key) 

#define BINARY_SEARCH(EXTRACT_KEY) {			\
 curkey = EXTRACT_KEY(current);				\
 COMPARE(curkey, key);					\
 if (GT() || (myinclude && EQ())){			\
   if (is_leaf) { d = GT(); break; }			\
   UNACCESS();						\
   level++;						\
   continue;						\
 }							\
 /* widening loop */					\
 d = 1;							\
 while (1) {						\
   int	i = node_len - 1 - current;			\
   KEY_TYPE	tmpkey;					\
   if (d > i) d = i;					\
   if (!i) { current = node_len; break; }		\
   tmpkey = EXTRACT_KEY(current + d);			\
   COMPARE(tmpkey, key);				\
   if (GT()) break;					\
   if (EQ()) {						\
     current += d; curkey = tmpkey; 			\
     if (myinclude) {d = 0; cl = INLIST_SUCCESS; }	\
     else d = 1;					\
     break;						\
   }							\
   current += d; d <<= 1;				\
 }							\
 /* d => key(current+d) > key */			\
 /* norrowing loop */					\
 while (d > 1) {					\
   int mid;						\
   KEY_TYPE tmpkey;					\
   mid = d >> 1;					\
   tmpkey = EXTRACT_KEY(current + mid);			\
   COMPARE(tmpkey, key);				\
   if (GT()) d = mid;					\
   else if (EQ()) {					\
     current += mid; curkey = tmpkey; 			\
     d = 0;						\
     if (myinclude) { d = 0; cl = INLIST_SUCCESS; }	\
     else d = 1;					\
     break;						\
   }							\
   else { current += mid; d -= mid; curkey = tmpkey; }	\
 }							\
 /* d => key(current+d) > key */			\
 if (d) { ++current; cl = INLIST; }			\
 node->current = current;				\
}
     
   
static Classification _locate(ISearch *isearch, KEY_TYPE key, bool include) {
  /* advance the tree iterator.

  If "include", we try to locate the least "k >= key", otherwise "k > key".
  If we fail, we return "AT_END"; otherwise we set "value" and
  return "INLIST_SUCCESS", if we hit "key" exactly, or "INLIST".

  In case of an exception, we return "-1".
  */
  IBTree	*ib = (IBTree *)isearch->data;
  /* for ACCESS and friends */
  BTree *btree = NULL /* to make gcc happy */;
  /* for COMPARE and friends */
  int cmp; KEY_TYPE key1, key2;
  /* internal */
  int current = 0 /* to make gcc happy */;
  Classification cl = NOT_INLIST;
  KEY_TYPE curkey = (KEY_TYPE) 0 /* to make gcc happy */;

  if (ib->is_deep && ib->current_leaf) {
    /* optimization for the frequent case of lock step access */
    BTNode *leaf = ib->current_leaf;
    current = leaf->current;
    ACCESS(leaf->tree); 
    curkey = EXTRACT_LEAF_KEY(current);
    COMPARE(curkey, key);
    if (include && EQ()) cl = INLIST_SUCCESS;
    else if (GT()) cl = INLIST;
    else {
      /* advance to the next element */
      if (++current >= btree->len) {
	/* no more elements in this leaf */
	BTree *next = BTREE(btree->firstbucket);
	UNACCESS();
	/* ATT: "next" appears to be unreliable (unbelievable) */
	if (!next) return AT_END;
	leaf = setIndependentCurrentLeaf(ib, next);
	current = 0;
	ACCESS(next);
      }
      leaf->current = current;
      curkey = EXTRACT_LEAF_KEY(current);
      COMPARE(curkey, key);
      if (include && EQ()) cl = INLIST_SUCCESS;
      else if (GT()) cl = INLIST;
    }
    UNACCESS();
  }

  if (cl == NOT_INLIST) {
    /* traverse from root */
    int	level = 0, d=0 /* to make gcc happy */;
    BTNode *node, *path;
    bool myinclude, is_leaf; int current, node_len;
    BTree *child;
    while (1) {
      path = ib->path;
      if (level == ib->path_len) {
	node = &path[level - 1];
	ACCESS(node->tree);
	node = pushPath(ib, BTREE(btree->data[node->current-1].child));
	UNACCESS();
	if (!node) return -1;
      } else node = &path[level];
      current = node->current;
      ACCESS(node->tree);
      node_len = btree->len; is_leaf = node->is_leaf;
      if (current >= node_len) {
	UNACCESS();
	if (is_leaf) return AT_END;
	level++;
	continue;
      }
      /* "myinclude" specifies whether we accept "k >= key"
	 (rather then require "k > key") */
      myinclude = is_leaf & include;
      if (is_leaf) {
	BINARY_SEARCH(EXTRACT_LEAF_KEY);
	/* "UNACCESS" outside of loop */
	break;
      }
      BINARY_SEARCH(EXTRACT_NODE_KEY);
      cropPath(ib, ++level);
      child = BTREE(btree->data[current-1].child);
      UNACCESS();
      if (! pushPath(ib, child)) return -1;
    }
    /* at leaf level
       "current" contains the least key "curkey" satisfying our requirements
       include => (current >= node_len or k == key) iff d == 0
     */
    if (current >= node_len) {
      /* not in this leaf -- maybe in the next one */
      BTree *next= BTREE(btree->firstbucket);
      UNACCESS();
      if (!next) return AT_END;
      node = setIndependentCurrentLeaf(ib, next);
      ACCESS(next); curkey = EXTRACT_LEAF_KEY(0); d = 1;
    } else curkey = EXTRACT_LEAF_KEY(current);
    cl = (include && !d) ? INLIST_SUCCESS : INLIST;
    UNACCESS();
  }
  COPY(curkey, isearch->VALUE);
  return cl;
}

static Classification ibtree_advanceTo(ISearch *isearch, KEY_TYPE to) {
  return (isearch->classification = _locate(isearch, to, 1));
}

static Classification ibtree_advanceFrom(ISearch *isearch,
					 bool fromValid,
					 KEY_TYPE from,
					 bool limitValid,
					 KEY_TYPE limit) {
  Classification cl;

  if (! fromValid) {
    IBTree	*ib = (IBTree *) isearch->data;
    BTree	*btree = NULL; /* for "ACCESS" and friends */
    ACCESS(ib->path[0].tree);
    if (ib->is_deep) {
      BTree	*leaf = BTREE(btree->firstbucket);
      UNACCESS();
      ACCESS(leaf);
    }
    if (btree->len) {
      COPY(BUCKET(btree)->keys[0], isearch->VALUE);
      cl = INLIST;
    } else cl = AT_END;
    UNACCESS();
  } else cl = _locate(isearch, from, 0);

  if (cl == INLIST) {
    if (limitValid) {
      /* for COMPARE and friends */
      int cmp; KEY_TYPE key1, key2;
      COMPARE(isearch->VALUE, limit);
      cl = GE();
    } else cl = INLIST_SUCCESS;
  }
  isearch->classification = cl;
  return cl;
}

static int ibtree_setup(ISearch *isearch, PyObject *args) { 
  IBTree	*ib = mycalloc(sizeof(IBTree));
  if (!ib) { PyErr_NoMemory(); return -1; }
  isearch->data = (void *) ib;
  ib->mean_node_size = PyInt_AS_LONG(PyTuple_GET_ITEM(args,2));
  ib->mean_bucket_size = PyInt_AS_LONG(PyTuple_GET_ITEM(args,3));
  if (! pushPath(ib, BTREE(PyTuple_GET_ITEM(args,1)))) return -1;
  ib->is_deep = !ib->path[0].is_leaf;
  return 0;
}

static int ibtree_cleanup(ISearch *isearch) { 
  IBTree	*ib = (IBTree *)isearch->data;
  if (!ib) return 0;
  unsetIndependentCurrentLeaf(ib);
  isearch->data = NULL;
  cropPath(ib, 0);
  free(ib->path);
  free(ib);
  return 0;
}

CAPI_TYPE IBTREE_CAPI_NAME = {
   ibtree_setup, ibtree_cleanup, NULL,
   ibtree_advanceTo, ibtree_advanceFrom
};


long ESTIMATE_SIZE(ISearch *isearch) {
  IBTree	*ib = (IBTree *) isearch->data;
  long		size;
  BTree		*btree = NULL; /* for ACCESS */
  ACCESS(ib->path[0].tree); size = btree->len; UNACCESS();
  if (!ib->is_deep) return size;
  while (1) {
    ACCESS(ib->path[ib->path_len-1].tree);
    if (! pushPath(ib, BTREE(btree->data[0].child))) return -1;
    UNACCESS();
    if (ib->path[ib->path_len-1].is_leaf) break;
    size *= ib->mean_node_size;
  }
  size *= ib->mean_bucket_size;
  return size;
}

PyObject *GET_TREE(ISearch *isearch) { 
  IBTree	*ib = (IBTree *) isearch->data;
  return OBJECT(ib->path[0].tree);
}



/****************************************************************************
*****************************************************************************

Set conversion

*****************************************************************************
****************************************************************************/

static PyObject *settype; 

PyObject *AS_SET(ISearch *isearch) { 
  Bucket *bucket;
  bool	fromValid = 0;
  Classification cl;

  if (!settype) {
    PyObject	*mod;
    mod = PyImport_ImportModule(SETTYPE_MODULE);
    if (!mod) return NULL;
    settype = PyObject_GetAttrString(mod, SETTYPE_CLASS);
    Py_DECREF(mod);
    if (!settype) return NULL;
  }

  bucket = BUCKET(PyObject_CallFunction(settype, ""));
  if (!bucket) return NULL;

  do {
    cl = CAPI(isearch)->advanceFrom(isearch,
				    fromValid, isearch->VALUE,
				    0, (KEY_TYPE) NULL
				    );
    if (cl == -1) goto err;
    if (cl == INLIST_SUCCESS) {
      if (bucket->len >= bucket->size) {
	KEY_TYPE	*keys;
	if (!bucket->size) bucket->size = 4;
	bucket->size <<= 1; /* double the size */
	keys = realloc(bucket->keys, sizeof(KEY_TYPE)*bucket->size);
	if (!keys) {
	  PyErr_NoMemory();
	  goto err;
	}
	bucket->keys = keys;
      }
      COPY_NEW(isearch->VALUE, bucket->keys[bucket->len++]);
      fromValid = 1;
    }
    else break;
  } while (1);
  return OBJECT(bucket);

 err:
  Py_DECREF(bucket);
  return NULL;
}


/****************************************************************************
*****************************************************************************

'_IAnd'

*****************************************************************************
****************************************************************************/

static int _iand_setup(ISearch *isearch, PyObject *args) {
  if (!PyList_CheckExact(args)) return -1;
  if (!PyList_GET_SIZE(args)) {
    PyErr_SetString(PyExc_ValueError, "cannot and zero isearches");
    return -1;
  }
  Py_INCREF(args);
  isearch->data = args;
  return 0;
}

static int _iand_cleanup(ISearch *isearch) { 
  Py_XDECREF(OBJECT(isearch->data)); /* 'X' because of 'unmantle' */
  isearch->data = NULL;
  return 0;
}

static PyObject *_iand_unmantle(ISearch *isearch) { 
  PyObject	*args;

  args = OBJECT(isearch->data);
  isearch->data = NULL;
  return args;
}

static Classification _iand_advanceTo(ISearch *isearch, KEY_TYPE to) {
  int i;
  Classification cl;

  for (i=0; i<PyList_GET_SIZE(isearch->data); i++) {
    ISearch *ss = (ISearch *)PyList_GET_ITEM(isearch->data, i);
    if ((cl = CAPI(ss)->advanceTo(ss, to)) == -1) return -1;
    if (cl != INLIST_SUCCESS) {
      if (cl <= CANDIDATE) {
	COPY(ss->VALUE, isearch->VALUE);
	cl = CANDIDATE;
      }
      return (isearch->classification = cl);
    }
  }
  COPY(to, isearch->VALUE);
  return (isearch->classification = INLIST_SUCCESS);
}

static Classification _iand_advanceFrom(ISearch *isearch,
					bool fromValid, KEY_TYPE from,
					bool limitValid, KEY_TYPE limit
					) {
  int			i, defined;
  Classification	cl;
  KEY_TYPE		to;
  ISearch 		*ss;

 retryNonCandidate:
  ss = (ISearch *) PyList_GET_ITEM(isearch->data, 0);
  cl = CAPI(ss)->advanceFrom(ss, fromValid, from, limitValid, limit);
  if (cl != INLIST_SUCCESS) {
    COPY(ss->VALUE, isearch->VALUE);
    return (isearch->classification = cl);
  }
  to = ss->VALUE;
  defined = 0;
 retryCandidate:
  for (i=0; i<PyList_GET_SIZE(isearch->data); i++) {
    if (i == defined) continue;
    ss = (ISearch *) PyList_GET_ITEM(isearch->data, i);
    cl = CAPI(ss)->advanceTo(ss, to);
    switch (cl) {
    case CANDIDATE:
    case INLIST:
      to = ss->VALUE;
      if (limitValid) {
	/* for COMPARE and friends */
	int cmp; KEY_TYPE key1, key2;
	COMPARE(to, limit);
	if (GE()) {
	  COPY(to, isearch->VALUE);
	  return (isearch->classification = CANDIDATE);
	}
      }
      defined = cl == INLIST ? i : -1;
      goto retryCandidate;
    case INLIST_SUCCESS:
      break;
    case NOT_INLIST:
      from = ss->VALUE; fromValid = 1;
      goto retryNonCandidate;
    default:
      return (isearch->classification = cl);
    }
  }
  COPY(to, isearch->VALUE);
  return (isearch->classification = INLIST_SUCCESS);
}
    

CAPI_TYPE IAND_CAPI_NAME = {
  _iand_setup, _iand_cleanup, _iand_unmantle,
  _iand_advanceTo, _iand_advanceFrom}
;



/****************************************************************************
*****************************************************************************

'_IOr' 

*****************************************************************************
****************************************************************************/

/* simply linked queue link */ 
typedef struct SQLink { 
  struct SQLink	*next;
  ISearch	*search;
} SQLink;

/* simply linked queue */ 
typedef struct SQ {
  SQLink	*last;
} SQ;

typedef struct IOr {
  /* the heap */
  long		heap_size;
  ISearch	**heap;
  /* non candidate management */
  SQ		non_candidates;
  SQ		new_non_candidates;
  /* link management */
  SQLink	*links;
  /* the area we take the links from */
  /* the area we take the heap from */
} IOr;

/* functions manipulation simply linked queues */
static ISearch *sqPop(SQ *sq, SQLink **links) {
  SQLink	*link;
  if (!(link = sq->last)) return NULL;
  if (link == link->next) {
    /* the queue becomes empty */
    sq->last = NULL;
  } else {
    /* take the first element */
    link = link->next; /* the first element */
    sq->last->next = link->next; /* taken out */
  }
  link->next = *links; *links = link; /* add to links */
  return link->search;
}

static void sqPush(SQ *sq, ISearch *search, SQLink **links) { 
  SQLink	*link;

  /* take link from "links" */
  link = *links; *links = link->next;
  
  link->search = search;

  /* add to queue */
  if (sq->last) {
    link->next = sq->last->next; sq->last = sq->last->next = link;
  } else sq->last = link->next = link;
}

/* functions manipulating the heap */ 
#define HEAP_NON_EMPTY(ior) ior->heap_size 

static int heapMoveUp(ISearch **heap, int index) {
  /* "heap" satisfies the heap invariant with the exception of leaf "index".
     Exchange "index" with its parent as long as it is smaller.
     This globally restores the invariant.

     We always store "search" because "COMPARE" could cause a premature
     return and we could get memory management problems would we keep
     it in local variables only.
  */
  /* for COMPARE */
  int cmp; KEY_TYPE key1, key2;
  ISearch	*search = heap[index];
  KEY_TYPE value = search->VALUE;

  while (index > 0) {
    int		parent = (index-1) >> 1;
    COMPARE(value, heap[parent]->VALUE);
    if (GE()) break;
    heap[index] = heap[parent]; heap[parent] = search;
    index = parent;
  }
  return 0;
}

static int heapMoveDown_large(ISearch **heap, int size) { 
  /* "heap" satisfies the heap invariant with the exception of the root.
     We have reason to believe that the root is large compared to
     the other heap elements.
     We remove the root and readjust the tree by recursively moving
     the smallest child into the vacant position until we reach
     a leaf position (this costs us "depth" comparisons). There,
     we put the removed root and than move it up until the heap
     invariant holds. (this costs us at most "depth" comparisons).

     We always store "root" because "COMPARE" could cause a premature
     return and we could get memory management problems would we keep
     it in local variables only.
  */
  ISearch	*root = heap[0];
  int		parent;
  /* for COMPARE */
  int cmp; KEY_TYPE key1, key2;

  for (parent=0 ;;) {
    int		child = (parent << 1) + 1; /* left child */
    if (child >= size) break;
    if (child + 1 < size) {
      /* left child exists */
      COMPARE(heap[child]->VALUE, heap[child+1]->VALUE);
      if (GT()) child++; /* replace with right child */
    }
    /* child now contains the smallest one */
    heap[parent] = heap[child]; heap[child] = root;
    parent = child;
  }
  return heapMoveUp(heap, parent);
}

static int heapMoveDown_small(ISearch **heap, int size) { 
  /* "heap" satisfies the heap invariant with the exception of the root.
     We have reason to believe that the root is small compared to
     the other heap elements.

     We move "root" down replacing it with its smallest
     child until it is not larger than its (up to two)
     children. Each level costs us (up to) two comparisons.

     We always store "root" because "COMPARE" could cause a premature
     return and we could get memory management problems would we keep
     it in local variables only.
  */
  ISearch	*root = heap[0];
  KEY_TYPE	value = root->VALUE;
  int		parent;
  /* for COMPARE */
  int cmp; KEY_TYPE key1, key2;

  for (parent=0 ;;) {
    int		child = (parent << 1) + 1; /* left child */
    if (child >= size) break;
    if (child + 1 < size) {
      /* left child exists */
      COMPARE(heap[child]->VALUE, heap[child+1]->VALUE);
      if (GT()) child++; /* replace with right child */
    }
    /* child now contains the smallest one */
    COMPARE(heap[child]->VALUE, value);
    if (GE()) break;
    heap[parent] = heap[child]; heap[child] = root;
    parent = child;
  }
  return 0;
}


static ISearch *heapPop(IOr *ior) {
  long		n = --ior->heap_size;
  ISearch	**heap = ior->heap, *search = heap[0];

  if (!n) return search;

  heap[0] = heap[n];

  if (heapMoveDown_large(heap, n)) return NULL;
  return search;
}

static int heapPush(IOr *ior, ISearch *search) { 
  long		n = ior->heap_size++;
  ISearch	**heap = ior->heap;

  heap[n] = search;

  return  heapMoveUp(heap, n);
}

static ISearch *heapReplace(IOr *ior, ISearch *search) { 
  long		n = ior->heap_size;
  ISearch	**heap = ior->heap, *rsearch = heap[0];

  heap[0] = search;

  if (heapMoveDown_small(heap, n)) return NULL;
  return rsearch;
}

/* functions for "non_candidates" management */
static void ncSetBoundary(IOr *ior) { 
  /* moves "new_non_candidates" in front of "non_candidates" */
  if (ior->new_non_candidates.last) {
    if (ior->non_candidates.last) {
      SQLink	*first = ior->non_candidates.last->next;
      ior->non_candidates.last->next = ior->new_non_candidates.last->next;
      ior->new_non_candidates.last->next = first;
    } else ior->non_candidates.last = ior->new_non_candidates.last;
    ior->new_non_candidates.last = NULL;
  }
}

static void ncPush(IOr *ior, ISearch *search) { 
  sqPush(&ior->new_non_candidates, search, &ior->links);
}

static ISearch *ncPop(IOr *ior) { 
  return sqPop(&ior->non_candidates, &ior->links);
}

static int ncPushedNonCandidates(IOr *ior) {
  return !!ior->new_non_candidates.last;
}

static int _ior_setup(ISearch *isearch, PyObject *arg) {
  int		i, n;
  IOr		*ior;
  SQLink	*links;
  if (!PyList_CheckExact(arg)) return -1;

  n = PyList_GET_SIZE(arg);

  if (! (ior = (IOr *) mycalloc(sizeof(IOr)
				+ n*sizeof(SQLink) /* for links */
				+ n*sizeof(ISearch *) /* for heap */
				))) {
    PyErr_NoMemory(); return -1;
  }
  isearch->data = ior;

  /* create links */
  links = (SQLink *)(&ior[1]); /* above IOR */
  ior->heap = (ISearch **)(&links[n]); /* above links */
  for (i=0; i<n; i++, links++) {
    ISearch	*ss = (ISearch *)PyList_GET_ITEM(arg, i);

    ior->links = links;
    Py_INCREF(ss); ncPush(ior, ss);
  }
  return 0;
}

#define ISearchVISIT(F) {					\
  ISearch	*ss;						\
  ncSetBoundary(ior);						\
  while (HEAP_NON_EMPTY(ior)) {ss = heapPop(ior); F(ss); }	\
  while ((ss = ncPop(ior))) F(ss);				\
}


static int _ior_cleanup(ISearch *isearch) { 
  IOr		*ior = (IOr *)isearch->data;
  isearch->data = 0;

  ISearchVISIT(Py_DECREF);
  free(ior);
  return 0;
}

static PyObject *_ior_unmantle(ISearch *isearch) { 
  PyObject	*searches = PyList_New(0);
  IOr		*ior = (IOr *)isearch->data;

  if (!searches) return NULL;

# define APPEND(is) do {					\
    if (PyList_Append(searches, (PyObject *)is)) return NULL;	\
  } while (0)							\

  ISearchVISIT(APPEND);
# undef APPEND
  return searches;
}

#undef ISearchVISIT 

static Classification _ior_advanceTo(ISearch *isearch, KEY_TYPE to) {
  IOr		*ior = (IOr *) isearch->data;
  ISearch	**heap = ior->heap, *ss = NULL /* to make gcc happy */;
  bool		found = 0;
  Classification	cl = -1;
  /* for COMPARE */
  int cmp; KEY_TYPE key1, key2;

  ncSetBoundary(ior);

  /* update heap until we either find a hit or all values > "to". */
  while (HEAP_NON_EMPTY(ior)) {
    ss = heap[0];
    COMPARE(ss->VALUE, to);
    if (GT()) break; /* larger */
    if (EQ() && ss->classification <= INLIST) {cl = INLIST_SUCCESS; break; }
    cl = CAPI(ss)->advanceTo(ss, to);
    if (cl == -1) return -1;
    if (cl <= CANDIDATE) {
      if (! heapReplace(ior, ss)) return -1;
      if (cl == INLIST_SUCCESS) {found = 1; break; }
    } else {
      if (! heapPop(ior)) return -1;
      if (cl == NOT_INLIST) ncPush(ior, ss);
      else Py_DECREF(ss); /* "AT_END" */
    }
  }

  if (cl != INLIST_SUCCESS) {
    /* check non_candidates */
    while ((ss = ncPop(ior))) {
      if ((cl = CAPI(ss)->advanceTo(ss, to)) == -1) return -1;
      if (cl <= CANDIDATE) {
	if (heapPush(ior, ss)) return -1;
	if (cl == INLIST_SUCCESS) break;
      } else if (cl == NOT_INLIST) ncPush(ior, ss);
      else Py_DECREF(ss); /* "AT_END" */
    }
    if (cl != INLIST_SUCCESS) {
      /* no hit found */
      if (ncPushedNonCandidates(ior))
	return (isearch->classification = NOT_INLIST);
      if (HEAP_NON_EMPTY(ior)) {ss = heap[0]; cl = CANDIDATE; }
      else return (isearch->classification = AT_END);
    }
  }
  isearch->classification = cl; COPY(ss->VALUE, isearch->VALUE);
  return cl;
}

static Classification
_ior_advanceFrom(ISearch *isearch,
		 bool fromValid, KEY_TYPE from,
		 bool limitValid, KEY_TYPE limit) {
  IOr		*ior = (IOr *) isearch->data;
  ISearch	**heap = ior->heap, *ss;
  KEY_TYPE	value = (KEY_TYPE) 0 /* to make gcc happy */;
  Classification cl = -1, clt;
  /* for COMPARE */
  int cmp; KEY_TYPE key1, key2;

  ncSetBoundary(ior);

  /* update heap until it contains only values "> from"
     and the bottom element is a potential hit.
  */
  while (HEAP_NON_EMPTY(ior)) {
    bool unchanged = 0;
    ss = heap[0]; value = ss->VALUE;
    /* Note: when something is in the heap, we can assume "fromValid" */
    COMPARE(value, from);
    if (GT()) {
      /* large enough */
      if (cl == -1 /* no hit found yet */
	  && limitValid) {
	/* "value" may be beyond "limit" */
	COMPARE(value, limit);
	if (GE()) { cl = CANDIDATE; break; }
      }
      /* either we already found a hit (in which case "value" cannot be larger)
	 or there is no limit or "value" is below "limit" */
      if (ss->classification == CANDIDATE) {
	/* must check whether it truely is in the list */
	if ((clt = CAPI(ss)->advanceTo(ss, value)) == -1) return -1;
	if (!clt) unchanged = 1;
	if (clt == NOT_INLIST) {
	  /* skip this bad value */
	  /* we may already have reached "limit" in which case we cannot
	     use 'advanceFrom' to skip over the value.
	     However, in this case, "cl == INLIST_SUCCESS" and
	     "value == limit" */
	  if (limitValid) {
	    COMPARE(value, limit);
	    if (GE()) {
	      clt = INLIST_SUCCESS; unchanged = 1;
	    } else goto skip_via_advanceFrom;
	  } else {
	  skip_via_advanceFrom:
	    if ((clt = CAPI(ss)->advanceFrom(ss, 1, value, limitValid, limit)) == -1)
	      return -1;
	  }
	}
      } else { clt = INLIST_SUCCESS; unchanged = 1; } /* "value" below "limit" */
    } else {
      /* advance into the legal range */
      if ((clt = CAPI(ss)->advanceFrom(ss, fromValid, from, limitValid, limit)) == -1)
	return -1;
    }
    if (clt <= CANDIDATE) {
      if (clt == INLIST_SUCCESS) {
	/* Note: any hit is better than the previous one */
	limitValid = 1; limit = ss->VALUE; cl = clt;
      }
      if (unchanged) break;
      if (! heapReplace(ior, ss)) return -1;
    } else {
      if (! heapPop(ior)) return -1;
      /* cannot happen */
      /* if (clt == NOT_INLIST) ncPush(ior, ss);
	 else */
      Py_DECREF(ss); /* "AT_END" */
    }
  }

  /* process non candiates */
  while ((ss = ncPop(ior))) {
    if ((clt = CAPI(ss)->advanceFrom(ss, fromValid, from, limitValid, limit))
	== -1) return -1;
    if (clt <= CANDIDATE) {
      if (heapPush(ior, ss)) return -1;
      if (clt == INLIST_SUCCESS) {
	/* Note: any hit is better than the previous one */
	limitValid = 1; limit = ss->VALUE; cl = clt;
      } else if (cl == -1) cl = CANDIDATE;
    } else /* if (clt == NOT_INLIST) ncPush(ior, ss);
	      else */ Py_DECREF(ss); /* "AT_END" */
  }
  
  /* prepare result */
  if (cl == -1)
    /* we did not find a hit nor a candidate -- especially, the heap is
       empty */
    cl = AT_END;
    /* cl = ncPushedNonCandidates(ior) ? NOT_INLIST : AT_END; */
  else if (cl != INLIST_SUCCESS) {
    /* a CANDIDATE -- especially, the heap is not empty */
    /*if (ncPushedNonCandidates(ior)) cl = NOT_INLIST;
      else */
    value = heap[0]->VALUE;
  } else value = limit;

  if (cl <= CANDIDATE) COPY(value, isearch->VALUE);
  isearch->classification = cl;
  return cl;
}

CAPI_TYPE IOR_CAPI_NAME = {
  _ior_setup, _ior_cleanup, _ior_unmantle,
  _ior_advanceTo, _ior_advanceFrom};
