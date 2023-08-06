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

#ifndef _Object_H
#define _Object_H

#include <Python.h>
#include "JObject.h"

namespace java {
    namespace lang {
        class Class;
        class String;

        class Object : public JObject {
        public:
            static Class *class$;
            static jmethodID *mids$;
            static jclass initializeClass();

            explicit Object();
            explicit Object(jobject obj) : JObject(obj) {
                initializeClass();
            }

            String toString() const;
            Class getClass() const;
            int hashCode() const;
        };

        extern PyTypeObject ObjectType;

        class t_Object {
        public:
            PyObject_HEAD
            Object object;
            static PyObject *wrapObject(const Object& object);
        };
    }
}


#endif /* _Object_H */
