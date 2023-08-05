/* ====================================================================
 * Copyright (c) 2007-2008 Open Source Applications Foundation.
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

#include <map>
#include <jni.h>

#include "JCCEnv.h"

extern JCCEnv *env;

#ifdef PYTHON
#include "JObject.h"
#include "functions.h"
#include "macros.h"
#endif

#ifdef _MSC_VER
DWORD JCCEnv::VM_ENV = 0;
#else
pthread_key_t JCCEnv::VM_ENV = (pthread_key_t) NULL;
#endif

#ifdef _MSC_VER

static CRITICAL_SECTION *mutex = NULL;

class lock {
public:
    lock() {
        EnterCriticalSection(mutex);
    }
    virtual ~lock() {
        LeaveCriticalSection(mutex);
    }
};

#else

static pthread_mutex_t *mutex = NULL;

class lock {
public:
    lock() {
        pthread_mutex_lock(mutex);
    }
    virtual ~lock() {
        pthread_mutex_unlock(mutex);
    }
};

#endif

JCCEnv::JCCEnv(JavaVM *vm, JNIEnv *vm_env)
{
#ifdef _MSC_VER
    if (!mutex)
    {
        mutex = new CRITICAL_SECTION();
        InitializeCriticalSection(mutex);
    }
#else
    if (!mutex)
    {
        mutex = new pthread_mutex_t();
        pthread_mutex_init(mutex, NULL);
    }
#endif

    this->vm = vm;
    set_vm_env(vm_env);
    env = this;

    _sys = (jclass) vm_env->NewGlobalRef(vm_env->FindClass("java/lang/System"));
    _obj = (jclass) vm_env->NewGlobalRef(vm_env->FindClass("java/lang/Object"));
    _thr = (jclass) vm_env->NewGlobalRef(vm_env->FindClass("java/lang/RuntimeException"));
    _mids = new jmethodID[max_mid];

    _mids[mid_sys_identityHashCode] =
        vm_env->GetStaticMethodID(_sys, "identityHashCode",
                                  "(Ljava/lang/Object;)I");
    _mids[mid_sys_setProperty] =
        vm_env->GetStaticMethodID(_sys, "setProperty",
                                  "(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;");
    _mids[mid_obj_toString] =
        vm_env->GetMethodID(_obj, "toString",
                            "()Ljava/lang/String;");
    _mids[mid_obj_hashCode] =
        vm_env->GetMethodID(_obj, "hashCode",
                            "()I");
    _mids[mid_obj_getClass] =
        vm_env->GetMethodID(_obj, "getClass",
                            "()Ljava/lang/Class;");
    _mids[mid_thr_getMessage] =
        vm_env->GetMethodID(_thr, "getMessage",
                            "()Ljava/lang/String;");
}

#ifdef _MSC_VER

void JCCEnv::set_vm_env(JNIEnv *vm_env)
{
    if (!VM_ENV)
        VM_ENV = TlsAlloc();
    TlsSetValue(VM_ENV, (LPVOID) vm_env);
}

#else

void JCCEnv::set_vm_env(JNIEnv *vm_env)
{
    if (!VM_ENV)
        pthread_key_create(&VM_ENV, NULL);
    pthread_setspecific(VM_ENV, (void *) vm_env);
}

#endif

jclass JCCEnv::findClass(const char *className)
{
    jclass cls = NULL;

    if (env)
        cls = get_vm_env()->FindClass(className);

    reportException();

    return cls;
}

void JCCEnv::registerNatives(jclass cls, JNINativeMethod *methods, int n)
{
    get_vm_env()->RegisterNatives(cls, methods, n);
}

jobject JCCEnv::newGlobalRef(jobject obj, int id)
{
    if (obj)
    {
        if (id)  /* zero when weak global ref is desired */
        {
            lock locked;

            for (std::multimap<int, countedRef>::iterator iter = refs.find(id);
                 iter != refs.end();
                 iter++) {
                if (iter->first != id)
                    break;
                if (isSame(obj, iter->second.global))
                {
                    iter->second.count += 1;
                    return iter->second.global;
                }
            }

            countedRef ref;
            JNIEnv *vm_env = get_vm_env();

            ref.global = vm_env->NewGlobalRef(obj);
            ref.count = 1;
            refs.insert(std::pair<const int, countedRef>(id, ref));
            vm_env->DeleteLocalRef(obj);

            return ref.global;
        }
        else
            return get_vm_env()->NewWeakGlobalRef(obj);
    }

    return NULL;
}

jobject JCCEnv::deleteGlobalRef(jobject obj, int id)
{
    if (obj)
    {
        if (id)  /* zero when obj is weak global ref */
        {
            lock locked;

            for (std::multimap<int, countedRef>::iterator iter = refs.find(id);
                 iter != refs.end();
                 iter++) {
                if (iter->first != id)
                    break;
                if (isSame(obj, iter->second.global))
                {
                    if (iter->second.count == 1)
                    {
                        get_vm_env()->DeleteGlobalRef(iter->second.global);
                        refs.erase(iter);
                    }
                    else
                        iter->second.count -= 1;
                    return NULL;
                }
            }

            printf("deleting non-existent ref: 0x%x\n", id);
        }
        else
            get_vm_env()->DeleteWeakGlobalRef(obj);
    }

    return NULL;
}

jobject JCCEnv::newObject(jclass (*initializeClass)(), jmethodID **mids,
                          int m, ...)
{
    jclass cls;
    jobject obj;
    va_list ap;

    va_start(ap, m);
    cls = (*initializeClass)();
    obj = get_vm_env()->NewObjectV(cls, (*mids)[m], ap);
    va_end(ap);

    reportException();

    return obj;
}

jobjectArray JCCEnv::newObjectArray(jclass cls, int size)
{
    jobjectArray array = get_vm_env()->NewObjectArray(size, cls, NULL);

    reportException();
    return array;
}

void JCCEnv::setObjectArrayElement(jobjectArray array, int n, jobject obj)
{
    get_vm_env()->SetObjectArrayElement(array, n, obj);
    reportException();
}

jobject JCCEnv::getObjectArrayElement(jobjectArray array, int n)
{
    jobject obj = get_vm_env()->GetObjectArrayElement(array, n);

    reportException();
    return obj;
}

int JCCEnv::getArrayLength(jarray array)
{
    int len = get_vm_env()->GetArrayLength(array);

    reportException();
    return len;
}


void JCCEnv::reportException()
{
    JNIEnv *vm_env = get_vm_env();
    jthrowable throwable = vm_env->ExceptionOccurred();

    if (throwable)
    {
        //vm_env->ExceptionDescribe();
        vm_env->ExceptionClear();

#ifdef PYTHON
        /* kludge: if RuntimeException is thrown assume a Python error */
        jobject cls =
            vm_env->CallObjectMethod(throwable, _mids[mid_obj_getClass]);

        if (vm_env->IsSameObject(cls, _thr))
            throw pythonError(throwable);
#endif

        throw exception(throwable);
    }
}


#define DEFINE_CALL(jtype, Type)                                        \
    jtype JCCEnv::call##Type##Method(jobject obj,                       \
                                     jmethodID mid, ...)                \
    {                                                                   \
        va_list ap;                                                     \
        jtype result;                                                   \
                                                                        \
        va_start(ap, mid);                                              \
        result = get_vm_env()->Call##Type##MethodV(obj, mid, ap);       \
        va_end(ap);                                                     \
                                                                        \
        reportException();                                              \
                                                                        \
        return result;                                                  \
    }

#define DEFINE_NONVIRTUAL_CALL(jtype, Type)                             \
    jtype JCCEnv::callNonvirtual##Type##Method(jobject obj, jclass cls, \
                                               jmethodID mid, ...)      \
    {                                                                   \
        va_list ap;                                                     \
        jtype result;                                                   \
                                                                        \
        va_start(ap, mid);                                              \
        result = get_vm_env()->CallNonvirtual##Type##MethodV(obj, cls,  \
                                                             mid, ap);  \
        va_end(ap);                                                     \
                                                                        \
        reportException();                                              \
                                                                        \
        return result;                                                  \
    }

#define DEFINE_STATIC_CALL(jtype, Type)                                 \
    jtype JCCEnv::callStatic##Type##Method(jclass cls,                  \
                                           jmethodID mid, ...)          \
    {                                                                   \
        va_list ap;                                                     \
        jtype result;                                                   \
                                                                        \
        va_start(ap, mid);                                              \
        result = get_vm_env()->CallStatic##Type##MethodV(cls, mid, ap); \
        va_end(ap);                                                     \
                                                                        \
        reportException();                                              \
                                                                        \
        return result;                                                  \
    }
        
DEFINE_CALL(jobject, Object)
DEFINE_CALL(jboolean, Boolean)
DEFINE_CALL(jbyte, Byte)
DEFINE_CALL(jchar, Char)
DEFINE_CALL(jdouble, Double)
DEFINE_CALL(jfloat, Float)
DEFINE_CALL(jint, Int)
DEFINE_CALL(jlong, Long)
DEFINE_CALL(jshort, Short)

DEFINE_NONVIRTUAL_CALL(jobject, Object)
DEFINE_NONVIRTUAL_CALL(jboolean, Boolean)
DEFINE_NONVIRTUAL_CALL(jbyte, Byte)
DEFINE_NONVIRTUAL_CALL(jchar, Char)
DEFINE_NONVIRTUAL_CALL(jdouble, Double)
DEFINE_NONVIRTUAL_CALL(jfloat, Float)
DEFINE_NONVIRTUAL_CALL(jint, Int)
DEFINE_NONVIRTUAL_CALL(jlong, Long)
DEFINE_NONVIRTUAL_CALL(jshort, Short)

DEFINE_STATIC_CALL(jobject, Object)
DEFINE_STATIC_CALL(jboolean, Boolean)
DEFINE_STATIC_CALL(jbyte, Byte)
DEFINE_STATIC_CALL(jchar, Char)
DEFINE_STATIC_CALL(jdouble, Double)
DEFINE_STATIC_CALL(jfloat, Float)
DEFINE_STATIC_CALL(jint, Int)
DEFINE_STATIC_CALL(jlong, Long)
DEFINE_STATIC_CALL(jshort, Short)

void JCCEnv::callVoidMethod(jobject obj, jmethodID mid, ...)
{
    va_list ap;

    va_start(ap, mid);
    get_vm_env()->CallVoidMethodV(obj, mid, ap);
    va_end(ap);

    reportException();
}

void JCCEnv::callNonvirtualVoidMethod(jobject obj, jclass cls,
                                      jmethodID mid, ...)
{
    va_list ap;

    va_start(ap, mid);
    get_vm_env()->CallNonvirtualVoidMethodV(obj, cls, mid, ap);
    va_end(ap);

    reportException();
}

void JCCEnv::callStaticVoidMethod(jclass cls, jmethodID mid, ...)
{
    va_list ap;

    va_start(ap, mid);
    get_vm_env()->CallStaticVoidMethodV(cls, mid, ap);
    va_end(ap);

    reportException();
}


jmethodID JCCEnv::getMethodID(jclass cls, const char *name,
                              const char *signature)
{
    jmethodID id = get_vm_env()->GetMethodID(cls, name, signature);

    reportException();

    return id;
}

jfieldID JCCEnv::getFieldID(jclass cls, const char *name,
                            const char *signature)
{
    jfieldID id = get_vm_env()->GetFieldID(cls, name, signature);

    reportException();

    return id;
}


jmethodID JCCEnv::getStaticMethodID(jclass cls, const char *name,
                                    const char *signature)
{
    jmethodID id = get_vm_env()->GetStaticMethodID(cls, name, signature);

    reportException();

    return id;
}

jobject JCCEnv::getStaticObjectField(jclass cls, const char *name,
                                     const char *signature)
{
    JNIEnv *vm_env = get_vm_env();
    jfieldID id = vm_env->GetStaticFieldID(cls, name, signature);

    reportException();

    return vm_env->GetStaticObjectField(cls, id);
}

#define DEFINE_GET_STATIC_FIELD(jtype, Type, signature)                 \
    jtype JCCEnv::getStatic##Type##Field(jclass cls, const char *name)  \
    {                                                                   \
        JNIEnv *vm_env = get_vm_env();                                  \
        jfieldID id = vm_env->GetStaticFieldID(cls, name, #signature);  \
        reportException();                                              \
        return vm_env->GetStatic##Type##Field(cls, id);                 \
    }

DEFINE_GET_STATIC_FIELD(jboolean, Boolean, Z)
DEFINE_GET_STATIC_FIELD(jbyte, Byte, B)
DEFINE_GET_STATIC_FIELD(jchar, Char, C)
DEFINE_GET_STATIC_FIELD(jdouble, Double, D)
DEFINE_GET_STATIC_FIELD(jfloat, Float, F)
DEFINE_GET_STATIC_FIELD(jint, Int, I)
DEFINE_GET_STATIC_FIELD(jlong, Long, J)
DEFINE_GET_STATIC_FIELD(jshort, Short, S)

#define DEFINE_GET_FIELD(jtype, Type)                                   \
    jtype JCCEnv::get##Type##Field(jobject obj, jfieldID id)            \
    {                                                                   \
        jtype value = get_vm_env()->Get##Type##Field(obj, id);          \
        reportException();                                              \
        return value;                                                   \
    }

DEFINE_GET_FIELD(jobject, Object)
DEFINE_GET_FIELD(jboolean, Boolean)
DEFINE_GET_FIELD(jbyte, Byte)
DEFINE_GET_FIELD(jchar, Char)
DEFINE_GET_FIELD(jdouble, Double)
DEFINE_GET_FIELD(jfloat, Float)
DEFINE_GET_FIELD(jint, Int)
DEFINE_GET_FIELD(jlong, Long)
DEFINE_GET_FIELD(jshort, Short)

#define DEFINE_SET_FIELD(jtype, Type)                                    \
    void JCCEnv::set##Type##Field(jobject obj, jfieldID id, jtype value) \
    {                                                                    \
        get_vm_env()->Set##Type##Field(obj, id, value);                  \
        reportException();                                               \
    }

DEFINE_SET_FIELD(jobject, Object)
DEFINE_SET_FIELD(jboolean, Boolean)
DEFINE_SET_FIELD(jbyte, Byte)
DEFINE_SET_FIELD(jchar, Char)
DEFINE_SET_FIELD(jdouble, Double)
DEFINE_SET_FIELD(jfloat, Float)
DEFINE_SET_FIELD(jint, Int)
DEFINE_SET_FIELD(jlong, Long)
DEFINE_SET_FIELD(jshort, Short)

void JCCEnv::setClassPath(const char *classPath)
{
    JNIEnv *vm_env = get_vm_env();
    jstring key = vm_env->NewStringUTF("java.class.path");
    jstring cp = vm_env->NewStringUTF(classPath);

    vm_env->CallStaticObjectMethod(_sys, _mids[mid_sys_setProperty], key, cp);
}

jstring JCCEnv::fromUTF(const char *bytes)
{
    jstring str = get_vm_env()->NewStringUTF(bytes);

    reportException();

    return str;
}

char *JCCEnv::toUTF(jstring str)
{
    JNIEnv *vm_env = get_vm_env();
    int len = vm_env->GetStringUTFLength(str);
    char *bytes = new char[len + 1];
    jboolean isCopy = 0;
    const char *utf = vm_env->GetStringUTFChars(str, &isCopy);

    if (!bytes)
        return NULL;

    memcpy(bytes, utf, len);
    bytes[len] = '\0';

    vm_env->ReleaseStringUTFChars(str, utf);

    return bytes;
}

char *JCCEnv::toString(jobject obj)
{
    return obj
        ? toUTF((jstring) callObjectMethod(obj, _mids[mid_obj_toString]))
        : NULL;
}

char *JCCEnv::getClassName(jobject obj)
{
    return obj
        ? toString(callObjectMethod(obj, _mids[mid_obj_getClass]))
        : NULL;
}

#ifdef PYTHON

jstring JCCEnv::fromPyString(PyObject *object)
{
    if (object == Py_None)
        return NULL;
    else if (PyUnicode_Check(object))
    {
        if (sizeof(Py_UNICODE) == sizeof(jchar))
        {
            jchar *buf = (jchar *) PyUnicode_AS_UNICODE(object);
            jsize len = (jsize) PyUnicode_GET_SIZE(object);

            return get_vm_env()->NewString(buf, len);
        }
        else
        {
            jsize len = PyUnicode_GET_SIZE(object);
            Py_UNICODE *pchars = PyUnicode_AS_UNICODE(object);
            jchar *jchars = new jchar[len];
            jstring str;

            for (int i = 0; i < len; i++)
                jchars[i] = (jchar) pchars[i];

            str = get_vm_env()->NewString(jchars, len);
            delete jchars;

            return str;
        }
    }
    else if (PyString_Check(object))
        return fromUTF(PyString_AS_STRING(object));
    else
    {
        PyObject *tuple = Py_BuildValue("(sO)", "expected a string", object);

        PyErr_SetObject(PyExc_TypeError, tuple);
        Py_DECREF(tuple);

        return NULL;
    }
}

PyObject *JCCEnv::fromJString(jstring js)
{
    if (!js)
        Py_RETURN_NONE;

    JNIEnv *vm_env = get_vm_env();

    if (sizeof(Py_UNICODE) == sizeof(jchar))
    {
        jboolean isCopy;
        const jchar *buf = vm_env->GetStringChars(js, &isCopy);
        jsize len = vm_env->GetStringLength(js);
        PyObject *string = PyUnicode_FromUnicode((const Py_UNICODE *) buf, len);

        vm_env->ReleaseStringChars(js, buf);
        return string;
    }
    else
    {
        jsize len = vm_env->GetStringLength(js);
        PyObject *string = PyUnicode_FromUnicode(NULL, len);

        if (!string)
            return NULL;

        jboolean isCopy;
        const jchar *jchars = vm_env->GetStringChars(js, &isCopy);
        Py_UNICODE *pchars = PyUnicode_AS_UNICODE(string);

        for (int i = 0; i < len; i++)
            pchars[i] = (Py_UNICODE) jchars[i];
        
        vm_env->ReleaseStringChars(js, jchars);
        return string;
    }
}

extern PyObject *PyErr_SetJavaError(jthrowable throwable);

jobjectArray JCCEnv::fromPySequence(jclass cls, PyObject *sequence)
{
    if (sequence == Py_None)
        return NULL;

    if (!PySequence_Check(sequence))
    {
        PyErr_SetObject(PyExc_TypeError, sequence);
        return NULL;
    }

    int length = PySequence_Length(sequence);
    jobjectArray array;

    try {
        array = newObjectArray(cls, length);
    } catch (JCCEnv::pythonError) {
        return NULL;
    } catch (JCCEnv::exception e) {
        PyErr_SetJavaError(e.throwable);
        return NULL;
    }

    JNIEnv *vm_env = get_vm_env();

    for (int i = 0; i < length; i++) {
        PyObject *obj = PySequence_GetItem(sequence, i);
        int fromString = 0;
        jobject jobj;

        if (!obj)
            break;
        else if (obj == Py_None)
            jobj = NULL;
        else if (PyString_Check(obj) || PyUnicode_Check(obj))
        {
            jobj = fromPyString(obj);
            fromString = 1;
        }
        else if (PyObject_TypeCheck(obj, &JObjectType))
            jobj = ((t_JObject *) obj)->object.this$;
        else if (PyObject_TypeCheck(obj, &FinalizerProxyType))
            jobj = ((t_JObject *) ((t_fp *) obj)->object)->object.this$;
        else /* todo: add auto-boxing of primitive types */
        {
            PyErr_SetObject(PyExc_TypeError, obj);
            Py_DECREF(obj);
            return NULL;
        }

        Py_DECREF(obj);

        try {
            setObjectArrayElement(array, i, jobj);
            if (fromString)
                vm_env->DeleteLocalRef(jobj);
        } catch (JCCEnv::exception e) {
            PyErr_SetJavaError(e.throwable);
            return NULL;
        }
    }

    return array;
}

/* may be called from finalizer thread which has no vm_env thread local */
void JCCEnv::finalizeObject(JNIEnv *jenv, PyObject *obj)
{
    PythonGIL gil;

    set_vm_env(jenv);
    Py_DECREF(obj);
}

#endif /* PYTHON */
