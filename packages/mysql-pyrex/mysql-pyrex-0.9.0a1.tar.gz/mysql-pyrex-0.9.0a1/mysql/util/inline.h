/*
  $Header: /home/cvs2/mysql/mysql/util/inline.h,v 1.1 2006/08/26 22:13:04 ehuss Exp $
  Copyright (c) 2006, Eric Huss
  All rights reserved.

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
  3. Neither the name of Eric Huss nor the names of any contributors may be
     used to endorse or promote products derived from this software without
     specific prior written permission.

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
  POSSIBILITY OF SUCH DAMAGE.
*/

/*
  Code inlined for Pyrex.
*/

#ifndef _PYREX_INLINE_H_
#define _PYREX_INLINE_H_

#include "Python.h"

#define PyINLINE_FUNC(RTYPE) static inline RTYPE

/* Converting Python builtins to direct calls. */
#define isinstance(o,c)         PyObject_IsInstance(o,c)
#define issubclass(c,csuper)    PyObject_IsSubclass(c,csuper)
#define hasattr(o,a)            PyObject_HasAttr(o,a)
#define getattr(o,a)            PyObject_GetAttr(o,a)
#define callable(o)             PyCallable_Check(o)

/* Abstract functions. */
PyINLINE_FUNC(PyObject *)
PySequence_Fast_GET_ITEM_SAFE (PyObject * o, int i)
{
    PyObject * x = PySequence_Fast_GET_ITEM(o, i);
    Py_INCREF(x);
    return x;
}

/* List functions. */

PyINLINE_FUNC(PyObject *)
PyList_GET_ITEM_SAFE (PyObject * l, int i)
{
    PyObject * x = PyList_GET_ITEM (l, i);
    Py_INCREF (x);
    return x;
}

PyINLINE_FUNC(void)
PyList_SET_ITEM_SAFE (PyObject * l, int i, PyObject * v)
{
    PyList_SET_ITEM (l, i, v);
    Py_INCREF (v);
}

PyINLINE_FUNC(PyObject *)
PyList_GetItem_SAFE (PyObject * l, int i)
{
    PyObject * x = PyList_GetItem (l, i);
    Py_INCREF (x);
    return x;
}

PyINLINE_FUNC(void)
PyList_SetItem_SAFE (PyObject * l, int i, PyObject * v)
{
    PyList_SetItem (l, i, v);
    Py_INCREF (v);
}

PyINLINE_FUNC(int)
PyList_DelSlice_SAFE(PyObject * list, int low, int high)
{
    // Pyrex won't allow NULL as a Python parameter.
    return PyList_SetSlice(list, low, high, NULL);
}

/* Tuple functions. */

PyINLINE_FUNC(PyObject *)
PyTuple_GET_ITEM_SAFE (PyObject * l, int i)
{
    PyObject * x = PyTuple_GET_ITEM (l, i);
    Py_INCREF (x);
    return x;
}

PyINLINE_FUNC(void)
PyTuple_SET_ITEM_SAFE (PyObject * l, int i, PyObject * v)
{
    PyTuple_SET_ITEM (l, i, v);
    Py_INCREF (v);
}

PyINLINE_FUNC(PyObject *)
PyTuple_GetItem_SAFE (PyObject * l, int i)
{
    PyObject * x = PyTuple_GetItem (l, i);
    Py_INCREF (x);
    return x;
}

PyINLINE_FUNC(void)
PyTuple_SetItem_SAFE (PyObject * l, int i, PyObject * v)
{
    PyTuple_SetItem (l, i, v);
    Py_INCREF (v);
}

/* Dict functions. */

/*
  Note, you *must* set ``instead`` to a real Python object, you cannot set it
  to NULL.  Suggest using None.
*/
PyINLINE_FUNC(PyObject *)
PyDict_GET_ITEM_SAFE (PyObject * d, PyObject * k, PyObject * instead)
{
    PyObject * r = PyDict_GetItem (d, k);
    if (r == NULL) {
        r = instead;
    }
    Py_INCREF (r);
    return r;
}

#endif
