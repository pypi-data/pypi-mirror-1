/*
 *   Copyright (c) 2007-2008 Open Source Applications Foundation
 *
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 */

#include <jni.h>
#include <Python.h>
#include "structmember.h"

#include "java/lang/Object.h"
#include "java/lang/Class.h"
#include "functions.h"

using namespace java::lang;


/* FinalizerProxy */

static PyObject *t_fc_call(PyObject *self, PyObject *args, PyObject *kwds);

static void t_fp_dealloc(t_fp *self);
static PyObject *t_fp_getattro(t_fp *self, PyObject *name);
static int t_fp_setattro(t_fp *self, PyObject *name, PyObject *value);
static int t_fp_traverse(t_fp *self, visitproc visit, void *arg);
static int t_fp_clear(t_fp *self);
static PyObject *t_fp_repr(t_fp *self);
static PyObject *t_fp_iter(t_fp *self);

PyTypeObject FinalizerClassType = {
    PyObject_HEAD_INIT(NULL)
    0,                                   /* ob_size */
    "jcc.FinalizerClass",                /* tp_name */
    PyType_Type.tp_basicsize,            /* tp_basicsize */
    0,                                   /* tp_itemsize */
    0,                                   /* tp_dealloc */
    0,                                   /* tp_print */
    0,                                   /* tp_getattr */
    0,                                   /* tp_setattr */
    0,                                   /* tp_compare */
    0,                                   /* tp_repr */
    0,                                   /* tp_as_number */
    0,                                   /* tp_as_sequence */
    0,                                   /* tp_as_mapping */
    0,                                   /* tp_hash  */
    (ternaryfunc) t_fc_call,             /* tp_call */
    0,                                   /* tp_str */
    0,                                   /* tp_getattro */
    0,                                   /* tp_setattro */
    0,                                   /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                  /* tp_flags */
    "FinalizerClass",                    /* tp_doc */
    0,                                   /* tp_traverse */
    0,                                   /* tp_clear */
    0,                                   /* tp_richcompare */
    0,                                   /* tp_weaklistoffset */
    0,                                   /* tp_iter */
    0,                                   /* tp_iternext */
    0,                                   /* tp_methods */
    0,                                   /* tp_members */
    0,                                   /* tp_getset */
    &PyType_Type,                        /* tp_base */
    0,                                   /* tp_dict */
    0,                                   /* tp_descr_get */
    0,                                   /* tp_descr_set */
    0,                                   /* tp_dictoffset */
    0,                                   /* tp_init */
    0,                                   /* tp_alloc */
    0,                                   /* tp_new */
};

PyTypeObject FinalizerProxyType = {
    PyObject_HEAD_INIT(NULL)
    0,                                   /* ob_size */
    "jcc.FinalizerProxy",                /* tp_name */
    sizeof(t_fp),                        /* tp_basicsize */
    0,                                   /* tp_itemsize */
    (destructor)t_fp_dealloc,            /* tp_dealloc */
    0,                                   /* tp_print */
    0,                                   /* tp_getattr */
    0,                                   /* tp_setattr */
    0,                                   /* tp_compare */
    (reprfunc)t_fp_repr,                 /* tp_repr */
    0,                                   /* tp_as_number */
    0,                                   /* tp_as_sequence */
    0,                                   /* tp_as_mapping */
    0,                                   /* tp_hash  */
    0,                                   /* tp_call */
    0,                                   /* tp_str */
    (getattrofunc)t_fp_getattro,         /* tp_getattro */
    (setattrofunc)t_fp_setattro,         /* tp_setattro */
    0,                                   /* tp_as_buffer */
    (Py_TPFLAGS_DEFAULT |
     Py_TPFLAGS_HAVE_GC),                /* tp_flags */
    "FinalizerProxy",                    /* tp_doc */
    (traverseproc)t_fp_traverse,         /* tp_traverse */
    (inquiry)t_fp_clear,                 /* tp_clear */
    0,                                   /* tp_richcompare */
    0,                                   /* tp_weaklistoffset */
    (getiterfunc)t_fp_iter,              /* tp_iter */
    0,                                   /* tp_iternext */
    0,                                   /* tp_methods */
    0,                                   /* tp_members */
    0,                                   /* tp_getset */
    0,                                   /* tp_base */
    0,                                   /* tp_dict */
    0,                                   /* tp_descr_get */
    0,                                   /* tp_descr_set */
    0,                                   /* tp_dictoffset */
    0,                                   /* tp_init */
    0,                                   /* tp_alloc */
    0,                                   /* tp_new */
};

static PyObject *t_fc_call(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *obj = PyType_Type.tp_call(self, args, kwds);

    if (obj)
    {
        t_fp *fp = (t_fp *) FinalizerProxyType.tp_alloc(&FinalizerProxyType, 0);

        fp->object = obj;
        obj = (PyObject *) fp;
    }

    return obj;
}

static void t_fp_dealloc(t_fp *self)
{
    if (self->object)
        ((t_JObject *) self->object)->object.weaken$();

    t_fp_clear(self);
    self->ob_type->tp_free((PyObject *) self);
}

static int t_fp_traverse(t_fp *self, visitproc visit, void *arg)
{
    Py_VISIT(self->object);
    return 0;
}

static int t_fp_clear(t_fp *self)
{
    Py_CLEAR(self->object);
    return 0;
}

static PyObject *t_fp_repr(t_fp *self)
{
    return PyObject_Repr(self->object);
}

static PyObject *t_fp_iter(t_fp *self)
{
    return PyObject_GetIter(self->object);
}

static PyObject *t_fp_getattro(t_fp *self, PyObject *name)
{
    return PyObject_GetAttr(self->object, name);
}

static int t_fp_setattro(t_fp *self, PyObject *name, PyObject *value)
{
    return PyObject_SetAttr(self->object, name, value);
}


/* const variable descriptor */

class t_descriptor {
public:
    PyObject_HEAD
    int flags;
    union {
        PyObject *value;
        jclass (*initializeClass)(void);
    } access;
};
    
#define DESCRIPTOR_VALUE 0x1
#define DESCRIPTOR_CLASS 0x2
#define DESCRIPTOR_GETFN 0x4

static void t_descriptor_dealloc(t_descriptor *self);
static PyObject *t_descriptor___get__(t_descriptor *self,
                                      PyObject *obj, PyObject *type);

static PyMethodDef t_descriptor_methods[] = {
    { NULL, NULL, 0, NULL }
};


PyTypeObject ConstVariableDescriptorType = {
    PyObject_HEAD_INIT(NULL)
    0,                                   /* ob_size */
    "jcc.ConstVariableDescriptor",       /* tp_name */
    sizeof(t_descriptor),                /* tp_basicsize */
    0,                                   /* tp_itemsize */
    (destructor)t_descriptor_dealloc,    /* tp_dealloc */
    0,                                   /* tp_print */
    0,                                   /* tp_getattr */
    0,                                   /* tp_setattr */
    0,                                   /* tp_compare */
    0,                                   /* tp_repr */
    0,                                   /* tp_as_number */
    0,                                   /* tp_as_sequence */
    0,                                   /* tp_as_mapping */
    0,                                   /* tp_hash  */
    0,                                   /* tp_call */
    0,                                   /* tp_str */
    0,                                   /* tp_getattro */
    0,                                   /* tp_setattro */
    0,                                   /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                  /* tp_flags */
    "const variable descriptor",         /* tp_doc */
    0,                                   /* tp_traverse */
    0,                                   /* tp_clear */
    0,                                   /* tp_richcompare */
    0,                                   /* tp_weaklistoffset */
    0,                                   /* tp_iter */
    0,                                   /* tp_iternext */
    t_descriptor_methods,                /* tp_methods */
    0,                                   /* tp_members */
    0,                                   /* tp_getset */
    0,                                   /* tp_base */
    0,                                   /* tp_dict */
    (descrgetfunc)t_descriptor___get__,  /* tp_descr_get */
    0,                                   /* tp_descr_set */
    0,                                   /* tp_dictoffset */
    0,                                   /* tp_init */
    0,                                   /* tp_alloc */
    0,                                   /* tp_new */
};

static void t_descriptor_dealloc(t_descriptor *self)
{
    if (self->flags & DESCRIPTOR_VALUE)
        Py_DECREF(self->access.value);
    self->ob_type->tp_free((PyObject *) self);
}

PyObject *make_descriptor(PyTypeObject *value)
{
    t_descriptor *self = (t_descriptor *)
        ConstVariableDescriptorType.tp_alloc(&ConstVariableDescriptorType, 0);

    if (self)
    {
        Py_INCREF(value);
        self->access.value = (PyObject *) value;
        self->flags = DESCRIPTOR_VALUE;
    }

    return (PyObject *) self;
}

PyObject *make_descriptor(jclass (*initializeClass)(void))
{
    t_descriptor *self = (t_descriptor *)
        ConstVariableDescriptorType.tp_alloc(&ConstVariableDescriptorType, 0);

    if (self)
    {
        self->access.initializeClass = initializeClass;
        self->flags = DESCRIPTOR_CLASS;
    }

    return (PyObject *) self;
}

PyObject *make_descriptor(PyObject *value)
{
    t_descriptor *self = (t_descriptor *)
        ConstVariableDescriptorType.tp_alloc(&ConstVariableDescriptorType, 0);

    if (self)
    {
        self->access.value = value;
        self->flags = DESCRIPTOR_VALUE;
    }
    else
        Py_DECREF(value);

    return (PyObject *) self;
}

PyObject *make_descriptor(PyObject *(*wrapfn)(const jobject &))
{
    return make_descriptor(PyCObject_FromVoidPtr((void *) wrapfn, NULL));
}

PyObject *make_descriptor(jboolean b)
{
    t_descriptor *self = (t_descriptor *)
        ConstVariableDescriptorType.tp_alloc(&ConstVariableDescriptorType, 0);

    if (self)
    {
        PyObject *value = b ? Py_True : Py_False;
        self->access.value = (PyObject *) value; Py_INCREF(value);
        self->flags = DESCRIPTOR_VALUE;
    }

    return (PyObject *) self;
}

PyObject *make_descriptor(jbyte value)
{
    t_descriptor *self = (t_descriptor *)
        ConstVariableDescriptorType.tp_alloc(&ConstVariableDescriptorType, 0);

    if (self)
    {
        self->access.value = PyString_FromStringAndSize((char *) &value, 1);
        self->flags = DESCRIPTOR_VALUE;
    }

    return (PyObject *) self;
}

PyObject *make_descriptor(jchar value)
{
    t_descriptor *self = (t_descriptor *)
        ConstVariableDescriptorType.tp_alloc(&ConstVariableDescriptorType, 0);

    if (self)
    {
        Py_UNICODE pchar = (Py_UNICODE) value;

        self->access.value = PyUnicode_FromUnicode(&pchar, 1);
        self->flags = DESCRIPTOR_VALUE;
    }

    return (PyObject *) self;
}

PyObject *make_descriptor(jdouble value)
{
    t_descriptor *self = (t_descriptor *)
        ConstVariableDescriptorType.tp_alloc(&ConstVariableDescriptorType, 0);

    if (self)
    {
        self->access.value = PyFloat_FromDouble(value);
        self->flags = DESCRIPTOR_VALUE;
    }

    return (PyObject *) self;
}

PyObject *make_descriptor(jfloat value)
{
    t_descriptor *self = (t_descriptor *)
        ConstVariableDescriptorType.tp_alloc(&ConstVariableDescriptorType, 0);

    if (self)
    {
        self->access.value = PyFloat_FromDouble((double) value);
        self->flags = DESCRIPTOR_VALUE;
    }

    return (PyObject *) self;
}

PyObject *make_descriptor(jint value)
{
    t_descriptor *self = (t_descriptor *)
        ConstVariableDescriptorType.tp_alloc(&ConstVariableDescriptorType, 0);

    if (self)
    {
        self->access.value = PyInt_FromLong(value);
        self->flags = DESCRIPTOR_VALUE;
    }

    return (PyObject *) self;
}

PyObject *make_descriptor(jlong value)
{
    t_descriptor *self = (t_descriptor *)
        ConstVariableDescriptorType.tp_alloc(&ConstVariableDescriptorType, 0);

    if (self)
    {
        self->access.value = PyLong_FromLongLong((long long) value);
        self->flags = DESCRIPTOR_VALUE;
    }

    return (PyObject *) self;
}

PyObject *make_descriptor(jshort value)
{
    t_descriptor *self = (t_descriptor *)
        ConstVariableDescriptorType.tp_alloc(&ConstVariableDescriptorType, 0);

    if (self)
    {
        self->access.value = PyInt_FromLong((short) value);
        self->flags = DESCRIPTOR_VALUE;
    }

    return (PyObject *) self;
}

static PyObject *t_descriptor___get__(t_descriptor *self,
                                      PyObject *obj, PyObject *type)
{
    if (self->flags & DESCRIPTOR_VALUE)
    {
        Py_INCREF(self->access.value);
        return self->access.value;
    }

    if (self->flags & DESCRIPTOR_CLASS)
        return t_Class::wrap_Object(Class((*self->access.initializeClass)()));

    Py_RETURN_NONE;
}

