# $Header: /home/cvs2/mysql/mysql/util/misc.pyx,v 1.6 2006/08/27 03:01:02 ehuss Exp $
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

"""Miscellaneous utility functions."""

__version__ = '$Revision: 1.6 $'

include "python.pxi"
include "inline.pyx"

def big_str_to_host_int(value):
    """Convert a string in big-endian format into an integer.

    :Parameters:
        - `value`: A binary string in big-endian format.  Must be less than or
          equal to 8 bytes in length.

    :Return:
        Returns an integer.
    """
    cdef int value_len
    cdef char * value_str
    cdef int i
    cdef unsigned int v_32
    cdef unsigned long long v_64

    PyString_AsStringAndSize(value, &value_str, &value_len)
    if value_len == 0:
        return 0
    elif value_len <= 4:
        v_32 = <unsigned char> value_str[0]
        for i from 1 <= i < value_len:
            v_32 = v_32 << 8
            v_32 = v_32 + <unsigned char> value_str[i]
        return _minimal_ulong(v_32)
    elif value_len <= 8:
        v_64 = <unsigned char> value_str[0]
        for i from 1 <= i < value_len:
            v_64 = v_64 << 8
            v_64 = v_64 + <unsigned char> value_str[i]
        return _minimal_ulonglong(v_64)
    else:
        raise AssertionError('Bit value is larger than expected.')
