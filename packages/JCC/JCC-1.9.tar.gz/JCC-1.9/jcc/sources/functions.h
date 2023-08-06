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

#ifndef _functions_h
#define _functions_h

#include "java/util/Iterator.h"
#include "java/util/Enumeration.h"
#include "java/lang/String.h"
#include "java/lang/Object.h"
#include "macros.h"

PyObject *PyErr_SetArgsError(char *name, PyObject *args);
PyObject *PyErr_SetArgsError(PyObject *self, char *name, PyObject *args);
PyObject *PyErr_SetArgsError(PyTypeObject *type, char *name, PyObject *args);
PyObject *PyErr_SetJavaError(jthrowable throwable);

extern PyObject *PyExc_JavaError;
extern PyObject *PyExc_InvalidArgsError;


void throwPythonError(void);
void throwTypeError(const char *name, PyObject *object);

#if defined(_MSC_VER) || defined(__SUNPRO_CC)

#define parseArgs __parseArgs
#define parseArg __parseArg

int __parseArgs(PyObject *args, char *types, ...);
int __parseArg(PyObject *arg, char *types, ...);

int _parseArgs(PyObject **args, unsigned int count, char *types,
	       va_list list, va_list check);

#else

#define parseArgs(args, types, rest...) \
    _parseArgs(((PyTupleObject *)(args))->ob_item, \
               ((PyTupleObject *)(args))->ob_size, types, ##rest)

#define parseArg(arg, types, rest...) \
    _parseArgs(&(arg), 1, types, ##rest)

int _parseArgs(PyObject **args, unsigned int count, char *types, ...);

#endif

int abstract_init(PyObject *self, PyObject *args, PyObject *kwds);

PyObject *j2p(const java::lang::String& js);
java::lang::String p2j(PyObject *object);

PyObject *make_descriptor(PyTypeObject *value);
PyObject *make_descriptor(jclass (*initializeClass)(void));
PyObject *make_descriptor(PyObject *value);
PyObject *make_descriptor(jboolean value);
PyObject *make_descriptor(jbyte value);
PyObject *make_descriptor(jchar value);
PyObject *make_descriptor(jdouble value);
PyObject *make_descriptor(jfloat value);
PyObject *make_descriptor(jint value);
PyObject *make_descriptor(jlong value);
PyObject *make_descriptor(jshort value);

jobjectArray make_array(jclass cls, PyObject *sequence);

PyObject *callSuper(PyTypeObject *type,
                    const char *name, PyObject *args, int cardinality);
PyObject *callSuper(PyTypeObject *type, PyObject *self,
                    const char *name, PyObject *args, int cardinality);

template<class T> PyObject *get_iterator(PyObject *self)
{
    java::util::Iterator iterator((jobject) NULL);

    OBJ_CALL(iterator = (((T *) self)->object.iterator()));
    return java::util::t_Iterator::wrapObject(iterator);
}

template<class U, class V> PyObject *get_iterator_next(PyObject *self)
{
    java::util::t_Iterator *iterator = (java::util::t_Iterator *) self;
    jboolean hasNext;

    OBJ_CALL(hasNext = iterator->object.hasNext());
    if (!hasNext)
    {
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }

    V next((jobject) NULL);
    OBJ_CALL(next = iterator->object.next());

    jclass cls = java::lang::String::initializeClass();
    if (env->get_vm_env()->IsInstanceOf(next.this$, cls))
        return env->fromJString((jstring) next.this$);

    return U::wrapObject(next);
}

template<class U, class V> PyObject *get_enumeration_nextElement(PyObject *self)
{
    java::util::t_Enumeration *enumeration = (java::util::t_Enumeration *) self;
    jboolean hasMoreElements;

    OBJ_CALL(hasMoreElements = enumeration->object.hasMoreElements());
    if (!hasMoreElements)
    {
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }

    V next((jobject) NULL);
    OBJ_CALL(next = enumeration->object.nextElement());

    jclass cls = java::lang::String::initializeClass();
    if (env->get_vm_env()->IsInstanceOf(next.this$, cls))
        return env->fromJString((jstring) next.this$);

    return U::wrapObject(next);
}

template<class T, class U, class V> PyObject *get_next(PyObject *self)
{
    T *iterator = (T *) self;
    V next((jobject) NULL);

    OBJ_CALL(next = iterator->object.next());
    if (!next)
    {
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }
        
    jclass cls = java::lang::String::initializeClass();
    if (env->get_vm_env()->IsInstanceOf(next.this$, cls))
        return env->fromJString((jstring) next.this$);

    return U::wrapObject(next);
}

PyObject *get_extension_iterator(PyObject *self);
PyObject *get_extension_next(PyObject *self);
PyObject *get_extension_nextElement(PyObject *self);

jobjectArray fromPySequence(jclass cls, PyObject *sequence);
PyObject *castCheck(PyObject *obj, jclass cls, int reportError);

extern PyTypeObject FinalizerClassType;
extern PyTypeObject FinalizerProxyType;

typedef struct {
    PyObject_HEAD
    PyObject *object;
} t_fp;

#endif /* _functions_h */
