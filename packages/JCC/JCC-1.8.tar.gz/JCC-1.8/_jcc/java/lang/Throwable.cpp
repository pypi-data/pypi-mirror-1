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
#include "java/lang/Object.h"
#include "java/lang/Class.h"
#include "java/lang/String.h"
#include "java/lang/Throwable.h"

namespace java {
    namespace lang {

        enum {
            mid_printStackTrace,
            mid_getMessage,
            max_mid
        };

        Class *Throwable::class$ = NULL;
        jmethodID *Throwable::_mids = NULL;

        jclass Throwable::initializeClass()
        {
            if (!class$)
            {
                jclass cls = env->findClass("java/lang/Throwable");

                _mids = new jmethodID[max_mid];
                _mids[mid_printStackTrace] = 
                    env->getMethodID(cls, "printStackTrace",
                                     "()V");
                _mids[mid_getMessage] = 
                    env->getMethodID(cls, "getMessage",
                                     "()Ljava/lang/String;");

                class$ = (Class *) new JObject(cls);
            }

            return (jclass) class$->this$;
        }

        void Throwable::printStackTrace() const
        {
            env->callVoidMethod(this$, _mids[mid_printStackTrace]);
        }
        
        String Throwable::getMessage() const
        {
            return String(env->callObjectMethod(this$, _mids[mid_getMessage]));
        }
    }
}


#include "structmember.h"
#include "functions.h"
#include "macros.h"

namespace java {
    namespace lang {

        static PyObject *t_Throwable_printStackTrace(t_Throwable *self);

        static PyMethodDef t_Throwable__methods_[] = {
            DECLARE_METHOD(t_Throwable, printStackTrace, METH_NOARGS),
            { NULL, NULL, 0, NULL }
        };

        DECLARE_TYPE(Throwable, t_Throwable, Object, java::lang::Throwable,
                     abstract_init, 0, 0, 0, 0, 0);

        static PyObject *t_Throwable_printStackTrace(t_Throwable *self)
        {
            OBJ_CALL(self->object.printStackTrace());
            Py_RETURN_NONE;
        }
    }
}
