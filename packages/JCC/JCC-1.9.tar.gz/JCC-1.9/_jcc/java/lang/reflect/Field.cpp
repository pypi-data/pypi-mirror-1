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
#include "java/lang/reflect/Field.h"

namespace java {
    namespace lang {
        namespace reflect {

            enum {
                mid_getModifiers,
                mid_getType,
                mid_getName,
                max_mid
            };

            Class *Field::class$ = NULL;
            jmethodID *Field::_mids = NULL;

            jclass Field::initializeClass()
            {
                if (!class$)
                {
                    jclass cls = env->findClass("java/lang/reflect/Field");

                    _mids = new jmethodID[max_mid];
                    _mids[mid_getModifiers] =
                        env->getMethodID(cls, "getModifiers",
                                         "()I");
                    _mids[mid_getType] =
                        env->getMethodID(cls, "getType",
                                         "()Ljava/lang/Class;");
                    _mids[mid_getName] =
                        env->getMethodID(cls, "getName",
                                         "()Ljava/lang/String;");

                    class$ = (Class *) new JObject(cls);
                }

                return (jclass) class$->this$;
            }

            int Field::getModifiers() const
            {
                return env->callIntMethod(this$, _mids[mid_getModifiers]);
            }

            Class Field::getType() const
            {
                return Class(env->callObjectMethod(this$, _mids[mid_getType]));
            }

            String Field::getName() const
            {
                return String(env->callObjectMethod(this$, _mids[mid_getName]));
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

            static PyObject *t_Field_getModifiers(t_Field *self);
            static PyObject *t_Field_getType(t_Field *self);
            static PyObject *t_Field_getName(t_Field *self);

            static PyMethodDef t_Field__methods_[] = {
                DECLARE_METHOD(t_Field, getModifiers, METH_NOARGS),
                DECLARE_METHOD(t_Field, getType, METH_NOARGS),
                DECLARE_METHOD(t_Field, getName, METH_NOARGS),
                { NULL, NULL, 0, NULL }
            };

            DECLARE_TYPE(Field, t_Field, Object, Field,
                         abstract_init, 0, 0, 0, 0, 0);

            static PyObject *t_Field_getModifiers(t_Field *self)
            {
                jint modifiers;

                OBJ_CALL(modifiers = self->object.getModifiers());
                return PyInt_FromLong(modifiers);
            }

            static PyObject *t_Field_getType(t_Field *self)
            {
                Class cls((jobject) NULL);

                OBJ_CALL(cls = self->object.getType());
                return t_Class::wrapObject(cls);
            }

            static PyObject *t_Field_getName(t_Field *self)
            {
                String name((jobject) NULL);

                OBJ_CALL(name = self->object.getName());
                return j2p(name);
            }
        }
    }
}
