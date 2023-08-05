
#include "Python.h"
#include "structmember.h"

#ifndef Py_ssize_t
#define Py_ssize_t ssize_t
#endif

/* Py_VISIT and Py_CLEAR are defined here to be compatible with Python 2.3 */

/* Utility macro to help write tp_traverse functions.
 * To use this macro, the tp_traverse function must name its arguments
 * "visit" and "arg".  This is intended to keep tp_traverse functions
 * looking as much alike as possible.
 */
#ifndef Py_VISIT
#define Py_VISIT(op)							\
        do { 								\
                if (op) {						\
                        int vret = visit((PyObject *)(op), arg);	\
                        if (vret)					\
                                return vret;				\
                }							\
        } while (0)
#endif

#ifndef Py_CLEAR
#define Py_CLEAR(op)				\
        do {                            	\
                if (op) {			\
                        PyObject *tmp = (PyObject *)(op);	\
                        (op) = NULL;		\
                        Py_DECREF(tmp);		\
                }				\
        } while (0)
#endif

/* partial type by Hye-Shik Chang <perky@FreeBSD.org>
   with adaptations by Raymond Hettinger <python@rcn.com>
   
   map, filter, foldr, foldl, id, the compose type and the flip type
   by Collin Winter <collinw@gmail.com>

   Copyright (c) 2004-2006 Python Software Foundation.
   All rights reserved.
*/

/* partial object **********************************************************/

typedef struct {
	PyObject_HEAD
	PyObject *fn;
	PyObject *args;
	PyObject *kw;
	PyObject *dict;
	PyObject *weakreflist; /* List of weak references */
} partialobject;

static PyTypeObject partial_type;

static PyObject *
partial_new(PyTypeObject *type, PyObject *args, PyObject *kw)
{
	PyObject *func;
	partialobject *pto;

	if (PyTuple_GET_SIZE(args) < 1) {
		PyErr_SetString(PyExc_TypeError,
				"type 'partial' takes at least one argument");
		return NULL;
	}

	func = PyTuple_GET_ITEM(args, 0);
	if (!PyCallable_Check(func)) {
		PyErr_SetString(PyExc_TypeError,
				"the first argument must be callable");
		return NULL;
	}

	/* create partialobject structure */
	pto = (partialobject *)type->tp_alloc(type, 0);
	if (pto == NULL)
		return NULL;

	pto->fn = func;
	Py_INCREF(func);
	pto->args = PyTuple_GetSlice(args, 1, INT_MAX);
	if (pto->args == NULL) {
		pto->kw = NULL;
		Py_DECREF(pto);
		return NULL;
	}
	if (kw != NULL) {
		pto->kw = PyDict_Copy(kw);
		if (pto->kw == NULL) {
			Py_DECREF(pto);
			return NULL;
		}
	} else {
		pto->kw = Py_None;
		Py_INCREF(Py_None);
	}

	pto->weakreflist = NULL;
	pto->dict = NULL;

	return (PyObject *)pto;
}

static void
partial_dealloc(partialobject *pto)
{
	PyObject_GC_UnTrack(pto);
	if (pto->weakreflist != NULL)
		PyObject_ClearWeakRefs((PyObject *) pto);
	Py_XDECREF(pto->fn);
	Py_XDECREF(pto->args);
	Py_XDECREF(pto->kw);
	Py_XDECREF(pto->dict);
	pto->ob_type->tp_free(pto);
}

static PyObject *
partial_call(partialobject *pto, PyObject *args, PyObject *kw)
{
	PyObject *ret;
	PyObject *argappl = NULL, *kwappl = NULL;

	assert (PyCallable_Check(pto->fn));
	assert (PyTuple_Check(pto->args));
	assert (pto->kw == Py_None  ||  PyDict_Check(pto->kw));

	if (0 == PyTuple_GET_SIZE(pto->args)) {
		argappl = args;
		Py_INCREF(args);
	} else if (0 == PyTuple_GET_SIZE(args)) {
		argappl = pto->args;
		Py_INCREF(pto->args);
	} else {
		argappl = PySequence_Concat(pto->args, args);
		if (argappl == NULL)
			return NULL;
	}

	if (pto->kw == Py_None) {
		kwappl = kw;
		Py_XINCREF(kw);
	} else {
		kwappl = PyDict_Copy(pto->kw);
		if (kwappl == NULL) {
			Py_DECREF(argappl);
			return NULL;
		}
		if (kw != NULL) {
			if (PyDict_Merge(kwappl, kw, 1)) {
				Py_DECREF(argappl);
				Py_DECREF(kwappl);
				return NULL;
			}
		}
	}

	ret = PyObject_Call(pto->fn, argappl, kwappl);
	Py_DECREF(argappl);
	Py_XDECREF(kwappl);
	return ret;
}

static int
partial_traverse(partialobject *pto, visitproc visit, void *arg)
{
	Py_VISIT(pto->fn);
	Py_VISIT(pto->args);
	Py_VISIT(pto->kw);
	Py_VISIT(pto->dict);
	return 0;
}

PyDoc_STRVAR(partial_doc,
"partial(func, *args, **keywords) - new function with partial application\n\
	of the given arguments and keywords.\n");

#define OFF(x) offsetof(partialobject, x)
static PyMemberDef partial_memberlist[] = {
	{"func",	T_OBJECT,	OFF(fn),	READONLY,
	 "function object to use in future partial calls"},
	{"args",	T_OBJECT,	OFF(args),	READONLY,
	 "tuple of arguments to future partial calls"},
	{"keywords",	T_OBJECT,	OFF(kw),	READONLY,
	 "dictionary of keyword arguments to future partial calls"},
	{NULL}  /* Sentinel */
};

static PyObject *
partial_get_dict(partialobject *pto)
{
	if (pto->dict == NULL) {
		pto->dict = PyDict_New();
		if (pto->dict == NULL)
			return NULL;
	}
	Py_INCREF(pto->dict);
	return pto->dict;
}

static int
partial_set_dict(partialobject *pto, PyObject *value)
{
	PyObject *tmp;

	/* It is illegal to del p.__dict__ */
	if (value == NULL) {
		PyErr_SetString(PyExc_TypeError,
				"a partial object's dictionary may not be deleted");
		return -1;
	}
	/* Can only set __dict__ to a dictionary */
	if (!PyDict_Check(value)) {
		PyErr_SetString(PyExc_TypeError,
				"setting partial object's dictionary to a non-dict");
		return -1;
	}
	tmp = pto->dict;
	Py_INCREF(value);
	pto->dict = value;
	Py_XDECREF(tmp);
	return 0;
}

static PyGetSetDef partial_getsetlist[] = {
	{"__dict__", (getter)partial_get_dict, (setter)partial_set_dict},
	{NULL} /* Sentinel */
};

static PyTypeObject partial_type = {
	PyObject_HEAD_INIT(NULL)
	0,				/* ob_size */
	"functional.partial",		/* tp_name */
	sizeof(partialobject),		/* tp_basicsize */
	0,				/* tp_itemsize */
	/* methods */
	(destructor)partial_dealloc,	/* tp_dealloc */
	0,				/* tp_print */
	0,				/* tp_getattr */
	0,				/* tp_setattr */
	0,				/* tp_compare */
	0,				/* tp_repr */
	0,				/* tp_as_number */
	0,				/* tp_as_sequence */
	0,				/* tp_as_mapping */
	0,				/* tp_hash */
	(ternaryfunc)partial_call,	/* tp_call */
	0,				/* tp_str */
	PyObject_GenericGetAttr,	/* tp_getattro */
	PyObject_GenericSetAttr,	/* tp_setattro */
	0,				/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
		Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_WEAKREFS,	/* tp_flags */
	partial_doc,			/* tp_doc */
	(traverseproc)partial_traverse,	/* tp_traverse */
	0,				/* tp_clear */
	0,				/* tp_richcompare */
	offsetof(partialobject, weakreflist),	/* tp_weaklistoffset */
	0,				/* tp_iter */
	0,				/* tp_iternext */
	0,				/* tp_methods */
	partial_memberlist,		/* tp_members */
	partial_getsetlist,		/* tp_getset */
	0,				/* tp_base */
	0,				/* tp_dict */
	0,				/* tp_descr_get */
	0,				/* tp_descr_set */
	offsetof(partialobject, dict),	/* tp_dictoffset */
	0,				/* tp_init */
	0,				/* tp_alloc */
	partial_new,			/* tp_new */
	PyObject_GC_Del,		/* tp_free */
};

/* foldl ********************************************************************/

static PyObject *
functional_foldl(PyObject *self, PyObject *args)
{
	PyObject *func, *start, *seq, *iter, *result = NULL, *func_args, *item;
    int decref_start = 1;
	
	if (!PyArg_UnpackTuple(args, "foldl", 3, 3, &func, &start, &seq)) {
		return NULL;
	}
    
    if (!PyCallable_Check(func)) {
		PyErr_SetString(PyExc_TypeError,
			"argument 1 to foldl() must be callable");
		return NULL;
	}
	
	iter = PyObject_GetIter(seq);
	if (iter == NULL) {
		PyErr_SetString(PyExc_TypeError,
			"argument 3 to foldl() must support iteration");
		return NULL;
	}
	
    func_args = PyTuple_New(2);
    if (NULL == func_args) {
        Py_DECREF(iter);
        return NULL;
    }
    
    Py_INCREF(start);
    while ((item = PyIter_Next(iter))) {
        PyTuple_SET_ITEM(func_args, 0, start);
		PyTuple_SET_ITEM(func_args, 1, item);
		result = PyObject_CallObject(func, func_args);
		PyTuple_SET_ITEM(func_args, 0, NULL);
        PyTuple_SET_ITEM(func_args, 1, NULL);
        Py_DECREF(start);
        decref_start = 0;
        Py_DECREF(item);

		if (NULL == result) {
            Py_DECREF(iter);
            Py_DECREF(func_args);
            return NULL;
		}
        start = result;
	}
    if (decref_start) {
        Py_DECREF(start);
    }
    Py_DECREF(func_args);
    Py_DECREF(iter);
    
	if (PyErr_Occurred()) {
		Py_XDECREF(result);
        return NULL;
	}
    
    /* This is here so if we skipped the iter loop, we return start */
    if (NULL == result) {
        Py_INCREF(start);
        return start;
    }
	return result;
}

PyDoc_STRVAR(foldl_doc,
"foldl(function, start, iterable) -> object\n\
\n\
Takes a binary function, a starting value (usually some kind of 'zero'), and\n\
an iterable. The function is applied to the starting value and the first\n\
element of the list, then the result of that and the second element of the\n\
list, then the result of that and the third element of the list, and so on.\n\
\n\
foldl(add, 0, [1, 2, 3]) is equivalent to add(add(add(0, 1), 2), 3)");

/* foldr ********************************************************************/

static PyObject *
foldr(PyObject *func, PyObject *base, PyObject *iter)
{
	PyObject *item, *func_args, *func_return, *recursive;
	
	item = PyIter_Next(iter);
	if (NULL == item) {
		if (PyErr_Occurred()) {
			return NULL;
		}
		return base;
	}
	
	recursive = foldr(func, base, iter);
	if (NULL == recursive) {
		Py_DECREF(item);
		return NULL;
	}
	
	func_args = PyTuple_New(2);
	PyTuple_SET_ITEM(func_args, 0, item);
	PyTuple_SET_ITEM(func_args, 1, recursive);
	func_return = PyObject_CallObject(func, func_args);

    if (NULL == func_return && recursive == base) {
        /* This is so base doesn't get decrefed twice: once by
           Py_DECREF(func_args) and once in functional_foldr
           after we return NULL below */
        PyTuple_SET_ITEM(func_args, 1, NULL);
    }
	Py_DECREF(func_args);
	return func_return;
}

static PyObject *
functional_foldr(PyObject *self, PyObject *args)
{
	PyObject *func, *base, *seq, *iter, *result;

	if (!PyArg_UnpackTuple(args, "foldr", 3, 3, &func, &base, &seq))
		return NULL;
        
    if (!PyCallable_Check(func)) {
        PyErr_SetString(PyExc_TypeError,
			"argument 1 to foldr() must be callable");
		return NULL;
    }
	
	iter = PyObject_GetIter(seq);
	if (NULL == iter) {
		PyErr_SetString(PyExc_TypeError,
			"argument 3 to foldr() must support iteration");
		return NULL;
	}
	
    Py_INCREF(base);
	result = foldr(func, base, iter);
	Py_DECREF(iter);
    if (NULL == result) {
        Py_DECREF(base);
    }
    
	return result;
}

PyDoc_STRVAR(foldr_doc,
"foldr(function, start, iterable) -> object\n\
\n\
Like foldl, but starts from the end of the iterable and works back toward the\n\
beginning. For example, foldr(subtract, 0, [1, 2, 3]) == 2, but\n\
foldl(subtract, 0, [1, 2, 3] == -6\n\
\n\
foldr(add, 0, [1, 2, 3]) is equivalent to add(1, add(2, add(3, 0)))");

/* id ***********************************************************************/

static PyObject *
functional_id(PyObject *self, PyObject *arg)
{
	Py_INCREF(arg);
	return arg;
}

PyDoc_STRVAR(id_doc,
"id(obj) -> object\n\
\n\
The identity function. id(obj) returns obj unchanged.\n\
\n\
>>> obj = object()\n\
>>> id(obj) is obj\n\
True");

/* scanl ********************************************************************/

static PyObject *
functional_scanl(PyObject *self, PyObject *args)
{
	PyObject *func, *start, *result = NULL, *seq, *iter, *result_list;
	
	if (!PyArg_UnpackTuple(args, "scanl", 3, 3, &func, &start, &seq)) {
		return NULL;
	}
	Py_INCREF(start);
    
	iter = PyObject_GetIter(seq);
	if (!iter) {
		PyErr_SetString(PyExc_TypeError,
			"argument 3 to scanl() must support iteration");
		Py_DECREF(start);
		return NULL;
	}
	
	if ((args = PyTuple_New(2)) == NULL) {
		goto Fail;
	}
	
	result_list = PyList_New(0);
	PyList_Append(result_list, start);
	result = start;

	for (;;) {
		PyObject *item;

		item = PyIter_Next(iter);
		if (!item) {
			if (PyErr_Occurred()) {
				goto Fail;
			}
			break;
		}

		PyTuple_SetItem(args, 0, result);
		PyTuple_SetItem(args, 1, item);
		if ((result = PyObject_CallObject(func, args)) == NULL) {
			Py_INCREF(start);
			goto Fail;
		}
		
		PyList_Append(result_list, result);
		
		if (args->ob_refcnt > 1) {
			Py_DECREF(args);
			if ((args = PyTuple_New(2)) == NULL)
				goto Fail;
		}
	}
	goto Succeed;

Fail:
	Py_CLEAR(result_list);
Succeed:
	Py_DECREF(start);
	Py_XDECREF(args);
	Py_DECREF(iter);
	return result_list;
}

PyDoc_STRVAR(scanl_doc,
"scanl(func, start, iterable) -> list\n\
\n\
Like foldl, but produces a list of successively reduced values, starting\n\
from the left.\n\
scanr(f, 0, [1, 2, 3]) is equivalent to\n\
[0, f(0, 1), f(f(0, 1), 2), f(f(f(0, 1), 2), 3)]");

/* scanr ********************************************************************/

/*
In Haskell:
    
scanr             :: (a -> b -> b) -> b -> [a] -> [b]
scanr f q0 []     =  [q0]
scanr f q0 (x:xs) =  f x q : qs
                     where qs@(q:_) = scanr f q0 xs
*/

static PyObject *
functional_scanr(PyObject *self, PyObject *args)
{
	PyObject *func, *start, *seq, *iter, *result_list, *item, *func_args;
	PyObject *result, *arg_1, *arg_2;
	int i;
	
	if (!PyArg_UnpackTuple(args, "scanr", 3, 3, &func, &start, &seq)) {
		return NULL;
	}
	Py_INCREF(start);
	
	func = PyTuple_GET_ITEM(args, 0);
	if (!PyCallable_Check(func)) {
		PyErr_SetString(PyExc_TypeError,
			"argument 1 to scanr() must be callable");
		Py_DECREF(start);
		return NULL;
	}
	
	iter = PyObject_GetIter(seq);
	if (iter == NULL) {
		PyErr_SetString(PyExc_TypeError,
			"argument 3 to scanr() must support iteration");
		Py_DECREF(start);
		return NULL;
	}
	
	result_list = PyList_New(0);
	if (NULL == result_list) {
		Py_DECREF(iter);
		Py_DECREF(start);
		return NULL;
	}
	
	while ((item = PyIter_Next(iter))) {
		PyList_Append(result_list, item);
		Py_DECREF(item);
	}
	Py_DECREF(iter);
	if (PyErr_Occurred()) {
		Py_DECREF(start);
		goto Fail;
	}
	
	PyList_Append(result_list, start);
	Py_DECREF(start);
	
	for (i = PyList_GET_SIZE(result_list) - 1; i > 0; i--) {
		func_args = PyTuple_New(2);
		arg_1 = PyList_GET_ITEM(result_list, i - 1);
		Py_INCREF(arg_1);
		arg_2 = PyList_GET_ITEM(result_list, i);
		Py_INCREF(arg_2);
	
		PyTuple_SetItem(func_args, 0, arg_1);
		PyTuple_SetItem(func_args, 1, arg_2);
		
		result = PyObject_CallObject(func, func_args);
		Py_DECREF(func_args);
		if (NULL == result) {
			goto Fail;
		}
		PyList_SetItem(result_list, i - 1, result);
	}
	goto Succeed;
	
Fail:
	Py_CLEAR(result_list);
Succeed:
	return result_list;
}

PyDoc_STRVAR(scanr_doc,
"scanr(func, start, iterable) -> list\n\
\n\
Like foldr, but produces a list of successively reduced values, starting\n\
from the right.\n\
scanr(f, 0, [1, 2, 3]) is equivalent to\n\
[f(1, f(2, f(3, 0))), f(2, f(3, 0)), f(3, 0), 0]");

/* compose ******************************************************************/

typedef struct {
	PyObject_HEAD
	PyObject *inner_func;
	PyObject *outer_func;
    PyObject *weakreflist; /* List of weak references */
    int unpack;
} composeobject;

static PyTypeObject compose_type;

static PyObject *
compose_new(PyTypeObject *type, PyObject *args, PyObject *kw)
{
	PyObject *inner_func, *outer_func, *unpack = Py_False;
	composeobject *compo;
    
    static char *kwlist[] = {"outer", "inner", "unpack", NULL};
    
    if(!PyArg_ParseTupleAndKeywords(args, kw, "OO|O", kwlist,
                &outer_func, &inner_func, &unpack))
        return NULL;

	if (!PyCallable_Check(outer_func)) {
		PyErr_SetString(PyExc_TypeError,
				"all arguments to compose must be callable");
		return NULL;
	}
	
	if (!PyCallable_Check(inner_func)) {
		PyErr_SetString(PyExc_TypeError,
				"all arguments to compose must be callable");
		return NULL;
	}
    
	/* create flipobject structure */
	compo = (composeobject *)type->tp_alloc(type, 0);
	if (compo == NULL)
		return NULL;
        
    /* Note to self: don't decref unpack */
    compo->unpack = PyObject_IsTrue(unpack);

    Py_INCREF(inner_func);
	compo->inner_func = inner_func;
	
	Py_INCREF(outer_func);
	compo->outer_func = outer_func;
	
	return (PyObject *)compo;
}

static PyObject *
compose_call(composeobject *compo, PyObject *args, PyObject *kw)
{
	PyObject *ret_val, *inner_ret_val, *inner_tuple;

    inner_ret_val = PyObject_Call(compo->inner_func, args, kw);
	if (NULL == inner_ret_val) {
		return NULL;
	}
	
    if (compo->unpack) {
        PyObject *arg_tuple = PySequence_Tuple(inner_ret_val);
        Py_DECREF(inner_ret_val);
        if (NULL == arg_tuple)
            return NULL;
    
        ret_val = PyObject_CallObject(compo->outer_func, arg_tuple);
        Py_DECREF(arg_tuple);
    }
    else {
	    inner_tuple = PyTuple_New(1);
	    PyTuple_SET_ITEM(inner_tuple, 0, inner_ret_val);
	    ret_val = PyObject_CallObject(compo->outer_func, inner_tuple);

        /* will decref inner_ret_val, too */
        Py_DECREF(inner_tuple);
    }    
        
	return ret_val;
}

static int
compose_traverse(composeobject *compo, visitproc visit, void *arg)
{
	Py_VISIT(compo->inner_func);
	Py_VISIT(compo->outer_func);

	return 0;
}

PyDoc_STRVAR(compose_doc,
"compose(func_1, func_2) -> compose object\n\
\n\
The compose object returned by compose is a composition of func_1 and func_2.\n\
That is, compose(func_1, func_2)(5) == func_1(func_2(5))");

static void
compose_dealloc(composeobject *compo)
{
	PyObject_GC_UnTrack(compo);
    if (compo->weakreflist != NULL)
		PyObject_ClearWeakRefs((PyObject *) compo);
	
	Py_XDECREF(compo->inner_func);
	Py_XDECREF(compo->outer_func);
	
	compo->ob_type->tp_free(compo);
}

static PyTypeObject compose_type = {
	PyObject_HEAD_INIT(NULL)
	0,				/* ob_size */
	"functional.compose",		/* tp_name */
	sizeof(composeobject),		/* tp_basicsize */
	0,				/* tp_itemsize */
	/* methods */
	(destructor)compose_dealloc,	/* tp_dealloc */
	0,				/* tp_print */
	0,				/* tp_getattr */
	0,				/* tp_setattr */
	0,				/* tp_compare */
	0,				/* tp_repr */
	0,				/* tp_as_number */
	0,				/* tp_as_sequence */
	0,				/* tp_as_mapping */
	0,				/* tp_hash */
	(ternaryfunc)compose_call,	/* tp_call */
	0,				/* tp_str */
	PyObject_GenericGetAttr,	/* tp_getattro */
	PyObject_GenericSetAttr,	/* tp_setattro */
	0,				/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
		Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_WEAKREFS,	/* tp_flags */
	compose_doc,			/* tp_doc */
	(traverseproc)compose_traverse,	/* tp_traverse */
	0,				/* tp_clear */
	0,				/* tp_richcompare */
	offsetof(composeobject, weakreflist),		/* tp_weaklistoffset */
	0,				/* tp_iter */
	0,				/* tp_iternext */
	0,				/* tp_methods */
	0,				/* tp_members */
	0,				/* tp_getset */
	0,				/* tp_base */
	0,				/* tp_dict */
	0,				/* tp_descr_get */
	0,				/* tp_descr_set */
	0,				/* tp_dictoffset */
	0,				/* tp_init */
	0,				/* tp_alloc */
	compose_new,			/* tp_new */
	PyObject_GC_Del,		/* tp_free */
};

/* flip *********************************************************************/

typedef struct {
	PyObject_HEAD
	PyObject *func;
    PyObject *weakreflist; /* List of weak references */
} flipobject;

static PyTypeObject flip_type;

static PyObject *
flip_new(PyTypeObject *type, PyObject *args, PyObject *kw)
{
	PyObject *func;
	flipobject *flipo;

	if (PyTuple_GET_SIZE(args) != 1) {
		PyErr_SetString(PyExc_TypeError,
				"type 'flip' takes exactly 1 argument");
		return NULL;
	}

	func = PyTuple_GET_ITEM(args, 0);
	if (!PyCallable_Check(func)) {
		PyErr_SetString(PyExc_TypeError,
				"the first argument must be callable");
		return NULL;
	}

	/* create flipobject structure */
	flipo = (flipobject *)type->tp_alloc(type, 0);
	if (flipo == NULL)
		return NULL;

	flipo->func = func;
	Py_INCREF(func);
	
	return (PyObject *)flipo;
}

static PyObject *
flip_call(flipobject *flipo, PyObject *args, PyObject *kw)
{
	PyObject *return_val, *flipped_args, *item;
	int args_size, i;

	assert (PyCallable_Check(flipo->func));

	args_size = PyTuple_GET_SIZE(args);
	flipped_args = PyTuple_New(args_size);
	
	for(i = 0; i < args_size; i++) {
		item = PyTuple_GetItem(args, i);
		Py_INCREF(item);
		PyTuple_SET_ITEM(flipped_args, args_size - i - 1, item);
	}

	return_val = PyObject_Call(flipo->func, flipped_args, kw);
	Py_DECREF(flipped_args);
	return return_val;
}

static int
flip_traverse(flipobject *flipo, visitproc visit, void *arg)
{
	Py_VISIT(flipo->func);
	return 0;
}

PyDoc_STRVAR(flip_doc,
"flip(func) -> flip object\n\
\n\
flip causes `func` to take its first two non-keyword arguments in reverse\n\
order. The returned flip object is a wrapper around `func` that makes this\n\
happen.");

static void
flip_dealloc(flipobject *flipo)
{
	PyObject_GC_UnTrack(flipo);
    if (flipo->weakreflist != NULL)
		PyObject_ClearWeakRefs((PyObject *) flipo);
    
	Py_XDECREF(flipo->func);
	flipo->ob_type->tp_free(flipo);
}

static PyTypeObject flip_type = {
	PyObject_HEAD_INIT(NULL)
	0,				/* ob_size */
	"functional.flip",		/* tp_name */
	sizeof(flipobject),		/* tp_basicsize */
	0,				/* tp_itemsize */
	/* methods */
	(destructor)flip_dealloc,	/* tp_dealloc */
	0,				/* tp_print */
	0,				/* tp_getattr */
	0,				/* tp_setattr */
	0,				/* tp_compare */
	0,				/* tp_repr */
	0,				/* tp_as_number */
	0,				/* tp_as_sequence */
	0,				/* tp_as_mapping */
	0,				/* tp_hash */
	(ternaryfunc)flip_call,	/* tp_call */
	0,				/* tp_str */
	PyObject_GenericGetAttr,	/* tp_getattro */
	PyObject_GenericSetAttr,	/* tp_setattro */
	0,				/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
		Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_WEAKREFS,	/* tp_flags */
	flip_doc,			/* tp_doc */
	(traverseproc)flip_traverse,	/* tp_traverse */
	0,				/* tp_clear */
	0,				/* tp_richcompare */
	offsetof(flipobject, weakreflist),	/* tp_weaklistoffset */
	0,				/* tp_iter */
	0,				/* tp_iternext */
	0,				/* tp_methods */
	0,		/* tp_members */
	0,		/* tp_getset */
	0,				/* tp_base */
	0,				/* tp_dict */
	0,				/* tp_descr_get */
	0,				/* tp_descr_set */
	0,	/* tp_dictoffset */
	0,				/* tp_init */
	0,				/* tp_alloc */
	flip_new,			/* tp_new */
	PyObject_GC_Del,		/* tp_free */
};

/* functional.map ***********************************************************/

static PyObject *
functional_map(PyObject *self, PyObject *args)
{
    PyObject *seq, *func, *accu, *it, *item, *arg, *result;
    int status;
    
    if (!PyArg_UnpackTuple(args, "map", 2, 2, &func, &seq))
		return NULL;
        
    if (!PyCallable_Check(func)) {
		PyErr_SetString(PyExc_TypeError,
				"map() argument 1 must be callable");
        return NULL;
	}
    
    it = PyObject_GetIter(seq);
    if (NULL == it) {
        PyErr_SetString(PyExc_TypeError,
				"map() argument 2 must be iterable");
        return NULL;
    }
    
    accu = PyList_New(0);
    if (NULL == accu) {
        Py_DECREF(it);
        return NULL;
    }
    
    arg = PyTuple_New(1);
	if (NULL == arg) {
		Py_DECREF(it);
        Py_DECREF(accu);
        return NULL;
    }
    
    while ((item = PyIter_Next(it))) {
        PyTuple_SET_ITEM(arg, 0, item);
        result = PyObject_CallObject(func, arg);
        PyTuple_SET_ITEM(arg, 0, NULL);
        Py_DECREF(item);
        if (NULL == result)
            goto fail;

        status = PyList_Append(accu, result);
        Py_DECREF(result);
        if (status < 0)
            goto fail;
    }
    
    if (PyErr_Occurred()) {
        Py_CLEAR(accu);
    }
    
    Py_DECREF(arg);
    Py_DECREF(it);
    return accu;
    
fail:
    Py_DECREF(it);
    Py_DECREF(arg);
    Py_DECREF(accu);
    return NULL;
}

PyDoc_STRVAR(map_doc,
"map(function, sequence) -> list\n\
\n\
Return a list of the results of applying the function to the items of\n\
the argument sequence.");

/* functional.filter ********************************************************/

static PyObject *
functional_filter(PyObject *self, PyObject *args)
{
    PyObject *seq, *func, *accu, *it, *item;
    int status;

    if (!PyArg_UnpackTuple(args, "filter", 2, 2, &func, &seq))
		return NULL;
    
    if (!PyCallable_Check(func)) {
		PyErr_SetString(PyExc_TypeError,
				"filter() argument 1 must be callable");
        return NULL;
	}
    
    it = PyObject_GetIter(seq);
    if (NULL == it) {
        PyErr_SetString(PyExc_TypeError,
				"filter() argument 2 must be iterable");
        return NULL;
    }
    
    accu = PyList_New(0);
    if (NULL == accu) {
        Py_DECREF(it);
        return NULL;
    }
    
    if ((PyObject *)&PyBool_Type == func) {
        while ((item = PyIter_Next(it))) {
            if (PyObject_IsTrue(item)) {
                status = PyList_Append(accu, item);
                Py_DECREF(item);
                if (status < 0)
                    goto fail;
            }
            else {
                Py_DECREF(item);
            }
        }
        if (PyErr_Occurred())
            goto fail;
    }
    else {
        PyObject *arg, *result;

        arg = PyTuple_New(1);
        if (NULL == arg)
            goto fail;
        
        while ((item = PyIter_Next(it))) {
            PyTuple_SET_ITEM(arg, 0, item);
            result = PyObject_CallObject(func, arg);
            PyTuple_SET_ITEM(arg, 0, NULL);
            
            if (NULL == result) {
                Py_DECREF(item);
                Py_DECREF(arg);
                goto fail;
            }
            
            if (PyObject_IsTrue(result)) {
                Py_DECREF(result);
                
                status = PyList_Append(accu, item);
                Py_DECREF(item);
                if (status < 0) {
                    Py_DECREF(arg);
                    goto fail;
                }
            }
            else {
                Py_DECREF(item);
                Py_DECREF(result);
            }
        }
        Py_DECREF(arg);
        
        if (PyErr_Occurred())
            goto fail;
    }
    
    Py_DECREF(it);
    return accu;

fail:
    Py_DECREF(it);
    Py_DECREF(accu);
    return NULL;
}

PyDoc_STRVAR(filter_doc,
"filter(function, sequence) -> list\n\
\n\
Return a list ofthose items in sequence for which function(item) is true");

/* module level code ********************************************************/

PyDoc_STRVAR(module_doc,
"Tools for functional programming.");

static PyMethodDef functional_methods[] = {
	{"foldl",	functional_foldl,   METH_VARARGS, foldl_doc},
	{"foldr",	functional_foldr,   METH_VARARGS, foldr_doc},
	{"id",      functional_id,      METH_O,       id_doc},
	{"scanl",   functional_scanl,   METH_VARARGS, scanl_doc},
	{"scanr",   functional_scanr,   METH_VARARGS, scanr_doc},
    {"map",     functional_map,     METH_VARARGS, map_doc},
    {"filter",  functional_filter,  METH_VARARGS, filter_doc},
 	{NULL,		NULL}		/* sentinel */
};

PyMODINIT_FUNC
initfunctional(void)
{
	int i;
	PyObject *m;
	char *name;
	PyTypeObject *typelist[] = {
		&partial_type,
		&flip_type,
		&compose_type,
		NULL
	};

	m = Py_InitModule3("functional", functional_methods, module_doc);
	if (m == NULL)
		return;

	for (i=0 ; typelist[i] != NULL ; i++) {
		if (PyType_Ready(typelist[i]) < 0)
			return;
		name = strchr(typelist[i]->tp_name, '.');
		assert (name != NULL);
		Py_INCREF(typelist[i]);
		PyModule_AddObject(m, name+1, (PyObject *)typelist[i]);
	}
}
