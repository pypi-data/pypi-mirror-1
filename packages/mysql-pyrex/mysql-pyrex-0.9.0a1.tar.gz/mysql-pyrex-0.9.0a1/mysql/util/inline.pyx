# $Header: /home/cvs2/mysql/mysql/util/inline.pyx,v 1.3 2006/08/26 22:13:04 ehuss Exp $
# Copyright (c) 2006, Eric Huss
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of Eric Huss nor the names of any contributors may be
#    used to endorse or promote products derived from this software without
#    specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Inline functions used in various parts of the code.

cdef object __builtin__
import __builtin__

cdef object True
True = __builtin__.True

cdef object False
False = __builtin__.False

cdef object bool
bool = __builtin__.bool

cdef _minimal_ulonglong(unsigned long long value):
    if value > PyInt_GetMax():
        return PyLong_FromUnsignedLongLong(value)
    else:
        return PyInt_FromLong(value)

cdef _minimal_longlong(long long value):
    if value > PyInt_GetMax() or value < -PyInt_GetMax()-1:
        return PyLong_FromLongLong(value)
    else:
        return PyInt_FromLong(value)

cdef _minimal_ulong(unsigned long value):
    if value > PyInt_GetMax():
        return PyLong_FromUnsignedLong(value)
    else:
        return PyInt_FromLong(value)


cdef extern from "inline.h":

    object  PySequence_Fast_GET_ITEM_SAFE   (object, int)

    object  PyList_GET_ITEM_SAFE    (object, int)
    void    PyList_SET_ITEM_SAFE    (object, int, object)
    object  PyList_GetItem_SAFE     (object, int)
    void    PyList_SetItem_SAFE     (object, int, object)
    int     PyList_DelSlice_SAFE    (object, int, int) except -1

    object  PyTuple_GET_ITEM_SAFE   (object, int)
    void    PyTuple_SET_ITEM_SAFE   (object, int, object)
    object  PyTuple_GetItem_SAFE    (object, int)
    void    PyTuple_SetItem_SAFE    (object, int, object)

    object  PyDict_GET_ITEM_SAFE    (object, object, object)

    int     isinstance              (object, object)
    int     issubclass              (object, object)
    int     hasattr                 (object, object)
    object  getattr                 (object, object)
    int     callable                (object)
