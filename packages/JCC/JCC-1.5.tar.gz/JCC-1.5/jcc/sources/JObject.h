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

#ifndef _JObject_H
#define _JObject_H

#include <stdio.h>
#include "JCCEnv.h"

class JObject {
public:
    jobject this$;
    int id;

    inline explicit JObject(jobject obj)
    {
        id = env->id(obj);
        this$ = env->newGlobalRef(obj, id);
    }

    inline JObject(const JObject& obj)
    {
        id = obj.id;
        this$ = env->newGlobalRef(obj.this$, id);
    }

    virtual ~JObject()
    {
        this$ = env->deleteGlobalRef(this$, id);
    }

    virtual inline int isNull() const
    {
        return this$ == NULL;
    }

    inline int operator==(const JObject& obj) const
    {
        return id == obj.id && env->isSame(this$, obj.this$);
    }

    JObject& operator=(const JObject& obj)
    {
        jobject prev = this$;

        this$ = env->newGlobalRef(obj.this$, obj.id);
        env->deleteGlobalRef(prev, id);
        id = obj.id;

        return *this;
    }
};

#include <Python.h>

class t_JObject {
public:
    PyObject_HEAD
    JObject object;
};

extern PyTypeObject JObjectType;

#endif /* _JObject_H */
