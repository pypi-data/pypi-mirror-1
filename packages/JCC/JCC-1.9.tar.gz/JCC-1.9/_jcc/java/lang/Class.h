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

#ifndef _Class_H
#define _Class_H

#include <Python.h>
#include "JArray.h"
#include "java/lang/Object.h"

namespace java {
    namespace lang {
        namespace reflect {
            class Method;
            class Constructor;
            class Field;
        }

        using namespace reflect;

        class Class : public Object {
        public:
            static Class *class$;
            static jmethodID *_mids;
            static jclass initializeClass();

            explicit Class(jobject obj) : Object(obj) {
                initializeClass();
            }
            Class(const Class& obj) : Object(obj) {}

            static Class forName(const String& className);
            JArray<Method> getDeclaredMethods() const;
            JArray<Method> getMethods() const;
            Method getMethod(const String &name, const JArray<Class>& params) const;
            Method getDeclaredMethod(const String &name, const JArray<Class>& params) const;
            JArray<Constructor> getDeclaredConstructors() const;
            JArray<Field> getDeclaredFields() const;
            JArray<Class> getDeclaredClasses() const;
            int isArray() const;
            int isPrimitive() const;
            int isInterface() const;
            int isAssignableFrom(const Class& obj) const;
            Class getComponentType() const;
            Class getSuperclass() const;
            JArray<Class> getInterfaces() const;
            String getName() const;
            int getModifiers() const;
            int isInstance(const Object &obj) const;
        };

        extern PyTypeObject ClassType;

        class t_Class {
        public:
            PyObject_HEAD
            Class object;
            static PyObject *wrapObject(const Class& object);
        };
    }
}


#endif /* _Class_H */
