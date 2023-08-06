/* ====================================================================
 * Copyright (c) 2007-2008 Open Source Applications Foundation.
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


_DLL_EXPORT JCCEnv *env;


/* JCCEnv */

class t_jccenv {
public:
    PyObject_HEAD
    JCCEnv *env;
};
    
static void t_jccenv_dealloc(t_jccenv *self);
static PyObject *t_jccenv_attachCurrentThread(PyObject *self, PyObject *args);
static PyObject *t_jccenv_detachCurrentThread(PyObject *self);
static PyObject *t_jccenv_strhash(PyObject *self, PyObject *arg);
static PyObject *t_jccenv__dumpRefs(PyObject *self,
                                    PyObject *args, PyObject *kwds);

static PyMemberDef t_jccenv_members[] = {
    { NULL, 0, 0, 0, NULL }
};

static PyMethodDef t_jccenv_methods[] = {
    { "attachCurrentThread", (PyCFunction) t_jccenv_attachCurrentThread,
      METH_VARARGS, NULL },
    { "detachCurrentThread", (PyCFunction) t_jccenv_detachCurrentThread,
      METH_NOARGS, NULL },
    { "strhash", (PyCFunction) t_jccenv_strhash,
      METH_O, NULL },
    { "_dumpRefs", (PyCFunction) t_jccenv__dumpRefs,
      METH_VARARGS | METH_KEYWORDS, NULL },
    { NULL, NULL, 0, NULL }
};

_DLL_EXPORT PyTypeObject JCCEnvType = {
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

static PyObject *t_jccenv_strhash(PyObject *self, PyObject *arg)
{
    int hash = PyObject_Hash(arg);
    char buffer[10];

    sprintf(buffer, "%08x", (unsigned int) hash);
    return PyString_FromStringAndSize(buffer, 8);
}

static PyObject *t_jccenv__dumpRefs(PyObject *self,
                                    PyObject *args, PyObject *kwds)
{
    static char *kwnames[] = {
        "classes", "values", NULL
    };
    int classes = 0, values = 0;
    PyObject *result;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|ii", kwnames,
                                     &classes, &values))
        return NULL;

    if (classes)
        result = PyDict_New();
    else
        result = PyList_New(env->refs.size());

    int count = 0;

    for (std::multimap<int, countedRef>::iterator iter = env->refs.begin();
         iter != env->refs.end();
         iter++) {
        if (classes)  // return dict of { class name: instance count }
        {
            char *name = env->getClassName(iter->second.global);
            PyObject *key = PyString_FromString(name);
            PyObject *value = PyDict_GetItem(result, key);

            if (value == NULL)
                value = PyInt_FromLong(1);
            else
                value = PyInt_FromLong(PyInt_AS_LONG(value) + 1);

            PyDict_SetItem(result, key, value);
            Py_DECREF(key);
            Py_DECREF(value);

            delete name;
        }
        else if (values)  // return list of (value string, ref count)
        {
            char *str = env->toString(iter->second.global);
            PyObject *key = PyString_FromString(str);
            PyObject *value = PyInt_FromLong(iter->second.count);

#if PY_VERSION_HEX < 0x02040000
            PyList_SET_ITEM(result, count++, Py_BuildValue("(OO)", key, value));
#else
            PyList_SET_ITEM(result, count++, PyTuple_Pack(2, key, value));
#endif
            Py_DECREF(key);
            Py_DECREF(value);

            delete str;
        }
        else  // return list of (id hash code, ref count)
        {
            PyObject *key = PyInt_FromLong(iter->first);
            PyObject *value = PyInt_FromLong(iter->second.count);

#if PY_VERSION_HEX < 0x02040000
            PyList_SET_ITEM(result, count++, Py_BuildValue("(OO)", key, value));
#else
            PyList_SET_ITEM(result, count++, PyTuple_Pack(2, key, value));
#endif
            Py_DECREF(key);
            Py_DECREF(value);
        }
    }

    return result;
}


_DLL_EXPORT PyObject *getVMEnv(PyObject *self)
{
    if (env)
    {
        t_jccenv *jccenv = (t_jccenv *) JCCEnvType.tp_alloc(&JCCEnvType, 0);
        jccenv->env = env;

        return (PyObject *) jccenv;
    }

    Py_RETURN_NONE;
}

_DLL_EXPORT PyObject *initVM(PyObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwnames[] = {
        "classpath", "initialheap", "maxheap", "maxstack",
        "vmargs", NULL
    };
    char *classpath = NULL;
    char *initialheap = NULL, *maxheap = NULL, *maxstack = NULL;
    char *vmargs = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|zzzzz", kwnames,
                                     &classpath,
                                     &initialheap, &maxheap, &maxstack,
                                     &vmargs))
        return NULL;

    if (env)
    {
        if (initialheap || maxheap || maxstack || vmargs)
        {
            PyErr_SetString(PyExc_ValueError,
                            "JVM is already running, options are ineffective");
            return NULL;
        }

        if (classpath)
            env->setClassPath(classpath);

        return getVMEnv(self);
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
            }
            free(buf);
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

        t_jccenv *jccenv = (t_jccenv *) JCCEnvType.tp_alloc(&JCCEnvType, 0);
        jccenv->env = new JCCEnv(vm, vm_env);

        return (PyObject *) jccenv;
    }
}
