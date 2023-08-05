
#include <Python.h>
#include "macros.h"

extern PyMethodDef module_funcs[];
extern PyTypeObject JObjectType, ConstVariableDescriptorType, JCCEnvType;

namespace java {
    namespace lang {
        void __install__(PyObject *m);
    }
}

void __initialize__(PyObject *m)
{
}


extern "C" {

    void init_jcc(void)
    {
        PyObject *m = Py_InitModule3("_jcc", module_funcs, "_jcc");

        INSTALL_TYPE(JObject, m);
        INSTALL_TYPE(ConstVariableDescriptor, m);
        INSTALL_TYPE(JCCEnv, m);
        java::lang::__install__(m);
    }
}
