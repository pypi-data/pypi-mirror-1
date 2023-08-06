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

#ifndef _Enumeration_H
#define _Enumeration_H

#include <Python.h>
#include "JObject.h"

namespace java {
    namespace lang {
        class Class;
        class Object;
    }        
    namespace util {
        using namespace java::lang;

        class Enumeration : public JObject {
        public:
            static Class *class$;
            static jmethodID *mids$;
            static jclass initializeClass();

            explicit Enumeration(jobject obj) : JObject(obj) {
                initializeClass();
            }

            jboolean hasMoreElements() const;
            Object nextElement() const;
        };

        extern PyTypeObject EnumerationType;

        class t_Enumeration {
        public:
            PyObject_HEAD
            Enumeration object;
            static PyObject *wrapObject(const Enumeration& object);
        };
    }
}

#endif /* _Enumeration_H */
