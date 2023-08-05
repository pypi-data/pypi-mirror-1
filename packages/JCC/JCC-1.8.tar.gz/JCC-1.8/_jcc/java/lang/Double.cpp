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
#include "java/lang/Double.h"

namespace java {
    namespace lang {

        enum {
            mid__init_,
            max_mid
        };

        Class *Double::class$ = NULL;
        jmethodID *Double::_mids = NULL;
        
        jclass Double::initializeClass()
        {
            if (!class$)
            {
                jclass cls = env->findClass("java/lang/Double");

                _mids = new jmethodID[max_mid];
                _mids[mid__init_] = env->getMethodID(cls, "<init>", "(D)V");

                class$ = (Class *) new JObject(cls);
            }

            return (jclass) class$->this$;
        }

        Double::Double(jdouble n) : Object(env->newObject(initializeClass, &_mids, mid__init_, n)) {
        }
    }
}


#include "structmember.h"
#include "functions.h"
#include "macros.h"

namespace java {
    namespace lang {

        static PyMethodDef t_Double__methods_[] = {
            { NULL, NULL, 0, NULL }
        };

        DECLARE_TYPE(Double, t_Double, Object, java::lang::Double,
                     abstract_init, 0, 0, 0, 0, 0);
    }
}
