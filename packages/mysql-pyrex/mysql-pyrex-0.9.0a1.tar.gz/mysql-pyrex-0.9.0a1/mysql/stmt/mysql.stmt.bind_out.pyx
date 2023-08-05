# $Header: /home/cvs2/mysql/mysql/stmt/mysql.stmt.bind_out.pyx,v 1.7 2006/08/26 21:30:47 ehuss Exp $
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

"""MySQL Statement Output Binding.

This module contains all the Statement output binding objects.  When you create
a new Statement object that selecs data, you need to call
`mysql.stmt.Statement.bind_output` with instances of these objects to indicate
which Python variable to set with the output value.

All output binding objects take at least two parameters, the first is the
object in which to set the value. The second is the name (as a string) of the
parameter to set.

Some output bindings, such as string objects, take a third argument which is
the maximum expected size of the value.  If the data is truncated, then the
call to ``fetch`` raises `mysql.exceptions.Data_Truncated`.

The "streaming" output bindings (blob and text) take an optional fourth
argument ``use_stream``.  If this is set to True, then the value in your object
will show up as a stream object with a ``read`` method.  Otherwise the value
will be set as a string.  See `Base_Out_Stream` for more detail.

All values may be returned as None for NULL values.

As a reference, use the following objects for their corresponding MySQL types:

- TINYINT: `Out_Tiny_Int`
- TINYINT UNSIGNED: `Out_U_Tiny_Int`
- SMALLINT: `Out_Small_Int`
- SMALLINT UNSIGNED: `Out_U_Small_Int`
- MEDIUMINT: `Out_Medium_Int` (currently an alias to `Out_Int`)
- MEDIUMINT UNSIGNED: `Out_U_Medium_Int` (currently an alias to `Out_U_Int`)
- INT: `Out_Int`
- INT UNSIGNED: `Out_U_Int`
- BIGINT: `Out_Big_Int`
- BIGINT UNSIGNED: `Out_U_Big_Int`
- BIT: `Out_Bit`
- BOOL: `Out_Bool`
- FLOAT: `Out_Float`
- FLOAT UNSIGNED: `Out_U_Float`
- DOUBLE: `Out_Double`
- DOUBLE UNSIGNED: `Out_U_Double`
- DECIMAL: `Out_Decimal`
- DECIMAL UNSIGNED: `Out_U_Decimal` (currently an alias to `Out_Decimal`)
- DATE: `Out_Date`
- DATETIME: `Out_Date_Time`
- TIMESTAMP: `Out_Timestamp`
- TIME: `Out_Time`
- YEAR: `Out_Year`
- CHAR: `Out_Char`
- VARCHAR: `Out_Varchar`
- BINARY: `Out_Binary` (currently an alias to `Out_Char`)
- VARBINARY: `Out_Varbinary` (currently an alias to `Out_Varchar`)
- ENUM: `Out_Enum` (currently an alias to `Out_Varchar`)
- SET: `Out_Set`
- TINYBLOB: `Out_Tiny_Blob`
- MEDIUMBLOB: `Out_Medium_Blob`
- BLOB: `Out_Blob`
- LONGBLOB: `Out_Long_Blob`
- TINYTEXT: `Out_Tiny_Text` (currently an alias to `Out_Tiny_Blob`)
- MEDIUMTEXT: `Out_Medium_Text` (currently an alias to `Out_Medium_Blob`)
- TEXT: `Out_Text` (currently an alias to `Out_Blob`)
- LONGTEXT: `Out_Long_Text` (currently an alias to `Out_Long_Blob`)

The following output binding types are not supported:

- GEOMETRY
- INT24
- NEWDATE
"""

__version__ = '$Revision: 1.7 $'

include "../python.pxi"
include "../libc.pxi"
include "../util/inline.pyx"

# XXX: Working around bug with sizeof function.
from extern_mysql cimport MYSQL_BIND

import datetime
import decimal
import sets

cdef class Output_Bind:

    """Base output binding class.

    The constructor takes at least 2 arguments  The first is the object in
    which to set the value.  The second is the name of the parameter to set in
    the object.

    Internally, the Statement object calls ``Output_Bind.load`` on all bound
    outputs during each call to ``fetch``.

    :IVariables:
        - `is_null`: Whether or not the value is null. (Part of MYSQL_BIND
          structure.)  (Read only.)
        - `length`: The length of the value as reported by MySQL. (Part of
          MYSQL_BIND structure.)  (Read only.)
        - `error`: Whether or not there was an error retrieving the value.
          (Part of MYSQL_BIND structure.)  (Read only.)
        - `_buffer_type`: The type of buffer (from enum_field_types). (Part of
          MYSQL_BIND structure.)  (C only.)
        - `_buffer`: The location where the data is stored. (Part of MYSQL_BIND
          structure.)  (C only.)
        - `_buffer_length`: The size of memory allocated for `_buffer`. This is
          set in __init__ by the user. (Part of MYSQL_BIND structure.)  (C
          only.)
        - `_is_unsigned`: Whether or not the value is unsigned.  This should be
          set to 1 in the __new__ method if necessary.  (Part of MYSQL_BIND
          structure.)  (C only.)
        - `_who`: The object what wants the value.  This is set in __init__.  (C
          only.)
        - `_what`: The variable name to set in `_who` with the value.  This is
          set in __init__.  (C only.)
    """

    def __init__(self, who, what, unsigned long max_size=0):
        self._who = who
        self._what = what
        self._buffer_length = max_size

    cdef init(self, Connection connection, statement, extern_mysql.MYSQL_STMT * stmt, raise_error, unsigned int column):
        """Separate initialization function used internally to set state.

        This is used to pass C data types which cannot be in the __init__.

        :Parameters:
            - `connection`: The Connection object.
            - `statement`: The Statement object.
            - `stmt`: The MYSQL_STMT data structure.
            - `raise_error`: A method to call when a MySQL error needs to be
              raised.  It takes no parameters.  The function will look at the
              MYSQL_STMT structure for the error number.
            - `column`: The column number in the output.
        """
        pass

    cdef load(self):
        """Load the data into the Python object.

        This is responsible for setting ``self._who.self._what`` to the value
        that was retrieved.
        """
        raise NotImplementedError

cdef class Out_Null(Output_Bind):

    """Null output binding.

    This always sets the value to None, no matter what was retrieved.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_NULL
        self.is_null = 1

    cdef load(self):
        setattr(self._who, self._what, None)

###############################################################################
# Character Output Bindings
###############################################################################

cdef class Base_Out_String(Output_Bind):

    """Base string-type output binding.

    All output string types take a third argument which is the maximum size of
    the buffer.

    If the buffer is not large enough, the call to ``fetch`` will raise
    `mysql.exceptions.Data_Truncated` and the value in the object will be
    truncated.
    """

    def __init__(self, who, what, unsigned long max_size):
        Output_Bind.__init__(self, who, what, max_size)
        self._buffer = PyMem_Malloc(max_size)

    def __dealloc__(self):
        PyMem_Free(self._buffer)

    cdef load(self):
        cdef unsigned long actual_length

        if self.is_null:
            value = None
        else:
            # Documentation is slightly wrong with regards to the definition of
            # the length parameter.  In the case of truncation, it is the
            # length of the length of the column data if it weren't truncated.
            # Filed bug #16289 with MySQL to clarify the documentation or
            # change the behavior.  (Update: documentation has been updated.)
            if self.length > self._buffer_length:
                actual_length = self._buffer_length
            else:
                actual_length = self.length
            value = PyString_FromStringAndSize(<char *> self._buffer, actual_length)
        setattr(self._who, self._what, value)

cdef class Out_Varchar(Base_Out_String):

    """VARCHAR output binding.

    The constructor takes 3 arguments:

    - ``who``: The object in which to set the value.
    - ``what``: The name of the parameter in the object to set.
    - ``max_size``: The maximum size of the string.  Attempting to load a value
      that is larger than this value will raise
      `mysql.exceptions.Data_Truncated` in the call to ``fetch`` and the data
      will be truncated to this length.

    Note that `Out_Varbinary` and `Out_Enum` are aliases for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_VAR_STRING

Out_Varbinary = Out_Varchar
Out_Enum = Out_Varchar

cdef class Out_Set(Base_Out_String):

    """SET output binding.

    The constructor takes 3 arguments:

    - ``who``: The object in which to set the value.
    - ``what``: The name of the parameter in the object to set.
    - ``max_size``: The maximum size of the string.  Attempting to load a value
      that is larger than this value will raise
      `mysql.exceptions.Data_Truncated` in the call to ``fetch`` and the data
      will be truncated to this length.

    The resulting value will be a ``sets.Set`` instance.
    """

    def __new__(self, *args, **kwargs):
        # MySQL does not support MYSQL_TYPE_SET
        self._buffer_type = extern_mysql.MYSQL_TYPE_VAR_STRING

    cdef load(self):
        if self.is_null:
            value = None
        else:
            if self.length > self._buffer_length:
                actual_length = self._buffer_length
            else:
                actual_length = self.length
            str_value = PyString_FromStringAndSize(<char *> self._buffer, actual_length)
            value = sets.Set(str_value.split(','))
        setattr(self._who, self._what, value)

cdef class Out_Char(Base_Out_String):

    """CHAR output binding.

    The constructor takes 3 arguments:

    - ``who``: The object in which to set the value.
    - ``what``: The name of the parameter in the object to set.
    - ``max_size``: The maximum size of the string.  Attempting to load a value
      that is larger than this value will raise
      `mysql.exceptions.Data_Truncated` in the call to ``fetch`` and the data
      will be truncated to this length.

    Note that `Out_Binary` is an alias for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_STRING

Out_Binary = Out_Char

###############################################################################
# Streaming Character Output Bindings
###############################################################################

cdef class Output_Stream:

    """Output stream.

    This is the object placed into your output binding that will relay data
    from MySQL.

    :IVariables:
        - `_stmt`: MYSQL_STMT structure.
        - `_column`: The column number.
        - `_bind`: The MYSQL_BIND structure (initialized in __init__).
        - `_offset`: The current offset into the result.
        - `_length`: The length of the value as reported by MySQL.
        - `_error`: Whether or not there was an error retrieving the value.
          Used for detecting truncation.
        - `_raise_error`: A callable object used to raise a MySQL error.  Takes
          no arguments.
        - `_connection`: The `mysql.connection.Connection` object.
        - `_statement`: The `mysql.stmt.Statement` object.
    """

    cdef extern_mysql.MYSQL_STMT * _stmt
    cdef unsigned int _column
    cdef extern_mysql.MYSQL_BIND _bind
    cdef unsigned long _offset
    cdef unsigned long _length
    cdef extern_mysql.my_bool _error
    cdef object _raise_error
    cdef Connection _connection
    cdef object _statement

    def __init__(self, unsigned int column,
                       int buffer_type,
                       unsigned long buffer_length):
        self._column = column
        self._offset = 0
        memset(&self._bind, 0, sizeof(MYSQL_BIND))
        self._bind.buffer_type = buffer_type
        self._bind.buffer_length = buffer_length
        self._bind.length = &self._length
        self._bind.buffer = PyMem_Malloc(buffer_length)
        self._bind.error = &self._error

    def __dealloc__(self):
        PyMem_Free(self._bind.buffer)

    def read(self, bytes=None):
        """Read data from the stream.

        **Note** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Parameters:
            - `bytes`: The number of bytes to read.  If not specified, it will
              read all bytes that are left.

        :Return:
            Returns a string of data.  Returns an empty string if there is no
            more data.

        :Exceptions:
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        cdef unsigned long bytes_left
        cdef unsigned long bytes_read

        self._error = 0

        bytes_left = self._length - self._offset
        if bytes is not None:
            bytes_left = min(bytes, bytes_left)

        self._connection._check_unbuffered_result(self._statement)

        read_array = []

        while bytes_left > 0:
            if extern_mysql.mysql_stmt_fetch_column(self._stmt, &self._bind, self._column, self._offset):
                self._raise_error()
            # I do not like this API.
            if bytes_left < self._bind.buffer_length:
                bytes_read = bytes_left
                bytes_left = 0
            else:
                bytes_read = self._bind.buffer_length
                bytes_left = bytes_left - self._bind.buffer_length
            # In extremely rare cases (like if the protocol gets reset),
            # length of the column will change.
            if self._length < bytes_read:
                raise AssertionError('MySQL indicated buffer size smaller than expected (got %i expected %i)' % (self._length, bytes_read))
            self._offset = self._offset + bytes_read
            value = PyString_FromStringAndSize(<char *> self._bind.buffer, bytes_read)
            read_array.append(value)

        if bytes is None:
            if self._error:
                raise AssertionError('Truncation still set after reading all data?')
        return ''.join(read_array)

    cdef reset(self, unsigned long length):
        """Reset the object.

        This is used internally between calls to ``fetch``.
        """
        self._offset = 0
        self._length = length

cdef class Base_Out_Stream(Output_Bind):

    """Base class for streaming output.

    The constructor takes the following arguments:

    - ``who``: The object on which to set the value.
    - ``what``: The attribute name to set on the object.
    - ``max_size``: The size of the buffer in bytes to use to fetch data.
      Defaults to 4000.
    - ``store_stream``: If True, will store a stream object (`Output_Stream`)
      which has a ``read`` method.  Otherwise it stores the entire result as a
      string.  Defaults to False.
    """

    # Maintain the same stream object for all fetches.
    # This is somewhat delicate, since the stream object can never die before I
    # do, but keeping a local reference that the user can't see should maintain
    # that rule.
    cdef Output_Stream _stream
    cdef int _store_stream

    def __init__(self, who, what, unsigned long max_size=4000, int store_stream=0):
        if max_size <= 0:
            raise ValueError('max_size must be greater than zero')
        self._store_stream = store_stream
        Output_Bind.__init__(self, who, what, max_size)

    cdef init(self, Connection connection, statement, extern_mysql.MYSQL_STMT * stmt, raise_error, unsigned int column):
        self._stream = Output_Stream(column, self._buffer_type, self._buffer_length)
        # Work around inability to pass C objects in __init__.
        self._stream._stmt = stmt
        self._stream._raise_error = raise_error
        self._buffer = self._stream._bind.buffer
        self._stream._statement = statement
        self._stream._connection = connection

    cdef load(self):
        self._stream.reset(self.length)
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            if self._store_stream:
                setattr(self._who, self._what, self._stream)
            else:
                setattr(self._who, self._what, self._stream.read())

cdef class Out_Tiny_Blob(Base_Out_Stream):

    """TINYBLOB output binding.

    The constructor takes the following arguments:

    - ``who``: The object on which to set the value.
    - ``what``: The attribute name to set on the object.
    - ``max_size``: The size of the buffer in bytes to use to fetch data.
      Defaults to 4000.
    - ``store_stream``: If True, will store a stream object (`Output_Stream`)
      which has a ``read`` method.  Otherwise it stores the entire result as a
      string.  Defaults to False.

    Note that `Out_Tiny_Text` is an alias for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_TINY_BLOB

cdef class Out_Medium_Blob(Base_Out_Stream):

    """MEDIUMBLOB output binding.

    The constructor takes the following arguments:

    - ``who``: The object on which to set the value.
    - ``what``: The attribute name to set on the object.
    - ``max_size``: The size of the buffer in bytes to use to fetch data.
      Defaults to 4000.
    - ``store_stream``: If True, will store a stream object (`Output_Stream`)
      which has a ``read`` method.  Otherwise it stores the entire result as a
      string.  Defaults to False.

    Note that `Out_Medium_Text` is an alias for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_MEDIUM_BLOB

cdef class Out_Blob(Base_Out_Stream):

    """BLOB output binding.

    The constructor takes the following arguments:

    - ``who``: The object on which to set the value.
    - ``what``: The attribute name to set on the object.
    - ``max_size``: The size of the buffer in bytes to use to fetch data.
      Defaults to 4000.
    - ``store_stream``: If True, will store a stream object (`Output_Stream`)
      which has a ``read`` method.  Otherwise it stores the entire result as a
      string.  Defaults to False.

    Note that `Out_Text` is an alias for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_BLOB

cdef class Out_Long_Blob(Base_Out_Stream):

    """LONGBLOB output binding.

    The constructor takes the following arguments:

    - ``who``: The object on which to set the value.
    - ``what``: The attribute name to set on the object.
    - ``max_size``: The size of the buffer in bytes to use to fetch data.
      Defaults to 4000.
    - ``store_stream``: If True, will store a stream object (`Output_Stream`)
      which has a ``read`` method.  Otherwise it stores the entire result as a
      string.  Defaults to False.

    Note that `Out_Long_Text` is an alias for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_LONG_BLOB

Out_Tiny_Text = Out_Tiny_Blob
Out_Medium_Text = Out_Medium_Blob
Out_Text = Out_Blob
Out_Long_Text = Out_Long_Blob

###############################################################################
# Numeric Output Bindings
###############################################################################

cdef class Out_Tiny_Int(Output_Bind):

    """TINYINT output binding.

    The value will be an integer.
    """

    cdef char _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_TINY
        self._buffer = &self._value

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            setattr(self._who, self._what, self._value)

cdef class Out_U_Tiny_Int(Output_Bind):

    """UNSIGNED TINYINT output binding.

    The value will be an integer.
    """

    cdef unsigned char _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_TINY
        self._buffer = &self._value
        self._is_unsigned = 1

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            setattr(self._who, self._what, self._value)

cdef class Out_Bool(Out_Tiny_Int):

    """BOOL output binding.

    The value will be an integer.
    """

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            setattr(self._who, self._what, bool(self._value))

cdef class Out_Small_Int(Output_Bind):

    """SMALLINT output binding.

    The value will be an integer.
    """

    cdef short int _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_SHORT
        self._buffer = &self._value

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            setattr(self._who, self._what, self._value)

cdef class Out_U_Small_Int(Output_Bind):

    """UNSIGNED SMALLINT output binding.

    The value will be an integer.
    """

    cdef unsigned short int _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_SHORT
        self._buffer = &self._value
        self._is_unsigned = 1

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            setattr(self._who, self._what, self._value)

cdef class Out_Int(Output_Bind):

    """INT output binding.

    The value will be an integer.

    Note that `Out_Medium_Int` is an alias for this object.
    """

    cdef int _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_LONG
        self._buffer = &self._value

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            setattr(self._who, self._what, self._value)

cdef class Out_U_Int(Output_Bind):

    """UNSIGNED INT output binding.

    The value will be an integer.

    Note that `Out_U_Medium_Int` is an alias for this object.
    """

    cdef unsigned int _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_LONG
        self._buffer = &self._value
        self._is_unsigned = 1

    cdef load(self):
        # Pyrex dosn't seem to know that unsigned int value do not always fit
        # in Python integer.
        cdef object value
        if self.is_null:
            value = None
        else:
            if self._value > PyInt_GetMax():
                value = PyLong_FromUnsignedLong(self._value)
            else:
                value = PyInt_FromLong(self._value)
        setattr(self._who, self._what, value)

Out_Medium_Int = Out_Int
Out_U_Medium_Int = Out_U_Int

cdef class Out_Big_Int(Output_Bind):

    """BIGINT output binding.

    The value will be an integer.
    """

    cdef long long _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_LONGLONG
        self._buffer = &self._value

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            setattr(self._who, self._what, _minimal_longlong(self._value))

cdef class Out_U_Big_Int(Output_Bind):

    """UNSIGNED BIGINT output binding.

    The value will be an integer.
    """

    cdef unsigned long long _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_LONGLONG
        self._buffer = &self._value
        self._is_unsigned = 1

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            setattr(self._who, self._what, _minimal_ulonglong(self._value))

cdef class Out_Float(Output_Bind):

    """FLOAT output binding.

    The value will be a float.

    Note that `Out_U_Float` is an alias for this object.
    """

    cdef float _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_FLOAT
        self._buffer = &self._value

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            setattr(self._who, self._what, self._value)

Out_U_Float = Out_Float

cdef class Out_Double(Output_Bind):

    """DOUBLE output binding.

    The value will be a float.

    Note that `Out_U_Double` is an alias for this object.
    """

    cdef double _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_DOUBLE
        self._buffer = &self._value

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            setattr(self._who, self._what, self._value)

Out_U_Double = Out_Double

cdef class Out_Bit(Output_Bind):

    """BIT output binding.

    The value will be an integer.
    """

    def __init__(self, who, what):
        Output_Bind.__init__(self, who, what, 8)
        self._buffer = PyMem_Malloc(8)

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_BIT

    def __dealloc__(self):
        PyMem_Free(self._buffer)

    cdef load(self):
        cdef unsigned long long value
        cdef unsigned char * p

        # Use local var to avoid lots of casts.
        p = <unsigned char *> self._buffer

        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            value = <unsigned long long> p[0]
            value = value << 8
            value = value + <unsigned long long> p[1]
            value = value << 8
            value = value + <unsigned long long> p[2]
            value = value << 8
            value = value + <unsigned long long> p[3]
            value = value << 8
            value = value + <unsigned long long> p[4]
            value = value << 8
            value = value + <unsigned long long> p[5]
            value = value << 8
            value = value + <unsigned long long> p[6]
            value = value << 8
            value = value + <unsigned long long> p[7]
            setattr(self._who, self._what, _minimal_ulonglong(value))

###############################################################################
# Decimal Output Bindings
###############################################################################

cdef class Out_Decimal(Output_Bind):

    """DECIMAL output binding.

    The value will be a ``decimal.Decimal`` object.

    Note that `Out_U_Decimal` is an alias for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_DECIMAL

    def __init__(self, who, what):
        # Maximum digits is 65
        # Plus 1 for decimal point and sign.
        Output_Bind.__init__(self, who, what, 67)
        self._buffer = PyMem_Malloc(67)

    def __dealloc__(self):
        PyMem_Free(self._buffer)

    cdef load(self):
        cdef unsigned long actual_length

        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            # Documentation is slightly wrong with regards to the definition of
            # the length parameter.  In the case of truncation, it is the
            # length of the length of the column data if it weren't truncated.
            # Filed bug #16289 with MySQL to clarify the documentation or
            # change the behavior. (Update: documentation has been updated.)
            if self.length > self._buffer_length:
                actual_length = self._buffer_length
            else:
                actual_length = self.length
            value = PyString_FromStringAndSize(<char *> self._buffer, actual_length)

            decimal_value = decimal.Decimal(value)
            setattr(self._who, self._what, decimal_value)

Out_U_Decimal = Out_Decimal

cdef class Out_New_Decimal(Out_Decimal):

    """NEW DECIMAL output binding.

    The value will be a ``decimal.Decimal`` object.

    This is currently implemented exactly the same as `Out_Decimal` using the
    ``MYSQL_TYPE_NEWDECIMAL`` field type.  It is currently not known if this
    actually causes any different behavior in the server.

    Note that `Out_U_New_Decimal` is an alias for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_NEWDECIMAL

Out_U_New_Decimal = Out_New_Decimal

###############################################################################
# Time Output Bindings
###############################################################################

cdef class Out_Timestamp(Output_Bind):

    """TIMESTAMP output binding.

    The value will be a ``datetime.datetime`` object.
    """

    cdef extern_mysql.MYSQL_TIME _ts

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_TIMESTAMP
        self._buffer = &self._ts

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            value = datetime.datetime(self._ts.year,
                                      self._ts.month,
                                      self._ts.day,
                                      self._ts.hour,
                                      self._ts.minute,
                                      self._ts.second,
                                      self._ts.second_part)
            setattr(self._who, self._what, value)

cdef class Out_Date(Output_Bind):

    """DATE output binding.

    The value will be a ``datetime.date`` object.
    """

    cdef extern_mysql.MYSQL_TIME _ts

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_DATE
        self._buffer = &self._ts

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            value = datetime.date(self._ts.year,
                                  self._ts.month,
                                  self._ts.day)
            setattr(self._who, self._what, value)

cdef class Out_Time(Output_Bind):

    """TIME output binding.

    The value will be a ``datetime.timedelta`` object.
    """

    cdef extern_mysql.MYSQL_TIME _ts

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_TIME
        self._buffer = &self._ts

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            if self._ts.neg:
                value = datetime.timedelta(hours=-<signed int>self._ts.hour,
                                           minutes=-<signed int>self._ts.minute,
                                           seconds=-<signed int>self._ts.second,
                                           microseconds=-<signed int>self._ts.second_part)
            else:
                value = datetime.timedelta(hours=self._ts.hour,
                                           minutes=self._ts.minute,
                                           seconds=self._ts.second,
                                           microseconds=self._ts.second_part)
            setattr(self._who, self._what, value)

cdef class Out_Date_Time(Output_Bind):

    """DATETIME output binding.

    The value will be a ``datetime.datetime`` object.
    """

    cdef extern_mysql.MYSQL_TIME _ts

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_DATETIME
        self._buffer = &self._ts

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            value = datetime.datetime(self._ts.year,
                                      self._ts.month,
                                      self._ts.day,
                                      self._ts.hour,
                                      self._ts.minute,
                                      self._ts.second,
                                      self._ts.second_part)
            setattr(self._who, self._what, value)

cdef class Out_Year(Output_Bind):

    """YEAR output binding.

    The value will be an integer.
    """

    cdef short int _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_YEAR
        self._buffer = &self._value

    cdef load(self):
        if self.is_null:
            setattr(self._who, self._what, None)
        else:
            setattr(self._who, self._what, self._value)
