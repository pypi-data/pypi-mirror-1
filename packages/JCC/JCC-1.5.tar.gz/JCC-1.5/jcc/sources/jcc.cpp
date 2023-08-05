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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <jni.h>

#include <Python.h>
#include "structmember.h"

#include "JCCEnv.h"
#include "java/lang/Class.h"
#include "java/lang/RuntimeException.h"
#include "functions.h"
#include "macros.h"

void __initialize__(PyObject *module);

JCCEnv *env;

using namespace java::lang;


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

static PyMemberDef t_descriptor_members[] = {
    { NULL, 0, 0, 0, NULL }
};

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
    t_descriptor_members,                /* tp_members */
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
        return t_Class::wrapObject(Class((*self->access.initializeClass)()));

    Py_RETURN_NONE;
}


/* JCCEnv */

class t_jccenv {
public:
    PyObject_HEAD
    JCCEnv *env;
};
    
static void t_jccenv_dealloc(t_jccenv *self);
static PyObject *t_jccenv_attachCurrentThread(PyObject *self, PyObject *args);
static PyObject *t_jccenv_detachCurrentThread(PyObject *self);
static PyObject *t_jccenv_findClass(PyObject *self, PyObject *args);
static PyObject *t_jccenv_strhash(PyObject *self, PyObject *arg);
static PyObject *t_jccenv__dumpRefs(PyObject *self);

static PyMemberDef t_jccenv_members[] = {
    { NULL, 0, 0, 0, NULL }
};

static PyMethodDef t_jccenv_methods[] = {
    { "attachCurrentThread", (PyCFunction) t_jccenv_attachCurrentThread,
      METH_VARARGS, NULL },
    { "detachCurrentThread", (PyCFunction) t_jccenv_detachCurrentThread,
      METH_NOARGS, NULL },
    { "findClass", (PyCFunction) t_jccenv_findClass,
      METH_VARARGS, NULL },
    { "strhash", (PyCFunction) t_jccenv_strhash,
      METH_O, NULL },
    { "_dumpRefs", (PyCFunction) t_jccenv__dumpRefs,
      METH_NOARGS, NULL },
    { NULL, NULL, 0, NULL }
};

PyTypeObject JCCEnvType = {
    PyObject_HEAD_INIT(NULL)
    0,                                   /* ob_size */
    "jcc.JCCEnv",                        /* tp_name */
    sizeof(t_jccenv),                    /* tp_basicsize */
    0,                                   /* tp_itemsize */
    (destructor)t_jccenv_dealloc,        /* tp_dealloc */
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
    "JCCEnv",                            /* tp_doc */
    0,                                   /* tp_traverse */
    0,                                   /* tp_clear */
    0,                                   /* tp_richcompare */
    0,                                   /* tp_weaklistoffset */
    0,                                   /* tp_iter */
    0,                                   /* tp_iternext */
    t_jccenv_methods,                    /* tp_methods */
    t_jccenv_members,                    /* tp_members */
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

static void t_jccenv_dealloc(t_jccenv *self)
{
    self->ob_type->tp_free((PyObject *) self);
}

static void add_option(char *name, char *value, JavaVMOption *option)
{
    char *buf = new char[strlen(name) + strlen(value) + 1];

    sprintf(buf, "%s%s", name, value);
    option->optionString = buf;
}

static PyObject *t_jccenv_attachCurrentThread(PyObject *self, PyObject *args)
{
    char *name = NULL;
    int asDaemon = 0, result;
    JNIEnv *jenv = NULL;

    if (!PyArg_ParseTuple(args, "|si", &name, &asDaemon))
        return NULL;

    JavaVMAttachArgs attach = {
        JNI_VERSION_1_2, name, NULL
    };

    if (asDaemon)
        result = env->vm->AttachCurrentThreadAsDaemon((void **) &jenv, &attach);
    else
        result = env->vm->AttachCurrentThread((void **) &jenv, &attach);

    env->set_vm_env(jenv);
        
    return PyInt_FromLong(result);
}

static PyObject *t_jccenv_detachCurrentThread(PyObject *self)
{
    int result = env->vm->DetachCurrentThread();
    return PyInt_FromLong(result);
}

static PyObject *t_jccenv_findClass(PyObject *self, PyObject *args)
{
    char *className;

    if (!PyArg_ParseTuple(args, "s", &className))
        return NULL;

    jclass cls;
    OBJ_CALL(cls = env->findClass(className));

    if (cls)
        return t_Class::wrapObject(Class(cls));

    Py_RETURN_NONE;
}

static PyObject *t_jccenv_strhash(PyObject *self, PyObject *arg)
{
    int hash = PyObject_Hash(arg);
    char buffer[10];

    sprintf(buffer, "%08x", (unsigned int) hash);
    return PyString_FromStringAndSize(buffer, 8);
}

static PyObject *t_jccenv__dumpRefs(PyObject *self)
{
    PyObject *result = PyDict_New();

    for (std::multimap<int, countedRef>::iterator iter = env->refs.begin();
         iter != env->refs.end();
         iter++)
        PyDict_SetItem(result,
                       PyInt_FromLong(iter->first),
                       PyInt_FromLong(iter->second.count));

    return result;
}


static PyObject *_setExceptionTypes(PyObject *self, PyObject *args)
{
    extern PyObject *PyExc_JavaError;
    extern PyObject *PyExc_InvalidArgsError;

    if (!PyArg_ParseTuple(args, "OO",
                          &PyExc_JavaError, &PyExc_InvalidArgsError))
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *initVM(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwnames[] = {
        "classpath", "initialheap", "maxheap", "maxstack",
        "vmargs", "env", NULL
    };
    char *classpath = NULL;
    char *initialheap = NULL, *maxheap = NULL, *maxstack = NULL;
    char *vmargs = NULL;
    t_jccenv *jccenv = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|zzzzzO", kwnames,
                                     &classpath,
                                     &initialheap, &maxheap, &maxstack,
                                     &vmargs, &jccenv))
        return NULL;

    if (jccenv)
    {
        if (!PyObject_TypeCheck((PyObject *) jccenv, &JCCEnvType))
        {
            PyErr_SetObject(PyExc_TypeError, (PyObject *) jccenv);
            return NULL;
        }

        if (env && jccenv->env != env)
        {
            env->vm->DestroyJavaVM();
            delete env;
            env = jccenv->env;
        }

        if (classpath)
            env->setClassPath(classpath);

        Py_INCREF((PyObject *) jccenv);
    }
    else
    {
        JavaVMInitArgs vm_args;
        JavaVMOption vm_options[32];
        JNIEnv *vm_env;
        JavaVM *vm;
        unsigned int nOptions = 0;

        vm_args.version = JNI_VERSION_1_4;
        JNI_GetDefaultJavaVMInitArgs(&vm_args);

        if (classpath)
            add_option("-Djava.class.path=", classpath,
                       &vm_options[nOptions++]);
        if (initialheap)
            add_option("-Xms", initialheap, &vm_options[nOptions++]);
        if (maxheap)
            add_option("-Xmx", maxheap, &vm_options[nOptions++]);
        if (maxstack)
            add_option("-Xss", maxstack, &vm_options[nOptions++]);

        if (vmargs)
        {
            char *buf = strdup(vmargs);
            char *sep = ",";
            char *option;

            for (option = strtok(buf, sep); option; option = strtok(NULL, sep))
            {
                if (nOptions < sizeof(vm_options) / sizeof(JavaVMOption))
                    add_option("", option, &vm_options[nOptions++]);
                else
                {
                    free(buf);
                    for (unsigned int i = 0; i < nOptions; i++)
                        delete vm_options[i].optionString;
                    PyErr_Format(PyExc_ValueError, "Too many options (> %d)",
                                 nOptions);
                    return NULL;
                }
                free(buf);
            }
        }

        //vm_options[nOptions++].optionString = "-verbose:gc";
        //vm_options[nOptions++].optionString = "-Xcheck:jni";

        vm_args.nOptions = nOptions;
        vm_args.ignoreUnrecognized = JNI_FALSE;
        vm_args.options = vm_options;

        if (JNI_CreateJavaVM(&vm, (void **) &vm_env, &vm_args) < 0)
        {
            for (unsigned int i = 0; i < nOptions; i++)
                delete vm_options[i].optionString;

            PyErr_Format(PyExc_ValueError,
                         "An error occurred while creating Java VM");
            return NULL;
        }

        for (unsigned int i = 0; i < nOptions; i++)
            delete vm_options[i].optionString;

        jccenv = (t_jccenv *) JCCEnvType.tp_alloc(&JCCEnvType, 0);
        jccenv->env = new JCCEnv(vm, vm_env);

#if PY_VERSION_HEX < 0x02040000
        PyEval_InitThreads();
#endif
    }

    java::lang::Class::initializeClass();
    java::lang::RuntimeException::initializeClass();
    __initialize__(self);

    return (PyObject *) jccenv;
}

static PyObject *getVMEnv(PyObject *self)
{
    if (env)
    {
        t_jccenv *jccenv = (t_jccenv *) JCCEnvType.tp_alloc(&JCCEnvType, 0);
        jccenv->env = env;

        return (PyObject *) jccenv;
    }

    Py_RETURN_NONE;
}

PyMethodDef module_funcs[] = {
    { "_setExceptionTypes", (PyCFunction) _setExceptionTypes,
      METH_VARARGS, NULL },
    { "initVM", (PyCFunction) initVM, METH_VARARGS | METH_KEYWORDS, NULL },
    { "getVMEnv", (PyCFunction) getVMEnv, METH_NOARGS, NULL },
    { NULL, NULL, 0, NULL }
};
