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

#ifndef _Integer_H
#define _Integer_H

#include <Python.h>
#include "java/lang/Object.h"
#include "java/lang/Class.h"

namespace java {
    namespace lang {

        class Integer : public Object {
        public:
            static Class *class$;
            static jmethodID *_mids;
            static jclass initializeClass();

            explicit Integer(jobject obj) : Object(obj) {
                initializeClass();
            }
            Integer(jint);
        };

        extern PyTypeObject IntegerType;

        class t_Integer {
        public:
            PyObject_HEAD
            Integer object;
            static PyObject *wrapObject(const Integer& object);
        };
    }
}

#endif /* _Integer_H */
