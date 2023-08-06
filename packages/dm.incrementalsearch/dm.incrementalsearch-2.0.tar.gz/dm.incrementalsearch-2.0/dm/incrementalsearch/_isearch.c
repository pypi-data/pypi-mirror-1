/* Copyright (C) 2005 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
  see "LICENSE.txt" for details
*/
/*	$Id: _isearch.c,v 1.1.1.1 2008/06/27 19:21:39 dieter Exp $
ISearch base classes.

This cooperates with capi implementations in "_isearch_int.c",
"_isearch_obj.c" and "_isearch_long.c".

To avoid cyclic module imports, we do not follow the advice
to communicate via Python modules only. Instead, we
use global (linker resolved) symbols.
This should work, as we know we are inside the same shared object.
We prefix them with 'DM_IncrementalSearch2_' to make name clashes very
unlikely.

We do not participate in cyclic garbage collection because
it is highly unlikely that an 'ISearch' is part of a cycle.
*/

#include "_isearch.h"
#include <structmember.h>

#ifdef DEBUG_INT
/* temporary to facilitate debugging */
ISearchCAPI_obj DM_IncrementalSearch2_ibtree_capi_obj={};
ISearchCAPI_obj DM_IncrementalSearch2_iand_capi_obj={};
ISearchCAPI_obj DM_IncrementalSearch2_ior_capi_obj={};
PyObject *DM_IncrementalSearch2_asSet_obj(ISearch *isearch) {return NULL;}
long DM_IncrementalSearch2_ibtree_estimateSize_obj(ISearch *isearch) {return 0;}
/* borrowed */
PyObject *DM_IncrementalSearch2_ibtree_getTree_obj(ISearch *isearch) {return NULL;}
int DM_IncrementalSearch2_init_obj(void){return 0;}
# endif /* DEBUG_INT */



/****************************************************************************
*****************************************************************************

The 'Unspecified' singleton.

*****************************************************************************
****************************************************************************/
/* We implement it as a type
   Its only useful operation is 'is' (and 'not is').
 */

static PyTypeObject Unspecified = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,
	"dm.incrementalsearch._isearch.Unspecified",
	0,
	0,
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,			 		/* tp_getattr */
	0,			 		/* tp_setattr */
	0,					/* tp_compare */
	0,		 			/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,			/* tp_flags */
	"'Unspecified' value for ISearches",	/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	0,					/* tp_new */
	0,					/* tp_free */
};


/****************************************************************************
*****************************************************************************

Generic (auxiliary) functions (used by several ISearches)

*****************************************************************************
****************************************************************************/

/* check, the ISearch has been initialized */
static int check(ISearch *isearch) {
  if (! isearch->capi) {
    PyErr_SetString(PyExc_SystemError, "operation on uninitialized ISearch");
    return -1;
  }
  return 0;
}

static int genericCleanup(ISearch *isearch) {
  CAPI_Head	*capi = isearch->capi;
  Keytype	keytype = isearch->keytype;

  if (!keytype) return 0;
  if (capi->cleanup && capi->cleanup(isearch)) return -1;
  isearch->keytype = 0; isearch->capi = NULL;
  if (keytype == OBJECT) {
    Py_DECREF(isearch->value.objValue);
  }
  return 0;
}

static int genericSetup(ISearch *isearch, Keytype keytype,
			ISearchCAPI_int *capi_int,
			ISearchCAPI_obj *capi_obj,
			ISearchCAPI_long *capi_long,
			PyObject	*arg
			) {
  CAPI_Head	*capi;

  if (keytype != INT && keytype != OBJECT && keytype != LONG) {
    PyErr_SetString(PyExc_TypeError, "Keytype must be INT, OBJECT or LONG");
    return -1;
  }
  if (genericCleanup(isearch)) return -1;
  isearch->keytype = keytype;
  isearch->classification = AT_START;
  isearch->estimatedSize = -1;
  if (keytype == INT) {
    isearch->value.intValue = 0;
    capi = (CAPI_Head *) capi_int;
  } else if (keytype == LONG) {
    isearch->value.longValue = 0;
    capi = (CAPI_Head *) capi_long;
  } else {
    Py_INCREF(&Unspecified);
    isearch->value.objValue = (PyObject *)&Unspecified;
    capi = (CAPI_Head *) capi_obj;
  }
  isearch->capi = capi;
  if (capi->setup) return capi->setup(isearch, arg);
  return 0;
}



/****************************************************************************
*****************************************************************************

'ISearch', the (abstract) base class for all incremental searches.

*****************************************************************************
****************************************************************************/


/* C-API defined in terms of Python implementation */
#define defineFunction(NAME, KEYTYPE, FORMAT)			\
static								\
Classification NAME(ISearch *isearch, KEYTYPE to) {		\
  PyObject *r;							\
  Classification c; 						\
  r = PyObject_CallMethod((PyObject *)isearch, "advanceTo",	\
                          FORMAT, to);				\
  c = r ? PyInt_AS_LONG(r) : -1;				\
  Py_XDECREF(r);						\
  return c;							\
}
defineFunction(isearch_advanceTo_int, int, "i")
defineFunction(isearch_advanceTo_obj, PyObject *, "O")
defineFunction(isearch_advanceTo_long, PY_LONG_LONG, "L")
#undef defineFunction

#define defineFunction(NAME, KEYTYPE, FORMAT)				\
static									\
Classification NAME(ISearch *isearch,					\
		    bool fromValid,					\
		    KEYTYPE from,					\
		    bool limitValid,					\
		    KEYTYPE limit) {					\
  PyObject *mfrom = NULL, *mlimit = NULL, *r=NULL;			\
  Classification c;							\
  mfrom = fromValid							\
    ? Py_BuildValue(FORMAT, from) : Py_BuildValue("O", &Unspecified);	\
  mlimit = limitValid							\
    ? Py_BuildValue(FORMAT, limit) : Py_BuildValue("O", &Unspecified);	\
  if (!mfrom || !mlimit) goto err;					\
  r = PyObject_CallMethod((PyObject *)isearch, "advanceFrom",		\
                          "OO", mfrom, mlimit);				\
  if (!r) goto err;							\
  c = PyInt_AS_LONG(r);							\
  goto finish;								\
 err:									\
  c = -1;								\
 finish:								\
  Py_XDECREF(mfrom); Py_XDECREF(mlimit); Py_XDECREF(r);			\
  return c;								\
}
defineFunction(isearch_advanceFrom_int, int, "i")
defineFunction(isearch_advanceFrom_obj, PyObject *, "O")
defineFunction(isearch_advanceFrom_long, PY_LONG_LONG, "L")
#undef defineFunction

static ISearchCAPI_int isearch_capi_int = {
  NULL, NULL, NULL, isearch_advanceTo_int, isearch_advanceFrom_int,
};

static ISearchCAPI_obj isearch_capi_obj = {
  NULL, NULL, NULL, isearch_advanceTo_obj, isearch_advanceFrom_obj,
};

static ISearchCAPI_long isearch_capi_long = {
  NULL, NULL, NULL, isearch_advanceTo_long, isearch_advanceFrom_long,
};

/* Members */
#define OFF(x) offsetof(ISearch, x)

static PyMemberDef isearch_memberlist[] = {
  {"keytype",	T_INT,		OFF(keytype), RO,},
  {"classification",	T_INT,	OFF(classification),	0,
   "classification result of last 'advanceTo/From' call"},
  {"estimatedSize",	T_INT,		OFF(estimatedSize), 0,
   "estimated size of the isearch or -1, if unknown"},
  {NULL}	/* Sentinel */
};

/* Attribute Access

We use it for type specific access to "value"
*/

static PyObject *isearch_getValue(PyObject *self, void *unused) {
  ISearch	*myself = (ISearch *) self;
  if (check(myself)) return NULL;
  if (myself->keytype == INT) return PyInt_FromLong(myself->value.intValue);
  else if (myself->keytype == LONG) return PyLong_FromLongLong(myself->value.longValue);
  else {
    PyObject	*value = myself->value.objValue;
    Py_INCREF(value);
    return value;
  }
}

static int isearch_setValue(PyObject *self, PyObject *value, void *unused) {
  ISearch	*myself = (ISearch *) self;
  int		cr = check(myself);

  if (cr) return cr;
  if (myself->keytype == INT) {
    long	myvalue = PyInt_AsLong(value);
    if (PyErr_Occurred()) return -1;
    myself->value.intValue = myvalue;
  } else if (myself->keytype == LONG) {
    PY_LONG_LONG	myvalue = PyLong_AsLongLong(value);
    if (PyErr_Occurred()) return -1;
    myself->value.longValue = myvalue;
  } else {
    PyObject	*tmp = myself->value.objValue;
    Py_INCREF(value); myself->value.objValue = value;
    Py_DECREF(tmp);
  }
  return 0;
}

static PyGetSetDef isearch_getset[] = { 
  {"value", isearch_getValue, isearch_setValue,
   "The current value", NULL },
  {NULL},  /* sentinel */
};
  

#if 0 /* see whether we get along without this function */
static PyObject *
isearch_new(PyTypeObject *type, PyObject *args, PyObject *kw) {

  return type->tp_alloc(type, 0);
}
#endif /* 0 */


static int
isearch_init(PyObject *self, PyObject *args, PyObject *kw) {
  ISearch *myself = (ISearch *) self;
  static char *kwlist[] = {"keytype", 0};
  int keytype;
  if (!PyArg_ParseTupleAndKeywords(args, kw, "i:ISearch", kwlist, &keytype))
    return -1;
  return genericSetup(myself, keytype,
		      &isearch_capi_int, &isearch_capi_obj, &isearch_capi_long,
		      NULL);
}

PyDoc_STRVAR(isearch_init_doc,
"__init__(keytype)\n"
"\n"
"Initialize the isearch for use with *keytype* keys (either 'INT' or 'OBJECT' constant).\n"
	     );

static void
isearch_dealloc(PyObject *self) {
  ISearch	*myself = (ISearch *)self;

  genericCleanup(myself);
  self->ob_type->tp_free((PyObject *) self);
}

static PyObject *
isearch_iter(PyObject *self) {
  Py_INCREF(self);
  return self;
}

static PyObject *
isearch_next(PyObject *self) {
  ISearch *myself = (ISearch *) self;
  PyObject *r = NULL,
    *start = NULL;
  int cl = myself->classification;

  if (cl == AT_END) return NULL;
  if (cl == AT_START) {
    start = (PyObject *) &Unspecified; Py_INCREF(start);
  } else if (! (start = PyObject_GetAttrString(self, "value"))) return NULL;
  r = PyObject_CallMethod(self, "advanceFrom", "OO", start, (PyObject *)&Unspecified);
  Py_DECREF(start);
  if (! r) return NULL;
  Py_DECREF(r);
  if (myself->classification == AT_END) return NULL; /* StopIteration */
  return PyObject_GetAttrString(self, "value");
}


static PyObject *
isearch_asSet(PyObject *self, PyObject *unused) {
  ISearch	*myself = (ISearch *)self;
  if (check(myself)) return NULL;
  return (
	  myself->keytype == INT
	  ? DM_IncrementalSearch2_asSet_int
	  : myself->keytype == OBJECT
	    ? DM_IncrementalSearch2_asSet_obj
	    : DM_IncrementalSearch2_asSet_long)(myself);
}

PyDoc_STRVAR(isearch_asSet_doc,
"asSet() -> usually an 'IISet' or 'OOSet' depending on keytype.\n"
"\n"
"The set containing the elements of the isearch.\n\n"
"Note that for efficiency reasons an 'IBTree' simply returns\n"
"the corresponding tree, which need not be of 'Set' type.\n"
	     );

static PyObject *
  isearch_advanceTo(PyObject *self, PyObject *unused) {
  PyErr_SetString(PyExc_NotImplementedError, "advanceTo");
  return NULL;
}

PyDoc_STRVAR(isearch_advanceTo_doc,
"advanceTo(key) -> classification: advance to *key*.\n"
"\n"
"The isearch may in fact advance to the least element of the isearch\n"
"at or above *key*.\n"
"The classification tells about the outcome of the advance.\n"
	     );

static PyObject *
  isearch_advanceFrom(PyObject *self, PyObject *unused) {
  PyErr_SetString(PyExc_NotImplementedError, "advanceFrom");
  return NULL;
}

PyDoc_STRVAR(isearch_advanceFrom_doc,
"advanceFrom(from, limit) -> classification: advance from *from*, not beyond *limit*.\n"
"\n"
"advance to the least isearch element above *from* if it is below *limit*.\n"
"The isearch may advance to the element even if it is beyond *limit*, but\n"
"it is not obliged to do so.\n"
"The classification tells about the outcome of the advance.\n"
	     );

static PyMethodDef isearch_methods[] = {
  {"asSet", isearch_asSet, METH_NOARGS, isearch_asSet_doc},
  {"advanceTo", isearch_advanceTo, METH_VARARGS, isearch_advanceTo_doc},
  {"advanceFrom", isearch_advanceFrom, METH_VARARGS, isearch_advanceFrom_doc},
  {NULL}
};


static PyTypeObject ISearch_Type = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,
	"dm.incrementalsearch._isearch.ISearch",
	sizeof(ISearch),
	0,
	isearch_dealloc,			/* tp_dealloc */
	0,					/* tp_print */
	0,			 		/* tp_getattr */
	0,			 		/* tp_setattr */
	0,					/* tp_compare */
	0,		 			/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	isearch_init_doc,			/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	isearch_iter,				/* tp_iter */
	isearch_next,				/* tp_iternext */
	isearch_methods,			/* tp_methods */
	isearch_memberlist,			/* tp_members */
	isearch_getset,				/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	isearch_init,				/* tp_init */
	0,					/* tp_alloc */
	PyType_GenericNew,			/* tp_new */
	0,					/* tp_free */
};


/****************************************************************************
*****************************************************************************

'ISearch_C' the (abstract) base class for C-implemented ISearches.

  It implements the Python API via its C API.

*****************************************************************************
****************************************************************************/

#define IDENTITY(x)	x

#define defineFunction(NAME, CAPITYPE, KEYTYPE, TOKEY)			\
static									\
Classification NAME(ISearch *isearch, CAPI_Head *capi, PyObject* to) {	\
  KEYTYPE mto = TOKEY(to);						\
  if (PyErr_Occurred()) return -1;					\
  return ((CAPITYPE *)capi)->advanceTo(isearch, mto);			\
}

defineFunction(isearch_c_advanceTo_int, ISearchCAPI_int, long, PyInt_AsLong)
defineFunction(isearch_c_advanceTo_obj, ISearchCAPI_obj, PyObject *, IDENTITY)
defineFunction(isearch_c_advanceTo_long, ISearchCAPI_long, PY_LONG_LONG, PyLong_AsLongLong)
#undef defineFunction

#define defineFunction(NAME, CAPITYPE, KEYTYPE, TOKEY)		\
static								\
Classification NAME(ISearch *isearch,				\
                    CAPI_Head *capi,				\
		    bool fromValid,				\
		    PyObject *from,				\
		    bool limitValid,				\
		    PyObject *limit) {				\
  KEYTYPE mfrom = fromValid ? TOKEY(from) : (KEYTYPE) 0;	\
  KEYTYPE mlimit = limitValid ? TOKEY(limit) : (KEYTYPE) 0;	\
  if (PyErr_Occurred()) return -1;				\
  return ((CAPITYPE *)capi)->advanceFrom(isearch,		\
					 fromValid, mfrom,	\
					 limitValid, mlimit	\
					 );			\
}

defineFunction(isearch_c_advanceFrom_int, ISearchCAPI_int, long, PyInt_AsLong)
defineFunction(isearch_c_advanceFrom_obj, ISearchCAPI_obj, PyObject *, IDENTITY)
defineFunction(isearch_c_advanceFrom_long, ISearchCAPI_long, PY_LONG_LONG, PyLong_AsLongLong)
#undef defineFunction

#undef IDENTITY

static PyObject *
  isearch_c_advanceTo(PyObject *self, PyObject *args) {
  ISearch *myself = (ISearch *)self;
  PyObject *to = NULL;
  Classification c;

  if (check(myself)) return NULL;

  if (!PyArg_ParseTuple(args, "O", &to)) return NULL;

  c = (myself->keytype == INT
       ? isearch_c_advanceTo_int
       : myself->keytype == OBJECT
       ?isearch_c_advanceTo_obj
       :isearch_c_advanceTo_long
       )(myself, myself->capi, to);
  if (c == -1) return NULL;
  return PyInt_FromLong(c);
}

static PyObject *
  isearch_c_advanceFrom(PyObject *self, PyObject *args) {
  ISearch *myself = (ISearch *)self;
  PyObject *from = NULL, *limit = NULL;
  bool fromValid, limitValid;
  Classification c;

  if (check(myself)) return NULL;

  if (!PyArg_ParseTuple(args, "OO", &from, &limit)) return NULL;

  fromValid = from != (PyObject *) &Unspecified;
  limitValid = limit != (PyObject *) &Unspecified;

  c = (myself->keytype == INT
       ? isearch_c_advanceFrom_int
       : myself->keytype == OBJECT
       ?isearch_c_advanceFrom_obj
       :isearch_c_advanceFrom_long
       )(myself, myself->capi, fromValid, from, limitValid, limit);
  if (c == -1) return NULL;
  return PyInt_FromLong(c);
}


static PyMethodDef isearch_c_methods[] = {
  {"advanceTo", isearch_c_advanceTo, METH_VARARGS, isearch_advanceTo_doc},
  {"advanceFrom", isearch_c_advanceFrom, METH_VARARGS, isearch_advanceFrom_doc},
  {NULL}
};


static PyTypeObject ISearch_c_Type = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,
	"dm.incrementalsearch._isearch.ISearch_c",
	0,
	0,
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,			 		/* tp_getattr */
	0,			 		/* tp_setattr */
	0,					/* tp_compare */
	0,		 			/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	0,					/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	isearch_c_methods,			/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	&ISearch_Type,				/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	0,					/* tp_init */
	0,					/* tp_alloc */
	0 /*isearch_new */,			/* tp_new */
	0,					/* tp_free */
};


/****************************************************************************
*****************************************************************************

'_IBTree' -- a 'BTrees' object as an ISearch

*****************************************************************************
****************************************************************************/

static int
  ibtree_init(PyObject *self, PyObject *args, PyObject *kw) {
  ISearch	*myself = (ISearch *) self;
  Keytype	keytype;
  PyObject	*tree = NULL;
  long		node_size, bucket_size;

  if (! PyArg_ParseTuple(args, "iOii", &keytype, &tree,
			 &node_size, &bucket_size)
      ) return -1;

  return genericSetup(myself, keytype,
		      &DM_IncrementalSearch2_ibtree_capi_int,
		      &DM_IncrementalSearch2_ibtree_capi_obj,
		      &DM_IncrementalSearch2_ibtree_capi_long,
		      args
		      );
}

/* override 'estimatedSize' to compute it lazily */ 
static PyObject *
  ibtree_getEstimatedSize(PyObject *self, void *unused) {
  ISearch	*myself = (ISearch *) self;

  if (myself->estimatedSize == -1) {
    if (check(myself)) return NULL;
    if (myself->classification != AT_START) {
      PyErr_SetString(PyExc_ValueError, "Size cannot be determined after iteration has started");
      return NULL;
    }
    myself->estimatedSize =
      (myself->keytype == INT
       ? DM_IncrementalSearch2_ibtree_estimateSize_int
       : myself->keytype == OBJECT
       ?DM_IncrementalSearch2_ibtree_estimateSize_obj
       :DM_IncrementalSearch2_ibtree_estimateSize_long
       )(myself);
    if (myself->estimatedSize == -1) return NULL;
  }
  return PyInt_FromLong(myself->estimatedSize);
}


static PyGetSetDef ibtree_getset[] = { 
  {"estimatedSize", ibtree_getEstimatedSize, NULL,
   "The estimated size", NULL },
  {NULL},  /* sentinel */
};

/* override 'asSet' for efficiency reasons */ 
static PyObject *
  ibtree_asSet(PyObject *self, PyObject *unused) {
  ISearch	*myself = (ISearch *) self;
  PyObject	*tree;

  if (check(myself)) return NULL;

  tree = (myself->keytype == INT
	  ? DM_IncrementalSearch2_ibtree_getTree_int
	  : myself->keytype == OBJECT
	  ? DM_IncrementalSearch2_ibtree_getTree_obj
	  : DM_IncrementalSearch2_ibtree_getTree_long
	  )(myself);
  Py_INCREF(tree);
  return tree;
}

static PyMethodDef ibtree_methods[] = {
  {"asSet", ibtree_asSet, METH_NOARGS, isearch_asSet_doc},
  {NULL}
};

static PyTypeObject IBTree_Type = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,
	"dm.incrementalsearch._isearch._IBTree",
	0,
	0,
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,			 		/* tp_getattr */
	0,			 		/* tp_setattr */
	0,					/* tp_compare */
	0,		 			/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	0,					/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	ibtree_methods,				/* tp_methods */
	0,					/* tp_members */
	ibtree_getset,				/* tp_getset */
	&ISearch_c_Type,			/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	ibtree_init,				/* tp_init */
	0,					/* tp_alloc */
	PyType_GenericNew,			/* tp_new */
	0,					/* tp_free */
};


/****************************************************************************
*****************************************************************************

Composite ISearches ('IAnd' and 'IOr')

*****************************************************************************
****************************************************************************/

static PyObject *
  composite_unmantle(PyObject *self, PyObject *unused) {
  ISearch	*myself = (ISearch *) self;
  PyObject	*subsearches = NULL;

  if (check(myself)) return NULL;

  subsearches = myself->capi->unmantle(myself);
  genericCleanup(myself);
  return subsearches;
}

PyDoc_STRVAR(composite_unmantle_doc,
"unmantle() -> subsearches\n"
"\n"
"unmantle the isearch and return its subsearches.\n"
	     );



static PyMethodDef composite_methods[] = {
  {"unmantle", composite_unmantle, METH_NOARGS, composite_unmantle_doc},
  {NULL}
};


static int
  iand_init(PyObject *self, PyObject *args, PyObject *unused) {
  ISearch	*myself = (ISearch *) self;
  Keytype	keytype;
  PyObject	*subsearches;

  if (!PyArg_ParseTuple(args, "iO", &keytype, &subsearches)) return -1;

  return genericSetup(myself, keytype,
		      &DM_IncrementalSearch2_iand_capi_int,
		      &DM_IncrementalSearch2_iand_capi_obj,
		      &DM_IncrementalSearch2_iand_capi_long,
		      subsearches
		      );
}


static PyTypeObject _IAnd_Type = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,
	"dm.incrementalsearch._isearch._IAnd",
	0,
	0,
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,			 		/* tp_getattr */
	0,			 		/* tp_setattr */
	0,					/* tp_compare */
	0,		 			/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	0,					/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	composite_methods,			/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	&ISearch_c_Type,			/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	iand_init,				/* tp_init */
	0,					/* tp_alloc */
	PyType_GenericNew,			/* tp_new */
	0,					/* tp_free */
};


static int
  ior_init(PyObject *self, PyObject *args, PyObject *unused) {
  ISearch	*myself = (ISearch *) self;
  Keytype	keytype;
  PyObject	*subsearches;

  if (!PyArg_ParseTuple(args, "iO", &keytype, &subsearches)) return -1;

  return genericSetup(myself, keytype,
		      &DM_IncrementalSearch2_ior_capi_int,
		      &DM_IncrementalSearch2_ior_capi_obj,
		      &DM_IncrementalSearch2_ior_capi_long,
		      subsearches
		      );
}


static PyTypeObject _IOr_Type = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,
	"dm.incrementalsearch._isearch._IOr",
	0,
	0,
	0,					/* tp_dealloc */
	0,					/* tp_print */
	0,			 		/* tp_getattr */
	0,			 		/* tp_setattr */
	0,					/* tp_compare */
	0,		 			/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	0,					/* tp_getattro */
	0,					/* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	0,					/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	composite_methods,			/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	&ISearch_c_Type,			/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	ior_init,				/* tp_init */
	0,					/* tp_alloc */
	PyType_GenericNew,			/* tp_new */
	0,					/* tp_free */
};













/****************************************************************************
*****************************************************************************

The module

*****************************************************************************
****************************************************************************/

PyDoc_STRVAR(isearch_doc,
	     "dm.incrementalsearch._isearch -- C implementation"
	     );

static PyMethodDef module_methods[] = { {NULL} };


PyMODINIT_FUNC init_isearch(void) {
  PyObject *m;

  if (DM_IncrementalSearch2_init_int()) return;
  if (DM_IncrementalSearch2_init_obj()) return;
  if (DM_IncrementalSearch2_init_long()) return;

  if (PyType_Ready(&ISearch_Type)) return;
  if (PyType_Ready(&ISearch_c_Type)) return;
  if (PyType_Ready(&IBTree_Type)) return;
  if (PyType_Ready(&_IAnd_Type)) return;
  if (PyType_Ready(&_IOr_Type)) return;

  if (! (m = Py_InitModule3("_isearch", module_methods, isearch_doc)))
    return;
  Py_INCREF(&Unspecified);
  if (PyModule_AddObject(m, "Unspecified", (PyObject *)&Unspecified)) return;
  Py_INCREF(&ISearch_Type);
  if (PyModule_AddObject(m, "ISearch", (PyObject *)&ISearch_Type)) return;
  Py_INCREF(&IBTree_Type);
  if (PyModule_AddObject(m, "_IBTree", (PyObject *)&IBTree_Type)) return;
  Py_INCREF(&_IAnd_Type);
  if (PyModule_AddObject(m, "_IAnd", (PyObject *)&_IAnd_Type)) return;
  Py_INCREF(&_IOr_Type);
  if (PyModule_AddObject(m, "_IOr", (PyObject *)&_IOr_Type)) return;
}
