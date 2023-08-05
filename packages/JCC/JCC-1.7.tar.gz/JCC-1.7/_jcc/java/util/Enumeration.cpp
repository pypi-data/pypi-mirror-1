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
#include "java/util/Enumeration.h"

namespace java {
    namespace util {
        enum {
            mid_hasMoreElements,
            mid_nextElement,
            max_mid
        };

        Class *Enumeration::class$ = NULL;
        jmethodID *Enumeration::mids$ = NULL;

        jclass Enumeration::initializeClass()
        {
            if (!class$)
            {
                jclass cls = env->findClass("java/util/Enumeration");

                mids$ = new jmethodID[max_mid];
                mids$[mid_hasMoreElements] = env->getMethodID(cls, "hasMoreElements", "()Z");
                mids$[mid_nextElement] = env->getMethodID(cls, "nextElement", "()Ljava/lang/Object;");

                class$ = (Class *) new JObject(cls);
            }

            return (jclass) class$->this$;
        }

        jboolean Enumeration::hasMoreElements() const
        {
            return env->callBooleanMethod(this$, mids$[mid_hasMoreElements]);
        }

        Object Enumeration::nextElement() const
        {
            return Object(env->callObjectMethod(this$, mids$[mid_nextElement]));
        }
    }
}


#include "structmember.h"
#include "functions.h"
#include "macros.h"

namespace java {
    namespace util {

        static PyObject *t_Enumeration_hasMoreElements(t_Enumeration *self);
        static PyObject *t_Enumeration_nextElement(t_Enumeration *self);

        static PyMethodDef t_Enumeration__methods_[] = {
            DECLARE_METHOD(t_Enumeration, hasMoreElements, METH_NOARGS),
            DECLARE_METHOD(t_Enumeration, nextElement, METH_NOARGS),
            { NULL, NULL, 0, NULL }
        };

        DECLARE_TYPE(Enumeration, t_Enumeration, JObject,
                     java::util::Enumeration, abstract_init, 0, 0, 0, 0, 0);

        static PyObject *t_Enumeration_hasMoreElements(t_Enumeration *self)
        {
            jboolean b;

            OBJ_CALL(b = self->object.hasMoreElements());
            Py_RETURN_BOOL(b);
        }

        static PyObject *t_Enumeration_nextElement(t_Enumeration *self)
        {
            Object nextElement((jobject) NULL);

            OBJ_CALL(nextElement = self->object.nextElement());
            return t_Object::wrapObject(nextElement);
        }
    }
}
