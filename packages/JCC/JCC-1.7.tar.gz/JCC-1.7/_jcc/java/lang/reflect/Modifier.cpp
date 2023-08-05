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
#include "java/lang/Class.h"
#include "java/lang/Object.h"
#include "java/lang/String.h"
#include "java/lang/reflect/Modifier.h"

namespace java {
    namespace lang {
        namespace reflect {

            enum {
                mid_isPublic,
                mid_isStatic,
                mid_isNative,
                mid_isFinal,
                mid_isAbstract,
                mid_isPrivate,
                mid_isProtected,
                max_mid
            };

            Class *Modifier::class$ = NULL;
            jmethodID *Modifier::_mids = NULL;

            jclass Modifier::initializeClass()
            {
                if (!class$)
                {
                    jclass cls = env->findClass("java/lang/reflect/Modifier");

                    _mids = new jmethodID[max_mid];
                    _mids[mid_isPublic] =
                        env->getStaticMethodID(cls, "isPublic",
                                               "(I)Z");
                    _mids[mid_isStatic] =
                        env->getStaticMethodID(cls, "isStatic",
                                               "(I)Z");
                    _mids[mid_isNative] =
                        env->getStaticMethodID(cls, "isNative",
                                               "(I)Z");
                    _mids[mid_isFinal] =
                        env->getStaticMethodID(cls, "isFinal",
                                               "(I)Z");
                    _mids[mid_isAbstract] =
                        env->getStaticMethodID(cls, "isAbstract",
                                               "(I)Z");
                    _mids[mid_isPrivate] =
                        env->getStaticMethodID(cls, "isPrivate",
                                               "(I)Z");
                    _mids[mid_isProtected] =
                        env->getStaticMethodID(cls, "isProtected",
                                               "(I)Z");

                    class$ = (Class *) new JObject(cls);
                }
                
                return (jclass) class$->this$;
            }

            int Modifier::isPublic(int mod)
            {
                jclass cls = initializeClass();
                return (int) env->callStaticBooleanMethod(cls, _mids[mid_isPublic], mod);
            }

            int Modifier::isStatic(int mod)
            {
                jclass cls = initializeClass();
                return (int) env->callStaticBooleanMethod(cls, _mids[mid_isStatic], mod);
            }

            int Modifier::isNative(int mod)
            {
                jclass cls = initializeClass();
                return (int) env->callStaticBooleanMethod(cls, _mids[mid_isNative], mod);
            }

            int Modifier::isFinal(int mod)
            {
                jclass cls = initializeClass();
                return (int) env->callStaticBooleanMethod(cls, _mids[mid_isFinal], mod);
            }

            int Modifier::isAbstract(int mod)
            {
                jclass cls = initializeClass();
                return (int) env->callStaticBooleanMethod(cls, _mids[mid_isAbstract], mod);
            }

            int Modifier::isPrivate(int mod)
            {
                jclass cls = initializeClass();
                return (int) env->callStaticBooleanMethod(cls, _mids[mid_isPrivate], mod);
            }

            int Modifier::isProtected(int mod)
            {
                jclass cls = initializeClass();
                return (int) env->callStaticBooleanMethod(cls, _mids[mid_isProtected], mod);
            }
        }
    }
}


#include "structmember.h"
#include "functions.h"
#include "macros.h"

namespace java {
    namespace lang {
        namespace reflect {

            static PyObject *t_Modifier_isPublic(PyTypeObject *type, PyObject *arg);
            static PyObject *t_Modifier_isStatic(PyTypeObject *type, PyObject *arg);
            static PyObject *t_Modifier_isNative(PyTypeObject *type, PyObject *arg);
            static PyObject *t_Modifier_isFinal(PyTypeObject *type, PyObject *arg);
            static PyObject *t_Modifier_isAbstract(PyTypeObject *type, PyObject *arg);
            static PyObject *t_Modifier_isPrivate(PyTypeObject *type, PyObject *arg);
            static PyObject *t_Modifier_isProtected(PyTypeObject *type, PyObject *arg);

            static PyMethodDef t_Modifier__methods_[] = {
                DECLARE_METHOD(t_Modifier, isPublic, METH_O | METH_CLASS),
                DECLARE_METHOD(t_Modifier, isStatic, METH_O | METH_CLASS),
                DECLARE_METHOD(t_Modifier, isNative, METH_O | METH_CLASS),
                DECLARE_METHOD(t_Modifier, isFinal, METH_O | METH_CLASS),
                DECLARE_METHOD(t_Modifier, isAbstract, METH_O | METH_CLASS),
                DECLARE_METHOD(t_Modifier, isPrivate, METH_O | METH_CLASS),
                DECLARE_METHOD(t_Modifier, isProtected, METH_O | METH_CLASS),
                { NULL, NULL, 0, NULL }
            };

            DECLARE_TYPE(Modifier, t_Modifier, Object, Modifier,
                         abstract_init, 0, 0, 0, 0, 0);

            static PyObject *t_Modifier_isPublic(PyTypeObject *type, PyObject *arg)
            {
                if (!PyInt_Check(arg))
                {
                    PyErr_SetObject(PyExc_TypeError, arg);
                    return NULL;
                }

                try {
                    int mod = PyInt_AsLong(arg);
                    int isPublic = Modifier::isPublic(mod);

                    Py_RETURN_BOOL(isPublic);
                } catch (JCCEnv::exception e) {
                    return PyErr_SetJavaError(e.throwable);
                }
            }

            static PyObject *t_Modifier_isStatic(PyTypeObject *type, PyObject *arg)
            {
                if (!PyInt_Check(arg))
                {
                    PyErr_SetObject(PyExc_TypeError, arg);
                    return NULL;
                }

                try {
                    int mod = PyInt_AsLong(arg);
                    int isStatic = Modifier::isStatic(mod);

                    Py_RETURN_BOOL(isStatic);
                } catch (JCCEnv::exception e) {
                    return PyErr_SetJavaError(e.throwable);
                }
            }

            static PyObject *t_Modifier_isNative(PyTypeObject *type, PyObject *arg)
            {
                if (!PyInt_Check(arg))
                {
                    PyErr_SetObject(PyExc_TypeError, arg);
                    return NULL;
                }

                try {
                    int mod = PyInt_AsLong(arg);
                    int isNative = Modifier::isNative(mod);

                    Py_RETURN_BOOL(isNative);
                } catch (JCCEnv::exception e) {
                    return PyErr_SetJavaError(e.throwable);
                }
            }

            static PyObject *t_Modifier_isFinal(PyTypeObject *type, PyObject *arg)
            {
                if (!PyInt_Check(arg))
                {
                    PyErr_SetObject(PyExc_TypeError, arg);
                    return NULL;
                }

                try {
                    int mod = PyInt_AsLong(arg);
                    int isFinal = Modifier::isFinal(mod);

                    Py_RETURN_BOOL(isFinal);
                } catch (JCCEnv::exception e) {
                    return PyErr_SetJavaError(e.throwable);
                }
            }

            static PyObject *t_Modifier_isAbstract(PyTypeObject *type, PyObject *arg)
            {
                if (!PyInt_Check(arg))
                {
                    PyErr_SetObject(PyExc_TypeError, arg);
                    return NULL;
                }

                try {
                    int mod = PyInt_AsLong(arg);
                    int isAbstract = Modifier::isAbstract(mod);

                    Py_RETURN_BOOL(isAbstract);
                } catch (JCCEnv::exception e) {
                    return PyErr_SetJavaError(e.throwable);
                }
            }

            static PyObject *t_Modifier_isPrivate(PyTypeObject *type, PyObject *arg)
            {
                if (!PyInt_Check(arg))
                {
                    PyErr_SetObject(PyExc_TypeError, arg);
                    return NULL;
                }

                try {
                    int mod = PyInt_AsLong(arg);
                    int isPrivate = Modifier::isPrivate(mod);

                    Py_RETURN_BOOL(isPrivate);
                } catch (JCCEnv::exception e) {
                    return PyErr_SetJavaError(e.throwable);
                }
            }

            static PyObject *t_Modifier_isProtected(PyTypeObject *type, PyObject *arg)
            {
                if (!PyInt_Check(arg))
                {
                    PyErr_SetObject(PyExc_TypeError, arg);
                    return NULL;
                }

                try {
                    int mod = PyInt_AsLong(arg);
                    int isProtected = Modifier::isProtected(mod);

                    Py_RETURN_BOOL(isProtected);
                } catch (JCCEnv::exception e) {
                    return PyErr_SetJavaError(e.throwable);
                }
            }
        }
    }
}
