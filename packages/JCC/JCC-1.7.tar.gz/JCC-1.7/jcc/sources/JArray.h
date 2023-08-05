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

#ifndef _JArray_H
#define _JArray_H

#ifdef PYTHON
#include <Python.h>
#include "macros.h"
#endif

#include "JCCEnv.h"
#include "java/lang/Object.h"

template<class T> class JArray : public java::lang::Object {
public:
    int length;

    explicit JArray<T>(jobject obj) : java::lang::Object(obj) {
        length = this$ ? env->getArrayLength((jobjectArray) this$) : 0;
    }
    JArray<T>(const JArray<T>& obj) : java::lang::Object(obj) {
        length = obj.length;
    }

#ifdef PYTHON
    JArray<T>(PyObject *sequence) : java::lang::Object(env->fromPySequence(T::initializeClass(), sequence)) {
        length = this$ ? env->getArrayLength((jobjectArray) this$) : 0;
    }

    JArray<T>(jclass cls, PyObject *sequence) : java::lang::Object(env->fromPySequence(cls, sequence)) {
        length = this$ ? env->getArrayLength((jobjectArray) this$) : 0;
    }

    PyObject *toSequence(PyObject *(*wrapfn)(const T&))
    {
        if (this$ == NULL)
            Py_RETURN_NONE;

        PyObject *list = PyList_New(length);

        for (int i = 0; i < length; i++)
            PyList_SET_ITEM(list, i, (*wrapfn)((*this)[i]));

        return list;
    }
#endif

    T operator[](int n) {
        return T(env->getObjectArrayElement((jobjectArray) this$, n));
    }
};

template<> class JArray<jboolean> : public java::lang::Object {
  public:
    int length;

    class arrayElements {
    private:
        jboolean isCopy;
        jbooleanArray array;
        jboolean *elts;
    public:
        arrayElements(jbooleanArray array) {
            this->array = array;
            elts = env->get_vm_env()->GetBooleanArrayElements(array, &isCopy);
        }
        virtual ~arrayElements() {
            env->get_vm_env()->ReleaseBooleanArrayElements(array, elts, isCopy);
        }
        operator jboolean *() {
            return elts;
        }
    };

    arrayElements elements() {
        return arrayElements((jbooleanArray) this$);
    }

    JArray<jboolean>(jobject obj) : java::lang::Object(obj) {
        length = this$ ? env->getArrayLength((jarray) this$) : 0;
    }

    JArray<jboolean>(const JArray& obj) : java::lang::Object(obj) {
        length = obj.length;
    }

#ifdef PYTHON
    JArray<jboolean>(PyObject *sequence) : java::lang::Object(env->get_vm_env()->NewBooleanArray(PySequence_Length(sequence))) {
        length = env->getArrayLength((jarray) this$);
        arrayElements elts = elements();
        jboolean *buf = (jboolean *) elts;

        for (int i = 0; i < length; i++) {
            PyObject *obj = PySequence_GetItem(sequence, i);

            if (!obj)
                break;
            else if (obj == Py_True || obj == Py_False)
                buf[i] = (jboolean) (obj == Py_True);
            else
            {
                PyErr_SetObject(PyExc_TypeError, obj);
                Py_DECREF(obj);
                break;
            }

            Py_DECREF(obj);
        }
    }

    PyObject *toSequence()
    {
        if (this$ == NULL)
            Py_RETURN_NONE;

        PyObject *list = PyList_New(length);
        arrayElements elts = elements();
        jboolean *buf = (jboolean *) elts;

        for (int i = 0; i < length; i++) {
            jboolean value = buf[i];
            PyObject *obj = value ? Py_True : Py_False;

            Py_INCREF(obj);
            PyList_SET_ITEM(list, i, obj);
        }

        return list;
    }
#endif

    jboolean operator[](int n) {
        JNIEnv *vm_env = env->get_vm_env();
        jboolean isCopy = 0;
        jboolean *elts = (jboolean *)
            vm_env->GetPrimitiveArrayCritical((jarray) this$, &isCopy);
        jboolean value = elts[n];

        vm_env->ReleasePrimitiveArrayCritical((jarray) this$, elts, isCopy);

        return value;
    }
};

template<> class JArray<jbyte> : public java::lang::Object {
  public:
    int length;

    class arrayElements {
    private:
        jboolean isCopy;
        jbyteArray array;
        jbyte *elts;
    public:
        arrayElements(jbyteArray array) {
            this->array = array;
            elts = env->get_vm_env()->GetByteArrayElements(array, &isCopy);
        }
        virtual ~arrayElements() {
            env->get_vm_env()->ReleaseByteArrayElements(array, elts, isCopy);
        }
        operator jbyte *() {
            return elts;
        }
    };

    arrayElements elements() {
        return arrayElements((jbyteArray) this$);
    }

    JArray<jbyte>(jobject obj) : java::lang::Object(obj) {
        length = this$ ? env->getArrayLength((jarray) this$) : 0;
    }

    JArray<jbyte>(const JArray& obj) : java::lang::Object(obj) {
        length = obj.length;
    }

#ifdef PYTHON
    JArray<jbyte>(PyObject *sequence) : java::lang::Object(env->get_vm_env()->NewByteArray(PySequence_Length(sequence))) {
        length = env->getArrayLength((jarray) this$);
        arrayElements elts = elements();
        jbyte *buf = (jbyte *) elts;

        if (PyString_Check(sequence))
            memcpy(buf, PyString_AS_STRING(sequence), length);
        else
            for (int i = 0; i < length; i++) {
                PyObject *obj = PySequence_GetItem(sequence, i);

                if (!obj)
                    break;
                else if (PyString_Check(obj) && (PyString_GET_SIZE(obj) == 1))
                    buf[i] = (jbyte) PyString_AS_STRING(obj)[0];
                else
                {
                    PyErr_SetObject(PyExc_TypeError, obj);
                    Py_DECREF(obj);
                    break;
                }

                Py_DECREF(obj);
            }
    }

    PyObject *toSequence()
    {
        if (this$ == NULL)
            Py_RETURN_NONE;

        arrayElements elts = elements();
        jbyte *buf = (jbyte *) elts;

        return PyString_FromStringAndSize((char *) buf, length);
    }
#endif

    jbyte operator[](int n) {
        JNIEnv *vm_env = env->get_vm_env();
        jboolean isCopy = 0;
        jbyte *elts = (jbyte *)
            vm_env->GetPrimitiveArrayCritical((jarray) this$, &isCopy);
        jbyte value = elts[n];

        vm_env->ReleasePrimitiveArrayCritical((jarray) this$, elts, isCopy);

        return value;
    }
};

template<> class JArray<jchar> : public java::lang::Object {
  public:
    int length;

    class arrayElements {
    private:
        jboolean isCopy;
        jcharArray array;
        jchar *elts;
    public:
        arrayElements(jcharArray array) {
            this->array = array;
            elts = env->get_vm_env()->GetCharArrayElements(array, &isCopy);
        }
        virtual ~arrayElements() {
            env->get_vm_env()->ReleaseCharArrayElements(array, elts, isCopy);
        }
        operator jchar *() {
            return elts;
        }
    };

    arrayElements elements() {
        return arrayElements((jcharArray) this$);
    }

    JArray<jchar>(jobject obj) : java::lang::Object(obj) {
        length = this$ ? env->getArrayLength((jarray) this$) : 0;
    }

    JArray<jchar>(const JArray& obj) : java::lang::Object(obj) {
        length = obj.length;
    }

#ifdef PYTHON
    JArray<jchar>(PyObject *sequence) : java::lang::Object(env->get_vm_env()->NewCharArray(PySequence_Length(sequence))) {
        length = env->getArrayLength((jarray) this$);
        arrayElements elts = elements();
        jchar *buf = (jchar *) elts;

        if (PyUnicode_Check(sequence))
        {
            if (sizeof(Py_UNICODE) == sizeof(jchar))
                memcpy(buf, PyUnicode_AS_UNICODE(sequence),
                       length * sizeof(jchar));
            else
            {
                Py_UNICODE *pchars = PyUnicode_AS_UNICODE(sequence);
                for (int i = 0; i < length; i++)
                    buf[i] = (jchar) pchars[i];
            }
        }
        else
            for (int i = 0; i < length; i++) {
                PyObject *obj = PySequence_GetItem(sequence, i);

                if (!obj)
                    break;
                else if (PyUnicode_Check(obj) && (PyUnicode_GET_SIZE(obj) == 1))
                    buf[i] = (jchar) PyUnicode_AS_UNICODE(obj)[0];
                else
                {
                    PyErr_SetObject(PyExc_TypeError, obj);
                    Py_DECREF(obj);
                    break;
                }

                Py_DECREF(obj);
            }
    }

    PyObject *toSequence()
    {
        if (this$ == NULL)
            Py_RETURN_NONE;

        arrayElements elts = elements();
        jchar *buf = (jchar *) elts;

        if (sizeof(Py_UNICODE) == sizeof(jchar))
            return PyUnicode_FromUnicode((const Py_UNICODE *) buf, length);
        else
        {
            PyObject *string = PyUnicode_FromUnicode(NULL, length);
            Py_UNICODE *pchars = PyUnicode_AS_UNICODE(string);

            for (int i = 0; i < length; i++)
                pchars[i] = (Py_UNICODE) buf[i];

            return string;
        }
    }
#endif

    jchar operator[](int n) {
        JNIEnv *vm_env = env->get_vm_env();
        jboolean isCopy = 0;
        jchar *elts = (jchar *)
            vm_env->GetPrimitiveArrayCritical((jarray) this$, &isCopy);
        jchar value = elts[n];

        vm_env->ReleasePrimitiveArrayCritical((jarray) this$, elts, isCopy);

        return value;
    }
};

template<> class JArray<jdouble> : public java::lang::Object {
  public:
    int length;

    class arrayElements {
    private:
        jboolean isCopy;
        jdoubleArray array;
        jdouble *elts;
    public:
        arrayElements(jdoubleArray array) {
            this->array = array;
            elts = env->get_vm_env()->GetDoubleArrayElements(array, &isCopy);
        }
        virtual ~arrayElements() {
            env->get_vm_env()->ReleaseDoubleArrayElements(array, elts, isCopy);
        }
        operator jdouble *() {
            return elts;
        }
    };

    arrayElements elements() {
        return arrayElements((jdoubleArray) this$);
    }

    JArray<jdouble>(jobject obj) : java::lang::Object(obj) {
        length = this$ ? env->getArrayLength((jarray) this$) : 0;
    }

    JArray<jdouble>(const JArray& obj) : java::lang::Object(obj) {
        length = obj.length;
    }

#ifdef PYTHON
    JArray<jdouble>(PyObject *sequence) : java::lang::Object(env->get_vm_env()->NewDoubleArray(PySequence_Length(sequence))) {
        length = env->getArrayLength((jarray) this$);
        arrayElements elts = elements();
        jdouble *buf = (jdouble *) elts;

        for (int i = 0; i < length; i++) {
            PyObject *obj = PySequence_GetItem(sequence, i);

            if (!obj)
                break;
            else if (PyFloat_Check(obj))
                buf[i] = (jdouble) PyFloat_AS_DOUBLE(obj);
            else
            {
                PyErr_SetObject(PyExc_TypeError, obj);
                Py_DECREF(obj);
                break;
            }

            Py_DECREF(obj);
        }
    }

    PyObject *toSequence()
    {
        if (this$ == NULL)
            Py_RETURN_NONE;

        PyObject *list = PyList_New(length);
        arrayElements elts = elements();
        jdouble *buf = (jdouble *) elts;

        for (int i = 0; i < length; i++)
            PyList_SET_ITEM(list, i, PyFloat_FromDouble((double) buf[i]));

        return list;
    }
#endif

    jdouble operator[](int n) {
        JNIEnv *vm_env = env->get_vm_env();
        jboolean isCopy = 0;
        jdouble *elts = (jdouble *)
            vm_env->GetPrimitiveArrayCritical((jarray) this$, &isCopy);
        jdouble value = elts[n];

        vm_env->ReleasePrimitiveArrayCritical((jarray) this$, elts, isCopy);

        return value;
    }
};

template<> class JArray<jfloat> : public java::lang::Object {
  public:
    int length;

    class arrayElements {
    private:
        jboolean isCopy;
        jfloatArray array;
        jfloat *elts;
    public:
        arrayElements(jfloatArray array) {
            this->array = array;
            elts = env->get_vm_env()->GetFloatArrayElements(array, &isCopy);
        }
        virtual ~arrayElements() {
            env->get_vm_env()->ReleaseFloatArrayElements(array, elts, isCopy);
        }
        operator jfloat *() {
            return elts;
        }
    };

    arrayElements elements() {
        return arrayElements((jfloatArray) this$);
    }

    JArray<jfloat>(jobject obj) : java::lang::Object(obj) {
        length = this$ ? env->getArrayLength((jarray) this$) : 0;
    }

    JArray<jfloat>(const JArray& obj) : java::lang::Object(obj) {
        length = obj.length;
    }

#ifdef PYTHON
    JArray<jfloat>(PyObject *sequence) : java::lang::Object(env->get_vm_env()->NewFloatArray(PySequence_Length(sequence))) {
        length = env->getArrayLength((jarray) this$);
        arrayElements elts = elements();
        jfloat *buf = (jfloat *) elts;

        for (int i = 0; i < length; i++) {
            PyObject *obj = PySequence_GetItem(sequence, i);

            if (!obj)
                break;
            else if (PyFloat_Check(obj))
                buf[i] = (jfloat) PyFloat_AS_DOUBLE(obj);
            else
            {
                PyErr_SetObject(PyExc_TypeError, obj);
                Py_DECREF(obj);
                break;
            }

            Py_DECREF(obj);
        }
    }

    PyObject *toSequence()
    {
        if (this$ == NULL)
            Py_RETURN_NONE;

        PyObject *list = PyList_New(length);
        arrayElements elts = elements();
        jfloat *buf = (jfloat *) elts;

        for (int i = 0; i < length; i++)
            PyList_SET_ITEM(list, i, PyFloat_FromDouble((double) buf[i]));

        return list;
    }
#endif

    jfloat operator[](int n) {
        JNIEnv *vm_env = env->get_vm_env();
        jboolean isCopy = 0;
        jfloat *elts = (jfloat *)
            vm_env->GetPrimitiveArrayCritical((jarray) this$, &isCopy);
        jfloat value = elts[n];

        vm_env->ReleasePrimitiveArrayCritical((jarray) this$, elts, isCopy);

        return value;
    }
};

template<> class JArray<jint> : public java::lang::Object {
  public:
    int length;

    class arrayElements {
    private:
        jboolean isCopy;
        jintArray array;
        jint *elts;
    public:
        arrayElements(jintArray array) {
            this->array = array;
            elts = env->get_vm_env()->GetIntArrayElements(array, &isCopy);
        }
        virtual ~arrayElements() {
            env->get_vm_env()->ReleaseIntArrayElements(array, elts, isCopy);
        }
        operator jint *() {
            return elts;
        }
    };

    arrayElements elements() {
        return arrayElements((jintArray) this$);
    }

    JArray<jint>(jobject obj) : java::lang::Object(obj) {
        length = this$ ? env->getArrayLength((jarray) this$) : 0;
    }

    JArray<jint>(const JArray& obj) : java::lang::Object(obj) {
        length = obj.length;
    }

#ifdef PYTHON
    JArray<jint>(PyObject *sequence) : java::lang::Object(env->get_vm_env()->NewIntArray(PySequence_Length(sequence))) {
        length = env->getArrayLength((jarray) this$);
        arrayElements elts = elements();
        jint *buf = (jint *) elts;

        for (int i = 0; i < length; i++) {
            PyObject *obj = PySequence_GetItem(sequence, i);

            if (!obj)
                break;
            else if (PyInt_Check(obj))
                buf[i] = (jint) PyInt_AS_LONG(obj);
            else
            {
                PyErr_SetObject(PyExc_TypeError, obj);
                Py_DECREF(obj);
                break;
            }

            Py_DECREF(obj);
        }
    }

    PyObject *toSequence()
    {
        if (this$ == NULL)
            Py_RETURN_NONE;

        PyObject *list = PyList_New(length);
        arrayElements elts = elements();
        jint *buf = (jint *) elts;

        for (int i = 0; i < length; i++)
            PyList_SET_ITEM(list, i, PyInt_FromLong(buf[i]));

        return list;
    }
#endif

    jint operator[](int n) {
        JNIEnv *vm_env = env->get_vm_env();
        jboolean isCopy = 0;
        jint *elts = (jint *)
            vm_env->GetPrimitiveArrayCritical((jarray) this$, &isCopy);
        jint value = elts[n];

        vm_env->ReleasePrimitiveArrayCritical((jarray) this$, elts, isCopy);

        return value;
    }
};

template<> class JArray<jlong> : public java::lang::Object {
  public:
    int length;

    class arrayElements {
    private:
        jboolean isCopy;
        jlongArray array;
        jlong *elts;
    public:
        arrayElements(jlongArray array) {
            this->array = array;
            elts = env->get_vm_env()->GetLongArrayElements(array, &isCopy);
        }
        virtual ~arrayElements() {
            env->get_vm_env()->ReleaseLongArrayElements(array, elts, isCopy);
        }
        operator jlong *() {
            return elts;
        }
    };

    arrayElements elements() {
        return arrayElements((jlongArray) this$);
    }

    JArray<jlong>(jobject obj) : java::lang::Object(obj) {
        length = this$ ? env->getArrayLength((jarray) this$) : 0;
    }

    JArray<jlong>(const JArray& obj) : java::lang::Object(obj) {
        length = obj.length;
    }

#ifdef PYTHON
    JArray<jlong>(PyObject *sequence) : java::lang::Object(env->get_vm_env()->NewLongArray(PySequence_Length(sequence))) {
        length = env->getArrayLength((jarray) this$);
        arrayElements elts = elements();
        jlong *buf = (jlong *) elts;

        for (int i = 0; i < length; i++) {
            PyObject *obj = PySequence_GetItem(sequence, i);

            if (!obj)
                break;
            else if (PyLong_Check(obj))
                buf[i] = (jlong) PyLong_AsLongLong(obj);
            else
            {
                PyErr_SetObject(PyExc_TypeError, obj);
                Py_DECREF(obj);
                break;
            }

            Py_DECREF(obj);
        }
    }

    PyObject *toSequence()
    {
        if (this$ == NULL)
            Py_RETURN_NONE;

        PyObject *list = PyList_New(length);
        arrayElements elts = elements();
        jlong *buf = (jlong *) elts;

        for (int i = 0; i < length; i++)
            PyList_SET_ITEM(list, i, PyLong_FromLongLong((long long) buf[i]));

        return list;
    }
#endif

    jlong operator[](long n) {
        JNIEnv *vm_env = env->get_vm_env();
        jboolean isCopy = 0;
        jlong *elts = (jlong *)
            vm_env->GetPrimitiveArrayCritical((jarray) this$, &isCopy);
        jlong value = elts[n];

        vm_env->ReleasePrimitiveArrayCritical((jarray) this$, elts, isCopy);

        return value;
    }
};

template<> class JArray<jshort> : public java::lang::Object {
  public:
    int length;

    class arrayElements {
    private:
        jboolean isCopy;
        jshortArray array;
        jshort *elts;
    public:
        arrayElements(jshortArray array) {
            this->array = array;
            elts = env->get_vm_env()->GetShortArrayElements(array, &isCopy);
        }
        virtual ~arrayElements() {
            env->get_vm_env()->ReleaseShortArrayElements(array, elts, isCopy);
        }
        operator jshort *() {
            return elts;
        }
    };

    arrayElements elements() {
        return arrayElements((jshortArray) this$);
    }

    JArray<jshort>(jobject obj) : java::lang::Object(obj) {
        length = this$ ? env->getArrayLength((jarray) this$) : 0;
    }

    JArray<jshort>(const JArray& obj) : java::lang::Object(obj) {
        length = obj.length;
    }

#ifdef PYTHON
    JArray<jshort>(PyObject *sequence) : java::lang::Object(env->get_vm_env()->NewShortArray(PySequence_Length(sequence))) {
        length = env->getArrayLength((jarray) this$);
        arrayElements elts = elements();
        jshort *buf = (jshort *) elts;

        for (int i = 0; i < length; i++) {
            PyObject *obj = PySequence_GetItem(sequence, i);

            if (!obj)
                break;
            else if (PyInt_Check(obj))
                buf[i] = (jshort) PyInt_AS_LONG(obj);
            else
            {
                PyErr_SetObject(PyExc_TypeError, obj);
                Py_DECREF(obj);
                break;
            }

            Py_DECREF(obj);
        }
    }

    PyObject *toSequence()
    {
        if (this$ == NULL)
            Py_RETURN_NONE;

        PyObject *list = PyList_New(length);
        arrayElements elts = elements();
        jshort *buf = (jshort *) elts;

        for (int i = 0; i < length; i++)
            PyList_SET_ITEM(list, i, PyInt_FromLong(buf[i]));

        return list;
    }
#endif

    jshort operator[](int n) {
        JNIEnv *vm_env = env->get_vm_env();
        jboolean isCopy = 0;
        jshort *elts = (jshort *)
            vm_env->GetPrimitiveArrayCritical((jarray) this$, &isCopy);
        jshort value = elts[n];

        vm_env->ReleasePrimitiveArrayCritical((jarray) this$, elts, isCopy);

        return value;
    }
};

#endif /* _JArray_H */
