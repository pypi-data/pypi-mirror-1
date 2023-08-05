/* ====================================================================
 * Copyright (c) 2007-2007 Open Source Applications Foundation.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions: 
 *
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software. 
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 * ====================================================================
 */

#include <jni.h>
#include "JCCEnv.h"

#include <Python.h>
#include "structmember.h"

#include "JObject.h"
#include "macros.h"


/* JObject */

static void t_JObject_dealloc(t_JObject *self);
static PyObject *t_JObject_new(PyTypeObject *type,
                               PyObject *args, PyObject *kwds);

static PyObject *t_JObject_richcmp(t_JObject *, PyObject *o2, int op);
static PyObject *t_JObject_str(t_JObject *self);
static PyObject *t_JObject_repr(t_JObject *self);
static int t_JObject_hash(t_JObject *self);
static PyObject *t_JObject__getObj(t_JObject *self, void *data);

static PyMemberDef t_JObject_members[] = {
    { NULL, 0, 0, 0, NULL }
};

static PyMethodDef t_JObject_methods[] = {
    { NULL, NULL, 0, NULL }
};

static PyGetSetDef t_JObject_properties[] = {
    { "_obj", (getter) t_JObject__getObj, NULL, NULL, NULL },
    { NULL, NULL, NULL, NULL, NULL }
};

PyTypeObject JObjectType = {
    PyObject_HEAD_INIT(NULL)
    0,                                   /* ob_size */
    "jcc.JObject",                       /* tp_name */
    sizeof(t_JObject),                   /* tp_basicsize */
    0,                                   /* tp_itemsize */
    (destructor)t_JObject_dealloc,       /* tp_dealloc */
    0,                                   /* tp_print */
    0,                                   /* tp_getattr */
    0,                                   /* tp_setattr */
    0,                                   /* tp_compare */
    (reprfunc)t_JObject_repr,            /* tp_repr */
    0,                                   /* tp_as_number */
    0,                                   /* tp_as_sequence */
    0,                                   /* tp_as_mapping */
    (hashfunc)t_JObject_hash,            /* tp_hash  */
    0,                                   /* tp_call */
    (reprfunc)t_JObject_str,             /* tp_str */
    0,                                   /* tp_getattro */
    0,                                   /* tp_setattro */
    0,                                   /* tp_as_buffer */
    (Py_TPFLAGS_DEFAULT |
     Py_TPFLAGS_BASETYPE),               /* tp_flags */
    "t_JObject objects",                 /* tp_doc */
    0,                                   /* tp_traverse */
    0,                                   /* tp_clear */
    (richcmpfunc)t_JObject_richcmp,      /* tp_richcompare */
    0,                                   /* tp_weaklistoffset */
    0,                                   /* tp_iter */
    0,                                   /* tp_iternext */
    t_JObject_methods,                   /* tp_methods */
    t_JObject_members,                   /* tp_members */
    t_JObject_properties,                /* tp_getset */
    0,                                   /* tp_base */
    0,                                   /* tp_dict */
    0,                                   /* tp_descr_get */
    0,                                   /* tp_descr_set */
    0,                                   /* tp_dictoffset */
    0,                                   /* tp_init */
    0,                                   /* tp_alloc */
    (newfunc)t_JObject_new,              /* tp_new */
};


static void t_JObject_dealloc(t_JObject *self)
{
    self->object = JObject(NULL);
    self->ob_type->tp_free((PyObject *) self);
}

static PyObject *t_JObject_new(PyTypeObject *type,
                               PyObject *args, PyObject *kwds)
{
    t_JObject *self = (t_JObject *) type->tp_alloc(type, 0);

    self->object = JObject(NULL);

    return (PyObject *) self;
}

static PyObject *t_JObject_richcmp(t_JObject *self, PyObject *arg, int op)
{
    int b = 0;

    switch (op) {
      case Py_EQ:
      case Py_NE:
        if (PyObject_TypeCheck(arg, &JObjectType))
            b = self->object == ((t_JObject *) arg)->object;
        if (op == Py_EQ)
            Py_RETURN_BOOL(b);
        Py_RETURN_BOOL(!b);
      case Py_LT:
        PyErr_SetString(PyExc_NotImplementedError, "<");
        return NULL;
      case Py_LE:
        PyErr_SetString(PyExc_NotImplementedError, "<=");
        return NULL;
      case Py_GT:
        PyErr_SetString(PyExc_NotImplementedError, ">");
        return NULL;
      case Py_GE:
        PyErr_SetString(PyExc_NotImplementedError, ">=");
        return NULL;
    }

    return NULL;
}

static PyObject *t_JObject_str(t_JObject *self)
{
    if (self->object.this$)
    {
        char *utf = env->toString(self->object.this$);
        PyObject *unicode = PyUnicode_DecodeUTF8(utf, strlen(utf), "strict");

        delete utf;
        return unicode;
    }

    return PyString_FromString("<null>");
}

static PyObject *t_JObject_repr(t_JObject *self)
{
    PyObject *name = PyObject_GetAttrString((PyObject *) self->ob_type,
                                            "__name__");
    PyObject *str = self->ob_type->tp_str((PyObject *) self);
#if PY_VERSION_HEX < 0x02040000
    PyObject *args = Py_BuildValue("(OO)", name, str);
#else
    PyObject *args = PyTuple_Pack(2, name, str);
#endif
    PyObject *format = PyString_FromString("<%s: %s>");
    PyObject *repr = PyString_Format(format, args);

    Py_DECREF(name);
    Py_DECREF(str);
    Py_DECREF(args);
    Py_DECREF(format);

    return repr;
}

static int t_JObject_hash(t_JObject *self)
{
    return env->hash(self->object.this$);
}

static PyObject *t_JObject__getObj(t_JObject *self, void *data)
{
    return PyInt_FromLong((long) self->object.this$);
}
