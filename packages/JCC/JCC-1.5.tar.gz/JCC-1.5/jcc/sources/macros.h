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

#ifndef _macros_H
#define _macros_H

#define OBJ_CALL(action)                                                \
    {                                                                   \
        try {                                                           \
            PythonThreadState state;                                    \
            action;                                                     \
        } catch (JCCEnv::pythonError) {                                 \
            return NULL;                                                \
        } catch (JCCEnv::exception e) {                                 \
            return PyErr_SetJavaError(e.throwable);                     \
        }                                                               \
    }

#define INT_CALL(action)                                                \
    {                                                                   \
        try {                                                           \
            PythonThreadState state;                                    \
            action;                                                     \
        } catch (JCCEnv::pythonError) {                                 \
            return -1;                                                  \
        } catch (JCCEnv::exception e) {                                 \
            PyErr_SetJavaError(e.throwable);                            \
            return -1;                                                  \
        }                                                               \
    }


#define DECLARE_METHOD(type, name, flags)               \
    { #name, (PyCFunction) type##_##name, flags, "" }

#define DECLARE_GET_FIELD(type, name)           \
    { #name, (getter) type##_get__##name, NULL, "", NULL }

#define DECLARE_SET_FIELD(type, name)           \
    { #name, NULL, (setter) type##_set__##name, "", NULL }

#define DECLARE_GETSET_FIELD(type, name)        \
    { #name, (getter) type##_get__##name, (setter) type##_set__##name, "", NULL }


#define DECLARE_TYPE(name, t_name, base, javaClass,                         \
                     init, iter, iternext, getset, mapping, sequence)       \
PyTypeObject name##Type = {                                                 \
    PyObject_HEAD_INIT(NULL)                                                \
    /* ob_size            */   0,                                           \
    /* tp_name            */   #name,                                       \
    /* tp_basicsize       */   sizeof(t_name),                              \
    /* tp_itemsize        */   0,                                           \
    /* tp_dealloc         */   0,                                           \
    /* tp_print           */   0,                                           \
    /* tp_getattr         */   0,                                           \
    /* tp_setattr         */   0,                                           \
    /* tp_compare         */   0,                                           \
    /* tp_repr            */   0,                                           \
    /* tp_as_number       */   0,                                           \
    /* tp_as_sequence     */   sequence,                                    \
    /* tp_as_mapping      */   mapping,                                     \
    /* tp_hash            */   0,                                           \
    /* tp_call            */   0,                                           \
    /* tp_str             */   0,                                           \
    /* tp_getattro        */   0,                                           \
    /* tp_setattro        */   0,                                           \
    /* tp_as_buffer       */   0,                                           \
    /* tp_flags           */   Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,    \
    /* tp_doc             */   #t_name" objects",                           \
    /* tp_traverse        */   0,                                           \
    /* tp_clear           */   0,                                           \
    /* tp_richcompare     */   0,                                           \
    /* tp_weaklistoffset  */   0,                                           \
    /* tp_iter            */   (getiterfunc) iter,                          \
    /* tp_iternext        */   (iternextfunc) iternext,                     \
    /* tp_methods         */   t_name##__methods_,                          \
    /* tp_members         */   0,                                           \
    /* tp_getset          */   getset,                                      \
    /* tp_base            */   &base##Type,                                 \
    /* tp_dict            */   0,                                           \
    /* tp_descr_get       */   0,                                           \
    /* tp_descr_set       */   0,                                           \
    /* tp_dictoffset      */   0,                                           \
    /* tp_init            */   (initproc)init,                              \
    /* tp_alloc           */   0,                                           \
    /* tp_new             */   0,                                           \
};                                                                          \
PyObject *t_name::wrapObject(const javaClass& object)                   \
{                                                                       \
    if (!object.isNull())                                               \
    {                                                                   \
        t_name *self = (t_name *) name##Type.tp_alloc(&name##Type, 0);  \
        if (self)                                                       \
            self->object = object;                                      \
        return (PyObject *) self;                                       \
    }                                                                   \
    Py_RETURN_NONE;                                                     \
}


#define INSTALL_TYPE(name, module)                                   \
    if (PyType_Ready(&name##Type) == 0)                              \
    {                                                                \
        Py_INCREF(&name##Type);                                      \
        PyModule_AddObject(module, #name, (PyObject *) &name##Type); \
    }


#define Py_RETURN_BOOL(b)                       \
    {                                           \
        if (b)                                  \
            Py_RETURN_TRUE;                     \
        else                                    \
            Py_RETURN_FALSE;                    \
    }

#if PY_VERSION_HEX < 0x02040000
#define Py_RETURN_NONE return Py_INCREF(Py_None), Py_None
#define Py_RETURN_TRUE return Py_INCREF(Py_True), Py_True
#define Py_RETURN_FALSE return Py_INCREF(Py_False), Py_False
#endif

#endif /* _macros_H */
