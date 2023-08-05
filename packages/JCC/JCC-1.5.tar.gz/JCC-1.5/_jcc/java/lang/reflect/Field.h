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

#ifndef _Field_H
#define _Field_H

#include <Python.h>

namespace java {
    namespace lang {
        class Class;
        class String;

        namespace reflect {
            class Field : public Object {
            public:
                static Class *class$;
                static jmethodID *_mids;
                static jclass initializeClass();

                explicit Field(jobject obj) : Object(obj) {
                    initializeClass();
                }
                Field(const Field& obj) : Object(obj) {}

                int getModifiers() const;
                Class getType() const;
                String getName() const;
            };

            extern PyTypeObject FieldType;

            class t_Field {
            public:
                PyObject_HEAD
                Field object;
                static PyObject *wrapObject(const Field& object);
            };
        }
    }
}

#endif /* _Field_H */
