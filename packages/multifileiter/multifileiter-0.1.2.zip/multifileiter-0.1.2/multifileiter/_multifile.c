#include "Python.h"
#include "structmember.h"

#if PY_MAJOR_VERSION >= 3
#define PyInt_FromLong PyLong_FromLong
#define PyInt_FromSsize_t PyLong_FromSsize_t

#define PyString_FromString PyUnicode_FromString
#endif

/* 
   $Id: _multifile.c 13 2010-01-20 17:21:59Z ggenellina $
   Copyright (c) 2010 Gabriel A. Genellina
   Licensed under the MIT License. See license.txt for details.
*/

struct module_state {
  PyObject* unused; 
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif

/* _multifile.MultiFileIter objects
   An iterator over all lines of the given files.
*/
   
typedef struct {
    PyObject_HEAD
    PyObject* files_it;
    PyObject* mode;
    PyObject* current;
    PyObject* curfilename;
    int lineno;
} MultiFileObject;


/* forward references */
int multifile_clear(MultiFileObject *self);
PyObject *multifile_close(MultiFileObject *self);


static PyObject *
multifile_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    MultiFileObject *self;

    self = (MultiFileObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->files_it = NULL;
        self->mode = NULL;
        self->current = NULL;
        self->curfilename = NULL;
        self->lineno = 0;
    }
    return (PyObject *)self;
}


static void
multifile_dealloc(MultiFileObject* self)
{
    PyObject* ret;
    
	ret = multifile_close(self);
	if (!ret) {
		PySys_WriteStderr("close failed in MultiFileObject destructor:\n");
		PyErr_Print();
	}
	else {
		Py_DECREF(ret);
	}
    multifile_clear(self);
    Py_TYPE(self)->tp_free((PyObject*)self);
}


static int
multifile_init(MultiFileObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *files=NULL, *mode=NULL;
    PyObject *it=NULL;
    static char *kwlist[] = {"files", "mode", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|OO:MultiFileIter", kwlist, 
           &files, &mode))
        return -1; 

    /* files */
    if (files) {
        it = PyObject_GetIter(files);
        if (it == NULL)
            return -1;
    } else {
        PyObject *empty = PyTuple_New(0);
        it = PyObject_GetIter(empty);
        Py_DECREF(empty);
        if (it == NULL)
            return -1;
    }
    Py_CLEAR(self->files_it);
    self->files_it = it;

    /* mode */
    if (mode) {
#if PY_MAJOR_VERSION >= 3
        if (!PyUnicode_Check(mode)) {
#else
        if (!PyString_Check(mode)) {
#endif
            PyErr_SetString(PyExc_TypeError, "mode must be string");
            return -1;
        }
        Py_CLEAR(self->mode);
        Py_INCREF(mode);
        self->mode = mode;
    } else {
        Py_CLEAR(self->mode);
        self->mode = PyString_FromString("r");
    }
    
    self->lineno = 0;
    return 0;
}


static int
multifile_traverse(MultiFileObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->files_it);
    Py_VISIT(self->current);
    Py_VISIT(self->curfilename);
    return 0;
}


static int
multifile_clear(MultiFileObject *self)
{
    Py_CLEAR(self->files_it);
    Py_CLEAR(self->mode);
    Py_CLEAR(self->current);
    Py_CLEAR(self->curfilename);
    return 0;
}


static void
_multifile_nextfile(MultiFileObject* self)
{
    PyObject *obj;
    
    if (self->current != NULL) {
        if ((PySys_GetObject("stdin") != self->current) &&
            PyObject_HasAttrString(self->current, "close")) 
        {
            obj = PyObject_CallMethod(self->current, "close", NULL);
            Py_XDECREF(obj);
        }    
        Py_CLEAR(self->current);
    }
}


static PyObject *
multifile_iternext(MultiFileObject *self)
{
    PyObject *o, *line, *name;

next:    
    if (self->current == NULL) {
        o = PyIter_Next(self->files_it);
        if (o == NULL) 
            return NULL;
        Py_CLEAR(self->curfilename);
#if PY_MAJOR_VERSION >= 3
        if (PyUnicode_Check(o)) {
            if (PyUnicode_CompareWithASCIIString(o, "-")==0) {
#else
        if (PyString_Check(o)) {
            if ((PyString_GET_SIZE(o) == 1) && ((*PyString_AS_STRING(o)) == '-')) {
#endif
                PyObject* sysstdin;
                sysstdin = PySys_GetObject("stdin");
                if (sysstdin == NULL) {
                    PyErr_SetString(PyExc_RuntimeError, "No sys.stdin to use");
                    Py_DECREF(o);
                    return NULL;
                }
                Py_INCREF(sysstdin);
                self->current = sysstdin;
                self->curfilename = PyString_FromString("<stdin>");
            } else {
#if PY_MAJOR_VERSION >= 3
                PyObject_CallFunctionObjArgs(
                    PyDict_GetItemString(PyEval_GetBuiltins(), "open"),
                    o,
                    self->mode,
                    NULL);
#else
                self->current = PyFile_FromString(PyString_AS_STRING(o), PyString_AS_STRING(self->mode));
#endif
                if (self->current == NULL)  {
                    Py_DECREF(o);
                    return NULL;
                }    
                self->curfilename = o;
                Py_INCREF(self->curfilename);
            }    
            Py_DECREF(o);
        } else {
            if (!PyIter_Check(o)) {
                PyErr_Format(PyExc_TypeError,
                    "MultiFileIter: expecting a string or iterable, got %.100s", Py_TYPE(o)->tp_name);
                Py_DECREF(o);
                return NULL;
            }
            self->current = o;
            name = PyObject_GetAttrString(self->current, "name");
            if (name != NULL) {
                self->curfilename = name;
            } else {
                PyErr_Clear();
            }
        }
    }           
    line = PyIter_Next(self->current);
    if (line == NULL) {
        if (!PyErr_Occurred()) {
            _multifile_nextfile(self);
            if (!PyErr_Occurred())
                goto next;
        }        
        return NULL;    
    }
    /*
    line = PyObject_CallMethod(self->current, "next", NULL);
    if (line == NULL) {
        if (PyErr_ExceptionMatches(PyExc_StopIteration)) {
            PyErr_Clear();
            _multifile_nextfile(self);
            if (!PyErr_Occurred())
                goto next;
        }
        return NULL;    
    }
    */
    self->lineno++;    
    return line;
}    


static PyObject *
multifile_lineno(MultiFileObject *self)
{
    return PyInt_FromSsize_t(self->lineno);
}    


static PyObject *
multifile_isstdin(MultiFileObject *self)
{
    if (self->current == NULL) 
        Py_RETURN_FALSE;
    return PyBool_FromLong(PySys_GetObject("stdin") == self->current);
}


static PyObject *
multifile_fileno(MultiFileObject *self)
{
    PyObject* ret;
    
    if (self->current == NULL) 
        goto error;
    ret = PyObject_CallMethod(self->current, "fileno", NULL);
    if (ret == NULL) {
        PyErr_Clear();
        goto error;
    }
    return ret;
error:
    return PyInt_FromLong(-1);
}


static PyObject *
multifile_filename(MultiFileObject *self)
{
    if (self->curfilename == NULL) 
        Py_RETURN_NONE;
    Py_INCREF(self->curfilename);
    return self->curfilename;
}


static PyObject *
multifile_nextfile(MultiFileObject *self)
{
    _multifile_nextfile(self);
    if (PyErr_Occurred())
        return NULL;
    Py_RETURN_NONE;
}


static PyObject *
multifile_close(MultiFileObject *self)
{
    PyObject *empty;
    
    _multifile_nextfile(self);
    if (PyErr_Occurred())
        return NULL;
    Py_CLEAR(self->files_it);
    empty = PyTuple_New(0);
    self->files_it = PyObject_GetIter(empty);
    Py_DECREF(empty);
    Py_RETURN_NONE;
}


static PyMethodDef multifile_methods[] = {
    {"filename", (PyCFunction)multifile_filename, METH_NOARGS, 
        "Name of the file currently being read, or None."},
    {"lineno", (PyCFunction)multifile_lineno, METH_NOARGS, 
        "Cumulative line number of the line that has just been read; 0 before reading the first line"},
    {"isstdin", (PyCFunction)multifile_isstdin, METH_NOARGS, 
        "Returns true if the line just read came from stdin, false otherwise"},
    {"fileno", (PyCFunction)multifile_fileno, METH_NOARGS, 
        "Returns the file descriptor for the current file, or -1 when no file is opened."},
    {"nextfile", (PyCFunction)multifile_nextfile, METH_NOARGS, 
        "Close the current file; the next iteration will read the first line from the next file (if any)."},
    {"close", (PyCFunction)multifile_close, METH_NOARGS, 
        "Close the whole sequence."},
    {NULL,      NULL}       /* sentinel */
};


PyDoc_STRVAR(multifile_doc,
"MultiFileIter([files[, mode]]) -> MultiFileIter object\n\
\n\
An iterator over all lines of the given files.\n\
");


static PyTypeObject MultiFile_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "multifileiter._multifile.MultiFileIter",   /* tp_name */
    sizeof(MultiFileObject),  /* tp_basicsize */
    0,                       /* tp_itemsize */
    (destructor)multifile_dealloc, /*tp_dealloc*/
    0,                       /* tp_print */
    0,                       /* tp_getattr */
    0,                       /* tp_setattr */
    0,                       /* tp_compare */
    0,                       /* tp_repr */
    0,                       /* tp_as_number */
    0,                       /* tp_as_sequence */
    0,                       /* tp_as_mapping */
    0,                       /* tp_hash */
    0,                       /* tp_call */
    0,                       /* tp_str */
    0,                       /* tp_getattro */
    0,                       /* tp_setattro */
    0,                       /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT |
#if PY_MAJOR_VERSION < 3
      Py_TPFLAGS_HAVE_ITER | 
#endif
      Py_TPFLAGS_BASETYPE | 
      Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    multifile_doc,           /* tp_doc */
    (traverseproc)multifile_traverse,   /* tp_traverse */
    (inquiry)multifile_clear,           /* tp_clear */
    0,                       /* tp_richcompare */
    0,                       /* tp_weaklistoffset */
    PyObject_SelfIter,       /* tp_iter */
    (iternextfunc)multifile_iternext,       /* tp_iternext */
    multifile_methods,       /* tp_methods */
    0,                       /* tp_members */
    0,                       /* tp_getset */
    0,                       /* tp_base */
    0,                       /* tp_dict */
    0,                       /* tp_descr_get */
    0,                       /* tp_descr_set */
    0,                       /* tp_dictoffset */
    (initproc)multifile_init,   /* tp_init */
    0,                       /* tp_alloc */
    multifile_new,           /* tp_new */
};


PyDoc_STRVAR(module_doc,
"A fast variant of FileInput, written in C.\n\
\n\
MultiFileIter: An iterator over all lines of the given files.\n\
");


static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};


static int
init_this_module(PyObject* module)
{
    if (PyType_Ready(&MultiFile_Type) < 0)
        return 0;
    Py_INCREF(&MultiFile_Type);
    if (PyModule_AddObject(module, "MultiFileIter", (PyObject *) &MultiFile_Type) < 0) {
        Py_DECREF(&MultiFile_Type);
        return 0;
    }
    return 1;
}


#if PY_MAJOR_VERSION >= 3

static int multifilemod_traverse(PyObject *m, visitproc visit, void *arg) {
    //Py_VISIT(GETSTATE(m)->xxx);
    return 0;
}

static int multifilemod_clear(PyObject *m) {
    //Py_CLEAR(GETSTATE(m)->xxx);
    return 0;
}

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "_multifile",
        module_doc,
        sizeof(struct module_state),
        module_methods,
        NULL,
        multifilemod_traverse,
        multifilemod_clear,
        NULL
};

PyObject *
PyInit__multifile(void)
{
    PyObject *module = PyModule_Create(&moduledef);
    if (module == NULL)
        return NULL;
    if (!init_this_module(module)) {
        Py_DECREF(module);
        return NULL;
    }
    return module;
}

#else

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_multifile(void) 
{
    PyObject *module;
    module = Py_InitModule3("_multifile", module_methods, module_doc);
    init_this_module(module);
}

#endif
