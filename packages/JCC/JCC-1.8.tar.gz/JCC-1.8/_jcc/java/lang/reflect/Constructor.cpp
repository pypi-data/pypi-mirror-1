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
#include "JArray.h"

#include "java/lang/Class.h"
#include "java/lang/Object.h"
#include "java/lang/String.h"
#include "java/lang/reflect/Constructor.h"

namespace java {
    namespace lang {
        namespace reflect {

            enum {
                mid_getModifiers,
                mid_getSignature,
                mid_getParameterTypes,
                mid_getExceptionTypes,
                max_mid
            };

            Class *Constructor::class$ = NULL;
            jmethodID *Constructor::_mids = NULL;

            jclass Constructor::initializeClass()
            {
                if (!class$)
                {
                    jclass cls = env->findClass("java/lang/reflect/Constructor");

                    _mids = new jmethodID[max_mid];
                    _mids[mid_getModifiers] =
                        env->getMethodID(cls, "getModifiers",
                                         "()I");
                    _mids[mid_getParameterTypes] =
                        env->getMethodID(cls, "getParameterTypes",
                                         "()[Ljava/lang/Class;");
                    _mids[mid_getExceptionTypes] =
                        env->getMethodID(cls, "getExceptionTypes",
                                         "()[Ljava/lang/Class;");

                    class$ = (Class *) new JObject(cls);
                }
                
                return (jclass) class$->this$;
            }

            int Constructor::getModifiers() const
            {
                return env->callIntMethod(this$, _mids[mid_getModifiers]);
            }

            JArray<Class> Constructor::getParameterTypes() const
            {
                jobjectArray array = (jobjectArray)
                    env->callObjectMethod(this$, _mids[mid_getParameterTypes]);

                return JArray<Class>(array);
            }

            JArray<Class> Constructor::getExceptionTypes() const
            {
                jobjectArray array = (jobjectArray)
                    env->callObjectMethod(this$, _mids[mid_getExceptionTypes]);

                return JArray<Class>(array);
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

            static PyObject *t_Constructor_getModifiers(t_Constructor *self);
            static PyObject *t_Constructor_getParameterTypes(t_Constructor *self);
            static PyObject *t_Constructor_getExceptionTypes(t_Constructor *self);

            static PyMethodDef t_Constructor__methods_[] = {
                DECLARE_METHOD(t_Constructor, getModifiers, METH_NOARGS),
                DECLARE_METHOD(t_Constructor, getParameterTypes, METH_NOARGS),
                DECLARE_METHOD(t_Constructor, getExceptionTypes, METH_NOARGS),
                { NULL, NULL, 0, NULL }
            };

            DECLARE_TYPE(Constructor, t_Constructor, Object, Constructor,
                         abstract_init, 0, 0, 0, 0, 0);

            static PyObject *t_Constructor_getModifiers(t_Constructor *self)
            {
                jint modifiers;

                OBJ_CALL(modifiers = self->object.getModifiers());
                return PyInt_FromLong(modifiers);                
            }

            static PyObject *t_Constructor_getParameterTypes(t_Constructor *self)
            {
                JArray<Class> types((jobject) NULL);
                OBJ_CALL(types = self->object.getParameterTypes());
                return types.toSequence(t_Class::wrapObject);
            }

            static PyObject *t_Constructor_getExceptionTypes(t_Constructor *self)
            {
                JArray<Class> types((jobject) NULL);
                OBJ_CALL(types = self->object.getExceptionTypes());
                return types.toSequence(t_Class::wrapObject);
            }
        }
    }
}
