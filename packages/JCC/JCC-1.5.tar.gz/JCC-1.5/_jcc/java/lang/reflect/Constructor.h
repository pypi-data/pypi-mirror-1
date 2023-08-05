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

#ifndef _Constructor_H
#define _Constructor_H

#include <Python.h>
#include "JArray.h"

namespace java {
    namespace lang {
        class Class;
        class String;

        namespace reflect {
            class Constructor : public Object {
            public:
                static Class *class$;
                static jmethodID *_mids;
                static jclass initializeClass();

                explicit Constructor(jobject obj) : Object(obj) {
                    initializeClass();
                }
                Constructor(const Constructor& obj) : Object(obj) {}

                int getModifiers() const;
                JArray<Class> getParameterTypes() const;
                JArray<Class> getExceptionTypes() const;
            };


            extern PyTypeObject ConstructorType;

            class t_Constructor {
            public:
                PyObject_HEAD
                Constructor object;
                static PyObject *wrapObject(const Constructor& object);
            };
        }
    }
}

#endif /* _Constructor_H */
