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
#include <string.h>
#include "JCCEnv.h"
#include "java/lang/Object.h"
#include "java/lang/Class.h"
#include "java/lang/String.h"

namespace java {
    namespace lang {

        enum {
            mid__init_,
            mid_toString,
            mid_length,
            max_mid
        };

        Class *String::class$ = NULL;
        jmethodID *String::_mids = NULL;

        jclass String::initializeClass()
        {
            if (!class$)
            {
                jclass cls = env->findClass("java/lang/String");

                _mids = new jmethodID[max_mid];
                _mids[mid__init_] = 
                    env->getMethodID(cls, "<init>",
                                     "()V");
                _mids[mid_toString] = 
                    env->getMethodID(cls, "toString",
                                     "()Ljava/lang/String;");
                _mids[mid_length] = 
                    env->getMethodID(cls, "length",
                                     "()I");

                class$ = (Class *) new JObject(cls);
            }

            return (jclass) class$->this$;
        }

        String::String() : Object(env->newObject(initializeClass, &_mids, mid__init_)) {
        }

        int String::length() const
        {
            return env->callIntMethod(this$, _mids[mid_length]);
        }
    }
}


#include "structmember.h"
#include "functions.h"
#include "macros.h"

namespace java {
    namespace lang {

        static int t_String_init(t_String *self,
                                 PyObject *args, PyObject *kwds);
        static PyObject *t_String_length(t_String *self);

        static PyMethodDef t_String__methods_[] = {
            DECLARE_METHOD(t_String, length, METH_NOARGS),
            { NULL, NULL, 0, NULL }
        };

        DECLARE_TYPE(String, t_String, Object, java::lang::String,
                     t_String_init, 0, 0, 0, 0, 0);

        static int t_String_init(t_String *self,
                                 PyObject *args, PyObject *kwds)
        {
            char *bytes;

            switch (PyTuple_Size(args)) {
              case 0:
                INT_CALL(self->object = String());
                break;
              case 1:
                if (!PyArg_ParseTuple(args, "s", &bytes))
                    return -1;
                INT_CALL(self->object = String(env->fromUTF(bytes)));
                break;
              default:
                PyErr_SetString(PyExc_ValueError, "invalid args");
                return -1;
            }
        
            return 0;
        }

        static PyObject *t_String_length(t_String *self)
        {
            jint length;

            OBJ_CALL(length = self->object.length());
            return PyInt_FromLong(length);
        }
    }
}
