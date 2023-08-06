
#include <jni.h>
#include <Python.h>
#include "java/lang/Class.h"
#include "java/lang/RuntimeException.h"
#include "macros.h"

extern PyTypeObject JObjectType, JCCEnvType, ConstVariableDescriptorType;

PyObject *initVM(PyObject *self, PyObject *args, PyObject *kwds);

namespace java {
    namespace lang {
        void __install__(PyObject *m);
    }
}

PyObject *__initialize__(PyObject *module, PyObject *args, PyObject *kwds)
{
    PyObject *env = initVM(module, args, kwds);

    if (env == NULL)
        return NULL;

    java::lang::Class::initializeClass();
    java::lang::RuntimeException::initializeClass();

    return env;
}

#include "jccfuncs.h"

extern "C" {

    void init_jcc(void)
    {
        PyObject *m = Py_InitModule3("_jcc", jcc_funcs, "_jcc");

        INSTALL_TYPE(JObject, m);
        INSTALL_TYPE(JCCEnv, m);
        INSTALL_TYPE(ConstVariableDescriptor, m);
        java::lang::__install__(m);
    }
}
