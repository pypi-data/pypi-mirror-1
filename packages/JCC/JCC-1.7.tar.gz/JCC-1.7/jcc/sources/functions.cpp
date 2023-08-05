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

#include <jni.h>
#include <stdarg.h>

#include "java/lang/Object.h"
#include "java/lang/Class.h"
#include "java/lang/String.h"
#include "java/lang/Throwable.h"
#include "java/lang/Boolean.h"
#include "java/lang/Integer.h"
#include "java/lang/Long.h"
#include "java/lang/Double.h"
#include "java/lang/RuntimeException.h"
#include "java/util/Iterator.h"
#include "JArray.h"
#include "functions.h"
#include "macros.h"

using namespace java::lang;
using namespace java::util;

PyObject *PyExc_JavaError = PyExc_ValueError;
PyObject *PyExc_InvalidArgsError = PyExc_ValueError;

#if defined(_MSC_VER) || defined(__SUNPRO_CC)
int __parseArgs(PyObject *args, char *types, ...)
{
    int count = ((PyTupleObject *)(args))->ob_size;
    va_list list, check;

    va_start(list, types);
    va_start(check, types);

    return _parseArgs(((PyTupleObject *)(args))->ob_item, count, types,
		      list, check);
}

int __parseArg(PyObject *arg, char *types, ...)
{
    va_list list, check;

    va_start(list, types);
    va_start(check, types);

    return _parseArgs(&arg, 1, types, list, check);
}

int _parseArgs(PyObject **args, unsigned int count, char *types,
	       va_list list, va_list check)
{
    unsigned int typeCount = strlen(types);

    if (count > typeCount)
        return -1;
#else

int _parseArgs(PyObject **args, unsigned int count, char *types, ...)
{
    unsigned int typeCount = strlen(types);
    va_list list, check;

    if (count > typeCount)
        return -1;

    va_start(list, types);
    va_start(check, types);
#endif

    unsigned int pos = 0;
    int array = 0;

    for (unsigned int a = 0; a < count; a++, pos++) {
        PyObject *arg = args[a];

        switch (types[pos]) {
          case '[':
          {
              if (++array > 1)
                  return -1;

              a -= 1;
              break;
          }

          case 'j':           /* Java object */
          {
              Class *cls = va_arg(list, Class *);
              
              if (arg == Py_None)
                  break;

              if (array)
              {
                  if (PySequence_Check(arg) &&
                      !PyString_Check(arg) && !PyUnicode_Check(arg))
                  {
                      if (PySequence_Length(arg) > 0)
                      {
                          PyObject *obj = PySequence_GetItem(arg, 0);
                          int ok =
                              (obj == Py_None ||
                               PyObject_TypeCheck(obj, &ObjectType) &&
                               cls->isInstance(((t_Object *) obj)->object));

                          Py_DECREF(obj);
                          if (ok)
                              break;
                      }
                      else
                          break;
                  }
              }
              else if (PyObject_TypeCheck(arg, &ObjectType) &&
                       cls->isInstance(((t_Object *) arg)->object))
                  break;
              else if (PyObject_TypeCheck(arg, &FinalizerProxyType))
              {
                  arg = ((t_fp *) arg)->object;
                  if (PyObject_TypeCheck(arg, &ObjectType) &&
                      cls->isInstance(((t_Object *) arg)->object))
                      break;
              }

              return -1;
          }

          case 'Z':           /* boolean, strict */
          {
              if (arg == Py_True || arg == Py_False)
                  break;
              return -1;
          }

          case 'B':           /* byte */
          {
              if (array)
              {
                  if (arg == Py_None || PyString_Check(arg))
                      break;
              }
              else if (PyString_Check(arg) && (PyString_Size(arg) == 1))
                  break;
              return -1;
          }

          case 'C':           /* char */
          {
              if (array)
              {
                  if (arg == Py_None || PyString_Check(arg) ||
                      PyUnicode_Check(arg))
                      break;
              }
              else if (PyUnicode_Check(arg) && PyUnicode_GET_SIZE(arg) == 1)
                  break;
              return -1;
          }

          case 'I':           /* int */
          case 'S':           /* short */
          {
              if (array)
              {
                  if (PySequence_Check(arg))
                  {
                      if (PySequence_Length(arg) > 0)
                      {
                          PyObject *obj = PySequence_GetItem(arg, 0);
                          int ok = PyInt_CheckExact(obj);

                          Py_DECREF(obj);
                          if (ok)
                              break;
                      }
                      else
                          break;
                  }
              }
              else if (PyInt_CheckExact(arg))
                  break;
              return -1;
          }

          case 'D':           /* double */
          case 'F':           /* float */
          {
              if (array)
              {
                  if (PySequence_Check(arg))
                  {
                      if (PySequence_Length(arg) > 0)
                      {
                          PyObject *obj = PySequence_GetItem(arg, 0);
                          int ok = PyFloat_CheckExact(obj);

                          Py_DECREF(obj);
                          if (ok)
                              break;
                      }
                      else
                          break;
                  }
              }
              else if (PyFloat_CheckExact(arg))
                  break;
              return -1;
          }

          case 'J':           /* long long */
          {
              if (array)
              {
                  if (PySequence_Check(arg))
                  {
                      if (PySequence_Length(arg) > 0)
                      {
                          PyObject *obj = PySequence_GetItem(arg, 0);
                          int ok = PyLong_CheckExact(obj);

                          Py_DECREF(obj);
                          if (ok)
                              break;
                      }
                      else
                          break;
                  }
              }
              else if (PyLong_CheckExact(arg))
                  break;
              return -1;
          }

          case 's':           /* string  */
          {
              if (array)
              {
                  if (arg == Py_None)
                      break;
                  if (PySequence_Check(arg) && 
                      !PyString_Check(arg) && !PyUnicode_Check(arg))
                  {
                      if (PySequence_Length(arg) > 0)
                      {
                          PyObject *obj = PySequence_GetItem(arg, 0);
                          int ok =
                              (obj == Py_None ||
                               PyString_Check(obj) || PyUnicode_Check(obj));

                          Py_DECREF(obj);
                          if (ok)
                              break;
                      }
                      else
                          break;
                  }
              }
              else if (arg == Py_None ||
                       PyString_Check(arg) || PyUnicode_Check(arg))
                  break;
              return -1;
          }

          case 'o':         /* java.lang.Object */
            break;

          default:
            return -1;
        }

        if (types[pos] != '[')
            array = 0;
    }

    if (array)
        return -1;

    pos = 0;

    for (unsigned int a = 0; a < count; a++, pos++) {
        PyObject *arg = args[a];
        
        switch (types[pos]) {
          case '[':
          {
              if (++array > 1)
                  return -1;

              a -= 1;
              break;
          }

          case 'j':           /* Java object except String and Object */
          {
              Class *cls = va_arg(check, Class *);

              if (array)
              {
                  JArray<Object> *array = va_arg(list, JArray<Object> *);

                  if (arg == Py_None)
                      *array = JArray<Object>((jobject) NULL);
                  else 
                      *array = JArray<Object>((jclass) cls->this$, arg);

                  if (PyErr_Occurred())
                      return -1;
              }
              else
              {
                  Object *obj = va_arg(list, Object *);

                  if (PyObject_TypeCheck(arg, &FinalizerProxyType))
                      arg = ((t_fp *) arg)->object;

                  *obj = arg == Py_None
                      ? Object(NULL)
                      : ((t_Object *) arg)->object;
              }
              break;
          }

          case 'B':           /* byte */
          {
              if (array)
              {
                  JArray<jbyte> *array = va_arg(list, JArray<jbyte> *);

                  if (arg == Py_None)
                      *array = JArray<jbyte>((jobject) NULL);
                  else 
                      *array = JArray<jbyte>(arg);

                  if (PyErr_Occurred())
                      return -1;
              }
              else
              {
                  jbyte *a = va_arg(list, jbyte *);
                  *a = (jbyte) PyString_AS_STRING(arg)[0];
              }
              break;
          }

          case 'Z':           /* boolean, strict */
          {
              if (array)
              {
                  JArray<jboolean> *array = va_arg(list, JArray<jboolean> *);

                  if (arg == Py_None)
                      *array = JArray<jboolean>((jobject) NULL);
                  else 
                      *array = JArray<jboolean>(arg);

                  if (PyErr_Occurred())
                      return -1;
              }
              else
              {
                  jboolean *b = va_arg(list, jboolean *);
                  *b = arg == Py_True;
              }
              break;
          }

          case 'C':           /* char */
          {
              if (array)
              {
                  JArray<jchar> *array = va_arg(list, JArray<jchar> *);

                  if (arg == Py_None)
                      *array = JArray<jchar>((jobject) NULL);
                  else 
                      *array = JArray<jchar>(arg);

                  if (PyErr_Occurred())
                      return -1;
              }
              else
              {
                  jchar *c = va_arg(list, jchar *);
                  *c = (jchar) PyUnicode_AS_UNICODE(arg)[0];
              }
              break;
          }

          case 'I':           /* int */
          {
              if (array)
              {
                  JArray<jint> *array = va_arg(list, JArray<jint> *);

                  if (arg == Py_None)
                      *array = JArray<jint>((jobject) NULL);
                  else 
                      *array = JArray<jint>(arg);

                  if (PyErr_Occurred())
                      return -1;
              }
              else
              {
                  jint *n = va_arg(list, jint *);
                  *n = (jint) PyInt_AsLong(arg);
              }
              break;
          }

          case 'S':           /* short */
          {
              if (array)
              {
                  JArray<jshort> *array = va_arg(list, JArray<jshort> *);

                  if (arg == Py_None)
                      *array = JArray<jshort>((jobject) NULL);
                  else 
                      *array = JArray<jshort>(arg);

                  if (PyErr_Occurred())
                      return -1;
              }
              else
              {
                  jshort *n = va_arg(list, jshort *);
                  *n = (jshort) PyInt_AsLong(arg);
              }
              break;
          }

          case 'D':           /* double */
          {
              jdouble *d = va_arg(list, jdouble *);
              *d = (jdouble) PyFloat_AsDouble(arg);
              break;
          }

          case 'F':           /* float */
          {
              jfloat *d = va_arg(list, jfloat *);
              *d = (jfloat) (float) PyFloat_AsDouble(arg);
              break;
          }

          case 'J':           /* long long */
          {
              jlong *l = va_arg(list, jlong *);
              *l = (jlong) PyLong_AsLongLong(arg);
              break;
          }

          case 's':           /* string  */
          {
              if (array)
              {
                  JArray<String> *array = va_arg(list, JArray<String> *);

                  if (arg == Py_None)
                      *array = JArray<String>((jobject) NULL);
                  else 
                      *array = JArray<String>(arg);

                  if (PyErr_Occurred())
                      return -1;
              }
              else
              {
                  String *str = va_arg(list, String *);

                  if (arg == Py_None)
                      *str = String(NULL);
                  else
                  {
                      *str = p2j(arg);
                      if (PyErr_Occurred())
                          return -1;
                  }
              }
              break;
          }

          case 'o':           /* java.lang.Object  */
          {
              if (array)
              {
                  JArray<Object> *array = va_arg(list, JArray<Object> *);

                  if (arg == Py_None)
                      *array = JArray<Object>((jobject) NULL);
                  else 
                      *array = JArray<Object>(arg);

                  if (PyErr_Occurred())
                      return -1;
              }
              else
              {
                  Object *obj = va_arg(list, Object *);

                  if (arg == Py_None)
                      *obj = Object(NULL);
                  else if (PyObject_TypeCheck(arg, &ObjectType))
                      *obj = ((t_Object *) arg)->object;
                  else if (PyObject_TypeCheck(arg, &FinalizerProxyType))
                  {
                      arg = ((t_fp *) arg)->object;
                      if (PyObject_TypeCheck(arg, &ObjectType))
                          *obj = ((t_Object *) arg)->object;
                      else
                          return -1;
                  }
                  else if (PyString_Check(arg) || PyUnicode_Check(arg))
                  {
                      *obj = p2j(arg);
                      if (PyErr_Occurred())
                          return -1;
                  }
                  else if (arg == Py_True)
                      *obj = *Boolean::TRUE;
                  else if (arg == Py_False)
                      *obj = *Boolean::FALSE;
                  else if (PyInt_Check(arg))
                  {
                      long ln = PyInt_AS_LONG(arg);
                      int n = (int) ln;

                      if (ln != (long) n)
                          *obj = Long((jlong) ln);
                      else
                          *obj = Integer((jint) n);
                  }
                  else if (PyLong_Check(arg))
                      *obj = Long((jlong) PyLong_AsLongLong(arg));
                  else if (PyFloat_Check(arg))
                      *obj = Double((jdouble) PyFloat_AS_DOUBLE(arg));
                  else
                      return -1;
              }
              break;
          }

          default:
            return -1;
        }

        if (types[pos] != '[')
            array = 0;
    }

    if (pos == typeCount)
        return 0;

    return -1;
}


String p2j(PyObject *object)
{
    return String(env->fromPyString(object));
}

PyObject *j2p(const String& js)
{
    return env->fromJString((jstring) js.this$);
}

PyObject *PyErr_SetArgsError(char *name, PyObject *args)
{
    PyObject *err = Py_BuildValue("(sO)", name, args);

    PyErr_SetObject(PyExc_InvalidArgsError, err);
    Py_DECREF(err);

    return NULL;
}

PyObject *PyErr_SetArgsError(PyObject *self, char *name, PyObject *args)
{
    PyObject *type = (PyObject *) self->ob_type;
    PyObject *err = Py_BuildValue("(OsO)", type, name, args);

    PyErr_SetObject(PyExc_InvalidArgsError, err);
    Py_DECREF(err);

    return NULL;
}

PyObject *PyErr_SetArgsError(PyTypeObject *type, char *name, PyObject *args)
{
    PyObject *err = Py_BuildValue("(OsO)", type, name, args);

    PyErr_SetObject(PyExc_InvalidArgsError, err);
    Py_DECREF(err);

    return NULL;
}

PyObject *PyErr_SetJavaError(jthrowable throwable)
{
    PyObject *err = t_Throwable::wrapObject(Throwable(throwable));

    PyErr_SetObject(PyExc_JavaError, err);
    Py_DECREF(err);

    return NULL;
}

void throwPythonError(void)
{
    PyObject *exc = PyErr_Occurred();

    if (exc && PyErr_GivenExceptionMatches(exc, PyExc_JavaError))
    {
        PyObject *value, *traceback;

        PyErr_Fetch(&exc, &value, &traceback);
        if (value)
        {
            PyObject *je = PyObject_CallMethod(value, "getJavaException", "");

            if (!je)
                PyErr_Restore(exc, value, traceback);
            else
            {
                Py_DECREF(exc);
                Py_DECREF(value);
                Py_XDECREF(traceback);
                exc = je;

                if (exc && PyObject_TypeCheck(exc, &ThrowableType))
                {
                    jobject jobj = ((t_Throwable *) exc)->object.this$;

                    env->get_vm_env()->Throw((jthrowable) jobj);
                    Py_DECREF(exc);

                    return;
                }
            }
        }
        else
            Py_XDECREF(traceback);
    }

    if (exc && PyErr_GivenExceptionMatches(exc, PyExc_StopIteration))
    {
        PyErr_Clear();
        return;
    }

    env->get_vm_env()->ThrowNew(RuntimeException::initializeClass(),
                                "PythonError");
}

void throwTypeError(const char *name, PyObject *object)
{
    PyObject *tuple = Py_BuildValue("(ssO)", "while calling", name, object);

    PyErr_SetObject(PyExc_TypeError, tuple);
    Py_DECREF(tuple);

    env->get_vm_env()->ThrowNew(RuntimeException::initializeClass(),
                                "PythonError");
}

int abstract_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *err =
        Py_BuildValue("(sO)", "instantiating java class", self->ob_type);

    PyErr_SetObject(PyExc_NotImplementedError, err);
    Py_DECREF(err);

    return -1;
}

PyObject *callSuper(PyTypeObject *type, const char *name, PyObject *args,
                    int cardinality)
{
    PyObject *super = (PyObject *) type->tp_base;
    PyObject *method =
        PyObject_GetAttrString(super, (char *) name); // python 2.4 cast
    PyObject *value;

    if (!method)
        return NULL;

    if (cardinality > 1)
        value = PyObject_Call(method, args, NULL);
    else
    {
#if PY_VERSION_HEX < 0x02040000
        PyObject *tuple = Py_BuildValue("(O)", args);
#else
        PyObject *tuple = PyTuple_Pack(1, args);
#endif   
        value = PyObject_Call(method, tuple, NULL);
        Py_DECREF(tuple);
    }

    Py_DECREF(method);

    return value;
}

PyObject *callSuper(PyTypeObject *type, PyObject *self,
                    const char *name, PyObject *args, int cardinality)
{
#if PY_VERSION_HEX < 0x02040000
    PyObject *tuple = Py_BuildValue("(OO)", type, self);
#else
    PyObject *tuple = PyTuple_Pack(2, type, self);
#endif
    PyObject *super = PyObject_Call((PyObject *) &PySuper_Type, tuple, NULL);
    PyObject *method, *value;

    Py_DECREF(tuple);
    if (!super)
        return NULL;

    method = PyObject_GetAttrString(super, (char *) name); // python 2.4 cast
    Py_DECREF(super);
    if (!method)
        return NULL;

    if (cardinality > 1)
        value = PyObject_Call(method, args, NULL);
    else
    {
#if PY_VERSION_HEX < 0x02040000
        tuple = Py_BuildValue("(O)", args);
#else
        tuple = PyTuple_Pack(1, args);
#endif
        value = PyObject_Call(method, tuple, NULL);
        Py_DECREF(tuple);
    }

    Py_DECREF(method);

    return value;
}

int castCheck(PyObject *obj, jclass cls, int reportError)
{
    if (!PyObject_TypeCheck(obj, &ObjectType))
    {
        if (reportError)
            PyErr_SetObject(PyExc_TypeError, obj);
        return -1;
    }

    jobject jobj = ((t_Object *) obj)->object.this$;
    
    if (jobj && !env->get_vm_env()->IsInstanceOf(jobj, cls))
    {
        if (reportError)
            PyErr_SetObject(PyExc_TypeError, obj);
        return -1;
    }

    return 0;
}

PyObject *get_extension_iterator(PyObject *self)
{
    return PyObject_CallMethod(self, "iterator", "");
}

PyObject *get_extension_next(PyObject *self)
{
    return PyObject_CallMethod(self, "next", "");
}

PyObject *get_extension_nextElement(PyObject *self)
{
    return PyObject_CallMethod(self, "nextElement", "");
}


/* FinalizerProxy */

static PyObject *t_fc_call(PyObject *self, PyObject *args, PyObject *kwds);

static void t_fp_dealloc(t_fp *self);
static PyObject *t_fp_getattro(t_fp *self, PyObject *name);
static int t_fp_setattro(t_fp *self, PyObject *name, PyObject *value);
static int t_fp_traverse(t_fp *self, visitproc visit, void *arg);
static int t_fp_clear(t_fp *self);
static PyObject *t_fp_repr(t_fp *self);
static PyObject *t_fp_iter(t_fp *self);

PyTypeObject FinalizerClassType = {
    PyObject_HEAD_INIT(NULL)
    0,                                   /* ob_size */
    "jcc.FinalizerClass",                /* tp_name */
    PyType_Type.tp_basicsize,            /* tp_basicsize */
    0,                                   /* tp_itemsize */
    0,                                   /* tp_dealloc */
    0,                                   /* tp_print */
    0,                                   /* tp_getattr */
    0,                                   /* tp_setattr */
    0,                                   /* tp_compare */
    0,                                   /* tp_repr */
    0,                                   /* tp_as_number */
    0,                                   /* tp_as_sequence */
    0,                                   /* tp_as_mapping */
    0,                                   /* tp_hash  */
    (ternaryfunc) t_fc_call,             /* tp_call */
    0,                                   /* tp_str */
    0,                                   /* tp_getattro */
    0,                                   /* tp_setattro */
    0,                                   /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                  /* tp_flags */
    "FinalizerClass",                    /* tp_doc */
    0,                                   /* tp_traverse */
    0,                                   /* tp_clear */
    0,                                   /* tp_richcompare */
    0,                                   /* tp_weaklistoffset */
    0,                                   /* tp_iter */
    0,                                   /* tp_iternext */
    0,                                   /* tp_methods */
    0,                                   /* tp_members */
    0,                                   /* tp_getset */
    &PyType_Type,                        /* tp_base */
    0,                                   /* tp_dict */
    0,                                   /* tp_descr_get */
    0,                                   /* tp_descr_set */
    0,                                   /* tp_dictoffset */
    0,                                   /* tp_init */
    0,                                   /* tp_alloc */
    0,                                   /* tp_new */
};

PyTypeObject FinalizerProxyType = {
    PyObject_HEAD_INIT(NULL)
    0,                                   /* ob_size */
    "jcc.FinalizerProxy",                /* tp_name */
    sizeof(t_fp),                        /* tp_basicsize */
    0,                                   /* tp_itemsize */
    (destructor)t_fp_dealloc,            /* tp_dealloc */
    0,                                   /* tp_print */
    0,                                   /* tp_getattr */
    0,                                   /* tp_setattr */
    0,                                   /* tp_compare */
    (reprfunc)t_fp_repr,                 /* tp_repr */
    0,                                   /* tp_as_number */
    0,                                   /* tp_as_sequence */
    0,                                   /* tp_as_mapping */
    0,                                   /* tp_hash  */
    0,                                   /* tp_call */
    0,                                   /* tp_str */
    (getattrofunc)t_fp_getattro,         /* tp_getattro */
    (setattrofunc)t_fp_setattro,         /* tp_setattro */
    0,                                   /* tp_as_buffer */
    (Py_TPFLAGS_DEFAULT |
     Py_TPFLAGS_HAVE_GC),                /* tp_flags */
    "FinalizerProxy",                    /* tp_doc */
    (traverseproc)t_fp_traverse,         /* tp_traverse */
    (inquiry)t_fp_clear,                 /* tp_clear */
    0,                                   /* tp_richcompare */
    0,                                   /* tp_weaklistoffset */
    (getiterfunc)t_fp_iter,              /* tp_iter */
    0,                                   /* tp_iternext */
    0,                                   /* tp_methods */
    0,                                   /* tp_members */
    0,                                   /* tp_getset */
    0,                                   /* tp_base */
    0,                                   /* tp_dict */
    0,                                   /* tp_descr_get */
    0,                                   /* tp_descr_set */
    0,                                   /* tp_dictoffset */
    0,                                   /* tp_init */
    0,                                   /* tp_alloc */
    0,                                   /* tp_new */
};

static PyObject *t_fc_call(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *obj = PyType_Type.tp_call(self, args, kwds);

    if (obj)
    {
        t_fp *fp = (t_fp *) FinalizerProxyType.tp_alloc(&FinalizerProxyType, 0);

        fp->object = obj;
        obj = (PyObject *) fp;
    }

    return obj;
}

static void t_fp_dealloc(t_fp *self)
{
    if (self->object)
        ((t_JObject *) self->object)->object.weaken$();

    t_fp_clear(self);
    self->ob_type->tp_free((PyObject *) self);
}

static int t_fp_traverse(t_fp *self, visitproc visit, void *arg)
{
    Py_VISIT(self->object);
    return 0;
}

static int t_fp_clear(t_fp *self)
{
    Py_CLEAR(self->object);
    return 0;
}

static PyObject *t_fp_repr(t_fp *self)
{
    return PyObject_Repr(self->object);
}

static PyObject *t_fp_iter(t_fp *self)
{
    return PyObject_GetIter(self->object);
}

static PyObject *t_fp_getattro(t_fp *self, PyObject *name)
{
    return PyObject_GetAttr(self->object, name);
}

static int t_fp_setattro(t_fp *self, PyObject *name, PyObject *value)
{
    return PyObject_SetAttr(self->object, name, value);
}
