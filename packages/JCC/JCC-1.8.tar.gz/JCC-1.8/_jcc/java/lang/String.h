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

#ifndef _String_H
#define _String_H

#include <Python.h>
#include "java/lang/Object.h"
#include "java/lang/Class.h"
#include "JArray.h"

namespace java {
    namespace lang {

        class String : public Object {
        public:
            static Class *class$;
            static jmethodID *_mids;
            static jclass initializeClass();

            explicit String(jobject obj) : Object(obj) {
                initializeClass();
            }
            String();
            String(const String& obj) : Object(obj) {}

            String toString() const {
                return *this;
            }
            int length() const;
        };

        extern PyTypeObject StringType;

        class t_String {
        public:
            PyObject_HEAD
            String object;
            static PyObject *wrapObject(const String& object);
        };
    }
}

#endif /* _String_H */
