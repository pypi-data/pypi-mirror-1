# $Header: /home/cvs2/mysql/mysql/stmt/mysql.stmt.bind_in.pyx,v 1.5 2006/08/26 21:30:47 ehuss Exp $
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

"""MySQL Statement Input Binding.

This module contains all the Statement input binding objects.  When you create
a new Statement object with parameters, you need to call
`mysql.stmt.Statement.bind_input` with instances of these objects to indicate
which Python variable to read the value from.

All input binding objects take at least two parameters, the first is the object
in which to look for a parameter. The second is the name (as a string) of the
parameter to read.

Some input bindings, such as string objects, take a third argument which is the
maximum expected size of the value.

The "streaming" input bindings (blob and text) take an optional ``use_stream``
parameter.  If this is set to True, then the value in your object will show up
as a stream object with a ``write`` method.  Otherwise the value is expected to
be a string. See `Base_In_Stream` for more detail.

All values may be set to None in which case the value will be set to NULL in
the database. However, when you are using a stream, do not write any data, and
the value will be set to NULL.  If you want an empty string when using a
stream, call write with an empty string.

As a reference, use the following objects for their corresponding MySQL types:

- TINYINT: `In_Tiny_Int`
- TINYINT UNSIGNED: `In_U_Tiny_Int`
- SMALLINT: `In_Small_Int`
- SMALLINT UNSIGNED: `In_U_Small_Int`
- MEDIUMINT: `In_Medium_Int`
- MEDIUMINT UNSIGNED: `In_U_Medium_Int`
- INT: `In_Int`
- INT UNSIGNED: `In_U_Int`
- BIGINT: `In_Big_Int`
- BIGINT UNSIGNED: `In_U_Big_Int`
- BIT: `In_Bit`
- BOOL: `In_Bool`
- FLOAT: `In_Float`
- FLOAT UNSIGNED: `In_U_Float`
- DOUBLE: `In_Double`
- DOUBLE UNSIGNED: `In_U_Double`
- DECIMAL: `In_Decimal` (Warning: broken in server 5.0.18 and earlier.)
- DECIMAL UNSIGNED: `In_U_Decimal` (Warning: broken in server 5.0.18 and earlier.)
- DATE: `In_Date`
- DATETIME: `In_Date_Time`
- TIMESTAMP: `In_Timestamp`
- TIME: `In_Time`
- YEAR: `In_Year`
- CHAR: `In_Char`
- VARCHAR: `In_Varchar`
- BINARY: `In_Binary` (currently an alias to `In_Char`)
- VARBINARY: `In_Varbinary` (currently an alias to `In_Varchar`)
- ENUM: `In_Enum`
- SET: `In_Set`
- TINYBLOB: `In_Tiny_Blob`
- MEDIUMBLOB: `In_Medium_Blob`
- BLOB: `In_Blob`
- LONGBLOB: `In_Long_Blob`
- TINYTEXT: `In_Tiny_Text` (currently an alias to `In_Tiny_Blob`)
- MEDIUMTEXT: `In_Medium_Text` (currently an alias to `In_Medium_Blob`)
- TEXT: `In_Text` (currently an alias to `In_Blob`)
- LONGTEXT: `In_Long_Text` (currently an alias to `In_Long_Blob`)

The following input binding types are not supported:

- GEOMETRY
- INT24
- NEWDATE
"""

__version__ = '$Revision: 1.5 $'

include "../python.pxi"
include "../libc.pxi"

import datetime
import decimal
import sets

cdef class Input_Bind:

    """Base input binding class.

    The constructor takes two arguments, the first is the object in which to
    look for a parameter. The second is the name (as a string) of the parameter
    to read.

    Internally, the Statement object calls ``Input_Bind.set_value`` on all
    bound inputs just before calling execute.  The ``set_value`` method is
    responsible for setting the internal C value from the Python value
    (``who.what``) that is pointed to by `_buffer_type`.  Note that the
    streaming objects are unique because their data is already transfered when
    the user wrote to the stream.

    :IVariables:
        - `_buffer_type`: The type of the buffer (as
          ``extern_mysql.enum_field_types``).  Should be set in ``__new__``. (C
          only.)
        - `_buffer`: A ``void *`` pointer to where the data is stored.  Should
          be set in ``__new__``. (C only.)
        - `_buffer_length`: The size of `_buffer` in bytes.  Not used for some
          data types (such as numbers) because the size is implied by the
          buffer type. Should be set in ``__new__`` if it is needed. (C only.)
        - `_is_null`: Whether or not the value is NULL. Should always be set or
          cleared in the ``set_value`` method. (C only.)
        - `_is_unsigned`: Set to true if the buffer is an unsigned number.
          Should be set in ``__new__``. (C only.)
        - `_length`: The length of the value in `_buffer`.  Not used for some
          data types (such as numbers) because the size is implied by the data
          type.  Should be set in the ``set_value`` method if needed.  (C only.)
        - `_who`: The object who contains the value.  Automatically set from
          __init__. (C only.)
        - `_what`: A string of the attribute to get from `_who` for the Python
          value to read.  Automatically set from __init__. (C only.)
    """

    def __new__(self, *args, **kwargs):
        self._buffer = NULL
        self._length = 0
        self._buffer_length = 0
        self._is_unsigned = 0
        self._is_null = 0

    def __init__(self, who, what):
        self._who = who
        self._what = what

    cdef init(self, Connection connection, statement, extern_mysql.MYSQL_STMT * stmt, raise_error, unsigned int param_num):
        """Initialize the object.

        This is used because the Statement object needs to pass some C data
        types into the object.  This is currently only used by the streaming
        objects.  The default implementation does nothing.

        :Parameters:
            - `connection`: A Connection object.
            - `statement`: A Statement object.
            - `stmt`: The MYSQL_STMT data structure.
            - `raise_error`: A method to call when a MySQL error needs to be
              raised.  It takes no parameters.  The function will look at the
              MYSQL_STMT structure for the error number.
            - `param_num`: The parameter number, starting at 0.
        """
        pass

    cdef set_value(self):
        """Read the value from ``self._who.self._what`` and update the buffer.

        :Exceptions:
            - `OverflowError`: The Python value will not fit into the buffer.
            - `TypeError`: The type of the Python object does not match what is
              expected for the type of input.
        """
        raise NotImplementedError


cdef class In_Null(Input_Bind):

    """Null input binding.

    The value is not read with this binding.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_NULL
        self._is_null = 1

###############################################################################
# Character Input Bindings
###############################################################################

cdef class Base_In_String(Input_Bind):

    """Base class input binding that is a character array from a string.

    All input string types take a third argument which is the maximum size of
    the buffer.

    If you attempt to give an input value that is larger than the specified
    maximum size, then the call to ``execute`` will raise ``OverflowError``.

    :IVariables:
        - `_value`: The ``char *`` character array, allocated in ``__init__``.
          (C only.)
    """

    cdef char * _value

    def __init__(self, who, what, max_size):
        self._value = <char *> PyMem_Malloc(max_size)
        self._buffer = self._value
        self._buffer_length = max_size
        Input_Bind.__init__(self, who, what)

    def __dealloc__(self):
        PyMem_Free(self._value)

    cdef set_value(self):
        cdef long value_len

        value = getattr(self._who, self._what, None)
        if value is None:
            self._length = 0
            self._is_null = 1
        else:
            value_len = PyString_Size(value)
            if value_len > self._buffer_length:
                raise OverflowError('Object length (%i) too large for buffer (%i).' % (value_len, self._buffer_length))
            memcpy(self._value, PyString_AsString(value), value_len)
            self._length = value_len
            self._is_null = 0


cdef class In_Varchar(Base_In_String):

    """VARCHAR input binding.

    The constructor takes 3 arguments:

    - ``who``: The object from which to read the value.
    - ``what``: The name of the parameter in the object to read.
    - ``max_size``: The maximum size of the string.  Attempting to input a
      string larger than this will raise ``OverflowError`` in the call to
      ``execute``.

    Note that `In_Varbinary` is an alias for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_VAR_STRING

In_Varbinary = In_Varchar

cdef class In_Char(Base_In_String):

    """CHAR input binding.

    The constructor takes 3 arguments:

    - ``who``: The object from which to read the value.
    - ``what``: The name of the parameter in the object to read.
    - ``max_size``: The maximum size of the string.  Attempting to input a
      string larger than this will raise ``OverflowError`` in the call to
      ``execute``.

    Note that `In_Binary` is an alias for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_STRING

In_Binary = In_Char

cdef class In_Enum(In_Varchar):

    """ENUM input binding.

    The constructor takes 3 arguments:

    - ``who``: The object from which to read the value.
    - ``what``: The name of the parameter in the object to read.
    - ``max_size``: The maximum size of the string.  Attempting to input a
      string larger than this will raise ``OverflowError`` in the call to
      ``execute``.

    The value may be a number or a string.
    """

    cdef set_value(self):
        cdef long value_len

        value = getattr(self._who, self._what, None)
        if value is None:
            self._length = 0
            self._is_null = 1
        else:
            if PyInt_Check(value) or PyLong_Check(value):
                value = str(value)
            value_len = PyString_Size(value)
            if value_len > self._buffer_length:
                raise OverflowError('Object length (%i) too large for buffer (%i).' % (value_len, self._buffer_length))
            memcpy(self._value, PyString_AsString(value), value_len)
            self._length = value_len
            self._is_null = 0


cdef class In_Set(In_Varchar):

    """SET input binding.

    - ``who``: The object from which to read the value.
    - ``what``: The name of the parameter in the object to read.
    - ``max_size``: The maximum size of the string.  Attempting to input a
      string larger than this will raise ``OverflowError`` in the call to
      ``execute``.

    The value may be:

    - A string.
    - A number (will be converted with ``str()``).
    - A dictionary, which will result in a comma-separated list of keys.
    - A set, which will result in a comma-separated list of values.
    - An object with a ``keys`` method, which will result in a comma seperated
      list of values from that method.
    """

    cdef set_value(self):
        cdef long value_len

        value = getattr(self._who, self._what, None)
        if value is None:
            self._length = 0
            self._is_null = 1
        else:
            if PyString_Check(value):
                value = value
            elif PyInt_Check(value) or PyLong_Check(value):
                value = str(value)
            elif PyDict_Check(value):
                value = ','.join(value.keys())
            elif PyList_Check(value) or PyTuple_Check(value):
                value = ','.join(value)
            elif isinstance(value, sets.Set):
                value = ','.join(tuple(value))
            elif hasattr(value, 'keys'):
                value = ','.join(value.keys())
            else:
                raise TypeError('Unsupported type %r' % (type(value),))
            value_len = PyString_Size(value)
            if value_len > self._buffer_length:
                raise OverflowError('Object length (%i) too large for buffer (%i).' % (value_len, self._buffer_length))
            memcpy(self._value, PyString_AsString(value), value_len)
            self._length = value_len
            self._is_null = 0


###############################################################################
# Streaming Character Input Bindings
###############################################################################

cdef class Input_Stream:

    """Input Stream.

    This is the object placed into your input binding that relays data to
    MySQL.
    """

    cdef extern_mysql.MYSQL_STMT * _stmt
    cdef unsigned int _param_num
    cdef object _raise_error
    cdef int _use_stream
    cdef Input_Stream _stream
    cdef int _sent_data
    cdef object _statement
    cdef Connection _connection
    cdef unsigned long long _max_size
    cdef unsigned long long _size

    cdef init(self, Connection connection, statement, extern_mysql.MYSQL_STMT * stmt, raise_error, unsigned int param_num, unsigned long long max_size):
        self._statement = statement
        self._stmt = stmt
        self._param_num = param_num
        self._raise_error = raise_error
        self._connection = connection
        self._max_size = max_size
        self._size = 0

    def write(self, data):
        """Write data to the input stream.

        **Note** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Parameters:
            - `data`: A string of data to write.

        :Exceptions:
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
            - `OverflowError`: The amount of data would exceed the column's
              maximum size.
        """
        cdef char * data_str
        cdef unsigned long data_len

        self._sent_data = 1

        PyString_AsStringAndSize(data, &data_str, <int *>&data_len)

        # XXX: Max size check won't work for LONGBLOB/LONGTEXT.
        # XXX: Also need to be careful about 64-bit platforms.
        if self._size + data_len > self._max_size:
            raise OverflowError

        self._connection._check_unbuffered_result(self._statement)
        if extern_mysql.mysql_stmt_send_long_data(self._stmt, self._param_num, data_str, data_len):
            self._raise_error()
        self._size = self._size + data_len


cdef class Base_In_Stream(Input_Bind):

    """Base class for streaming input.

    The constructor takes the following arguments:

    - ``who``: The object from which to read the value.
    - ``what``: The name of the parameter in the object to read.
    - ``use_stream``: If True, sets ``who.what`` to a stream object
      (`Input_Stream`) that has a ``write`` method.  If False, then it assumes
      the value is just a string.  Defaults to False.

    :IVariables:
        - `_stmt`: MYSQL_STMT structure.  (C only.)
        - `_param_num`: The parameter number in the statement.  (C only.)
        - `_raise_error`: A callable object that will raise the appropriate
          MySQL exception (from `mysql.stmt.Statement._raise_error`).  (C only.)
        - `_use_stream`: Whether or not to use a stream or just a string.  (C
          only.)
        - `_stream`: The `Input_Stream` instance.  This is created even if
          `_use_stream` is False, in which case the ``set_value`` method will
          call ``write`` for the user.  (C only.)
        - `_max_size`: The maximum size of the column (based on the column
          type).  (C only.)
    """

    cdef extern_mysql.MYSQL_STMT * _stmt
    cdef unsigned int _param_num
    cdef object _raise_error
    cdef int _use_stream
    cdef Input_Stream _stream
    cdef unsigned long long _max_size

    def __init__(self, who, what, int use_stream=0):
        Input_Bind.__init__(self, who, what)
        self._use_stream = use_stream

    cdef init(self, Connection connection, statement, extern_mysql.MYSQL_STMT * stmt, raise_error, unsigned int param_num):
        self._stream = Input_Stream()
        self._stream.init(connection, statement, stmt, raise_error, param_num, self._max_size)
        if self._use_stream:
            setattr(self._who, self._what, self._stream)

    cdef set_value(self):
        if self._use_stream:
            if self._stream._sent_data:
                self._is_null = 0
            else:
                self._is_null = 1
            self._stream._sent_data = 0
            self._stream._size = 0
        else:
            value = getattr(self._who, self._what, None)
            if value is None:
                self._is_null = 1
            else:
                self._is_null = 0
                try:
                    self._stream.write(value)
                except OverflowError:
                    self._stream._size = 0
                    raise
            self._stream._size = 0

cdef class In_Tiny_Blob(Base_In_Stream):

    """TINYBLOB input binding.

    The constructor takes the following arguments:

    - ``who``: The object from which to read the value.
    - ``what``: The name of the parameter in the object to read.
    - ``use_stream``: If True, sets ``who.what`` to a stream object
      (`Input_Stream`) that has a ``write`` method.  If False, then it assumes
      the value is just a string.  Defaults to False.

    Note that `In_Tiny_Text` is an alias for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_TINY_BLOB
        self._max_size = 256

cdef class In_Medium_Blob(Base_In_Stream):

    """MEDIUMBLOB input binding.

    The constructor takes the following arguments:

    - ``who``: The object from which to read the value.
    - ``what``: The name of the parameter in the object to read.
    - ``use_stream``: If True, sets ``who.what`` to a stream object
      (`Input_Stream`) that has a ``write`` method.  If False, then it assumes
      the value is just a string.  Defaults to False.

    Note that `In_Medium_Text` is an alias for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_MEDIUM_BLOB
        self._max_size = 65536

cdef class In_Blob(Base_In_Stream):

    """BLOB input binding.

    The constructor takes the following arguments:

    - ``who``: The object from which to read the value.
    - ``what``: The name of the parameter in the object to read.
    - ``use_stream``: If True, sets ``who.what`` to a stream object
      (`Input_Stream`) that has a ``write`` method.  If False, then it assumes
      the value is just a string.  Defaults to False.

    Note that `In_Text` is an alias for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_BLOB
        self._max_size = 16777216

cdef class In_Long_Blob(Base_In_Stream):

    """LONGBLOB input binding.

    The constructor takes the following arguments:

    - ``who``: The object from which to read the value.
    - ``what``: The name of the parameter in the object to read.
    - ``use_stream``: If True, sets ``who.what`` to a stream object
      (`Input_Stream`) that has a ``write`` method.  If False, then it assumes
      the value is just a string.  Defaults to False.

    Note that `In_Long_Text` is an alias for this object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_LONG_BLOB
        self._max_size = 4294967296

In_Tiny_Text = In_Tiny_Blob
In_Medium_Text = In_Medium_Blob
In_Text = In_Blob
In_Long_Text = In_Long_Blob

###############################################################################
# Numeric Input Bindings
###############################################################################

cdef class In_Tiny_Int(Input_Bind):

    """TINYINT input binding.

    The value should be an integer.
    """

    cdef char _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_TINY
        self._buffer = &self._value

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            self._value = <char> PyInt_AsLong(value)
            if self._value != value:
                raise OverflowError(value)
            self._is_null = 0

cdef class In_U_Tiny_Int(Input_Bind):

    """UNSIGNED TINYINT input binding.

    The value should be an integer.
    """

    cdef unsigned char _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_TINY
        self._buffer = &self._value
        self._is_unsigned = 1

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            self._value = <char> PyInt_AsLong(value)
            if self._value != value:
                raise OverflowError(value)
            self._is_null = 0

cdef class In_Bool(In_Tiny_Int):

    """BOOL input binding.

    The value should be an integer or bool.
    """

cdef class In_Small_Int(Input_Bind):

    """SMALLINT input binding.

    The value should be an integer.
    """

    cdef short int _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_SHORT
        self._buffer = &self._value

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            self._value = <short int> PyInt_AsLong(value)
            if self._value != value:
                raise OverflowError(value)
            self._is_null = 0

cdef class In_U_Small_Int(Input_Bind):

    """UNSIGNED SMALLINT input binding.

    The value should be an integer.
    """

    cdef unsigned short int _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_SHORT
        self._buffer = &self._value
        self._is_unsigned = 1

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            self._value = <short int> PyInt_AsLong(value)
            if self._value != value:
                raise OverflowError(value)
            self._is_null = 0

cdef class In_Medium_Int(Input_Bind):

    """MEDIUMINT input binding.

    The value should be an integer.
    """

    cdef int _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_LONG
        self._buffer = &self._value

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            self._value = PyInt_AsLong(value)
            if self._value != value or self._value > 8388607 or self._value < -8388608:
                raise OverflowError(value)
            self._is_null = 0

cdef class In_U_Medium_Int(Input_Bind):

    """UNSIGNED MEDIUMINT input binding.

    The value should be an integer.
    """

    cdef unsigned int _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_LONG
        self._buffer = &self._value
        self._is_unsigned = 1

    cdef set_value(self):
        cdef object test_value

        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            self._value = PyInt_AsLong(value)
            if self._value > 16777215 or self._value < 0:
                raise OverflowError(value)
            # Pyrex doesn't seem to know that "unsigned int" will not always
            # convert to a Python integer, so we'll need to write this check
            # manually.
            #
            # This check probably isn't necessary since we are doing explicit
            # conversion above.
            test_value = PyLong_FromUnsignedLong(self._value)
            if test_value != value:
                raise OverflowError(value)
            self._is_null = 0

cdef class In_Int(Input_Bind):

    """INT input binding.

    The value should be an integer.
    """

    cdef int _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_LONG
        self._buffer = &self._value

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            self._value = PyInt_AsLong(value)
            if self._value != value:
                raise OverflowError(value)
            self._is_null = 0

cdef class In_U_Int(Input_Bind):

    """UNSIGNED INT input binding.

    The value should be an integer.
    """

    cdef unsigned int _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_LONG
        self._buffer = &self._value
        self._is_unsigned = 1

    cdef set_value(self):
        cdef object test_value

        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            if PyInt_Check(value):
                self._value = PyInt_AsLong(value)
            elif PyLong_Check(value):
                self._value = PyLong_AsUnsignedLong(value)
            else:
                raise TypeError('an integer is required')
            # Pyrex doesn't seem to know that "unsigned int" will not always
            # convert to a Python integer, so we'll need to write this check
            # manually.
            #
            # This check probably isn't necessary since we are doing explicit
            # conversion above.
            test_value = PyLong_FromUnsignedLong(self._value)
            if test_value != value:
                raise OverflowError(value)
            self._is_null = 0

cdef class In_Big_Int(Input_Bind):

    """BIGINT input binding.

    The value should be an integer.
    """

    cdef long long _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_LONGLONG
        self._buffer = &self._value

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            self._value = PyLong_AsLongLong(value)
            if self._value != value:
                raise OverflowError(value)
            self._is_null = 0


cdef class In_U_Big_Int(Input_Bind):

    """UNSIGNED BIG INT input binding.

    The value should be an integer.
    """

    cdef unsigned long long _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_LONGLONG
        self._buffer = &self._value
        self._is_unsigned = 1

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            if PyInt_Check(value):
                self._value = <unsigned long long> PyInt_AsUnsignedLongMask(value)
            elif PyLong_Check(value):
                self._value = PyLong_AsUnsignedLongLong(value)
            else:
                raise TypeError('an integer is required')
            if self._value != value:
                raise OverflowError(value)
            self._is_null = 0

cdef class In_Float(Input_Bind):

    """FLOAT input binding.

    The value should be a floating point number.

    Note that there is no overflow checking.
    """

    cdef float _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_FLOAT
        self._buffer = &self._value

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            self._value = <float> PyFloat_AsDouble(value)
            self._is_null = 0

cdef class In_U_Float(Input_Bind):

    """UNSIGNED FLOAT input binding.

    The value should be a floating point number.

    Note that there is no overflow checking (except it will raise OverflowError
    on negative values).
    """

    cdef float _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_FLOAT
        self._buffer = &self._value
        self._is_unsigned = 1

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            if value < 0:
                raise OverflowError(value)
            self._value = <float> PyFloat_AsDouble(value)
            self._is_null = 0

cdef class In_Double(Input_Bind):

    """DOUBLE input binding.

    The value should be a floating point number.
    """

    cdef double _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_DOUBLE
        self._buffer = &self._value

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            self._value = PyFloat_AsDouble(value)
            self._is_null = 0

cdef class In_U_Double(Input_Bind):

    """UNSIGNED DOUBLE input binding.

    The value should be a floating point number.
    """

    cdef double _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_DOUBLE
        self._buffer = &self._value
        self._is_unsigned = 1

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            if value < 0:
                raise OverflowError(value)
            self._value = PyFloat_AsDouble(value)
            self._is_null = 0


cdef class In_Bit(Input_Bind):

    """BIT input binding.

    The value should be an integer.
    """

    cdef unsigned char * _value

    def __init__(self, who, what):
        self._value = <unsigned char *> PyMem_Malloc(8)
        self._buffer = self._value
        self._buffer_length = 8
        Input_Bind.__init__(self, who, what)

    def __dealloc__(self):
        PyMem_Free(self._value)

    def __new__(self, *args, **kwargs):
        # For now, MySQL doesn't have direct support for the BIT type.
        # What's odd is that mysql_stmt_bind_result does support BIT.
        self._buffer_type = extern_mysql.MYSQL_TYPE_STRING

    cdef set_value(self):
        cdef unsigned long int32
        cdef unsigned long long int64

        value = getattr(self._who, self._what, None)
        if value is None:
            self._length = 0
            self._is_null = 1
        else:
            self._is_null = 0
            # XXX: This does not work on 64-bit platforms.
            if PyInt_CheckExact(value):
                int32 = PyInt_AsUnsignedLongMask(value)
                self._value[3] = int32
                int32 = int32 >> 8
                self._value[2] = int32
                int32 = int32 >> 8
                self._value[1] = int32
                int32 = int32 >> 8
                self._value[0] = int32
                self._length = 4
            elif PyLong_CheckExact(value):
                int64 = PyLong_AsUnsignedLongLong(value)
                self._value[7] = int64
                int64 = int64 >> 8
                self._value[6] = int64
                int64 = int64 >> 8
                self._value[5] = int64
                int64 = int64 >> 8
                self._value[4] = int64
                int64 = int64 >> 8
                self._value[3] = int64
                int64 = int64 >> 8
                self._value[2] = int64
                int64 = int64 >> 8
                self._value[1] = int64
                int64 = int64 >> 8
                self._value[0] = int64
                self._length = 8
            else:
                raise TypeError('Type must be an int or long for bit field, was %s.' % (type(value),))

###############################################################################
# Decimal Input Bindings
###############################################################################

cdef class Base_Decimal(Input_Bind):

    """Signed Decimal input binding.

    Warning: Decimal input binding is broken in server versions 5.0.18 and
    older.  See http://bugs.mysql.com/bug.php?id=16511

    The value must be a ``decimal.Decimal`` object.

    :IVariables:
        - `_value`:  The value as a string (in base-10).  (C only.)
        - `_allow_negative`: Set to true in `In_U_Decimal`.  (C only.)
    """

    cdef char * _value
    cdef int _allow_negative

    def __init__(self, who, what):
        # Maximum digits is 65
        # Plus 1 for decimal point and sign.
        self._value = <char *> PyMem_Malloc(67)
        self._buffer = self._value
        self._buffer_length = 67
        Input_Bind.__init__(self, who, what)

    def __dealloc__(self):
        PyMem_Free(self._value)

    cdef set_value(self):
        cdef long value_len

        value = getattr(self._who, self._what, None)
        if value is None:
            self._length = 0
            self._is_null = 1
        else:
            if not isinstance(value, decimal.Decimal):
                raise TypeError('Value must be a Decimal instance, was %r' % (type(value),))
            if not self._allow_negative and value.as_tuple()[0]:
                raise OverflowError('Value may not be negative.')

            s = str(value)

            value_len = PyString_Size(s)
            if value_len > self._buffer_length:
                raise OverflowError('Object length (%i) too large for buffer (%i).' % (value_len, self._buffer_length))
            memcpy(self._value, PyString_AsString(s), value_len)
            self._length = value_len
            self._is_null = 0

cdef class In_Decimal(Base_Decimal):

    """Signed Decimal input binding.

    Warning: Decimal input binding is broken in server versions 5.0.18 and
    older.  See http://bugs.mysql.com/bug.php?id=16511

    The value must be a ``decimal.Decimal`` object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_DECIMAL
        self._allow_negative = 1


cdef class In_U_Decimal(Base_Decimal):

    """Unsigned Decimal input binding.

    Warning: Decimal input binding is broken in server versions 5.0.18 and
    older.  See http://bugs.mysql.com/bug.php?id=16511

    The value must be a ``decimal.Decimal`` object.  Raises ``OverflowError``
    when ``execute`` is called if the value is negative.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_DECIMAL
        self._allow_negative = 0

cdef class In_New_Decimal(Base_Decimal):

    """Signed "new" decimal input binding.

    This is currently implemented exactly the same as `In_Decimal` using the
    ``MYSQL_TYPE_NEWDECIMAL`` field type.  It is currently not known if this
    actually causes any different behavior in the server.

    Warning: Decimal input binding is broken in server versions 5.0.18 and
    older.  See http://bugs.mysql.com/bug.php?id=16511

    The value must be a ``decimal.Decimal`` object.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_NEWDECIMAL
        self._allow_negative = 1


cdef class In_U_New_Decimal(Base_Decimal):

    """Unsigned "new" decimal input binding.

    This is currently implemented exactly the same as `In_Decimal` using
    the ``MYSQL_TYPE_NEWDECIMAL`` field type.  It is currently not known
    if this actually causes any different behavior in the server.

    Warning: Decimal input binding is broken in server versions 5.0.18 and
    older.  See http://bugs.mysql.com/bug.php?id=16511

    The value must be a ``decimal.Decimal`` object.  Raises ``OverflowError``
    when ``execute`` is called if the value is negative.
    """

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_NEWDECIMAL
        self._allow_negative = 0


###############################################################################
# Time Input Bindings
###############################################################################

cdef class In_Timestamp(Input_Bind):

    """TIMESTAMP input binding.

    The value should be a ``datetime.datetime`` object.
    """

    cdef extern_mysql.MYSQL_TIME _ts

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_TIMESTAMP
        self._buffer = &self._ts

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._is_null = 1
        else:
            if not isinstance(value, datetime.datetime):
                raise TypeError('Value must be a datetime instance, was %r.' % (type(value),))
            self._ts.year = value.year
            self._ts.month = value.month
            self._ts.day = value.day
            self._ts.hour = value.hour
            self._ts.minute = value.minute
            self._ts.second = value.second
            self._ts.second_part = value.microsecond
            self._ts.neg = 0
            self._is_null = 0

cdef class In_Date(Input_Bind):

    """DATE input binding.

    The value should be a ``datetime.date`` object.
    """

    cdef extern_mysql.MYSQL_TIME _ts

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_DATE
        self._buffer = &self._ts

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._is_null = 1
        else:
            if not isinstance(value, datetime.date):
                raise TypeError('Value must be a date instance, was %r.' % (type(value),))
            self._ts.year = value.year
            self._ts.month = value.month
            self._ts.day = value.day
            self._ts.neg = 0
            self._is_null = 0

cdef class In_Time(Input_Bind):

    """TIME input binding.

    The value should be a ``datetime.time`` or ``datetime.timedelta`` object.
    """

    cdef extern_mysql.MYSQL_TIME _ts

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_TIME
        self._buffer = &self._ts

    cdef set_value(self):
        cdef unsigned int hours
        cdef unsigned int minutes
        cdef unsigned int seconds

        value = getattr(self._who, self._what, None)
        if value is None:
            self._is_null = 1
        else:
            self._is_null = 0
            if isinstance(value, datetime.time):
                self._ts.hour = value.hour
                self._ts.minute = value.minute
                self._ts.second = value.second
                self._ts.second_part = value.microsecond
                self._ts.neg = 0
            elif isinstance(value, datetime.timedelta):
                # Need to denormalize the normalization done by the timedelta
                # object.
                #
                # - days   Between -999999999 and 999999999 inclusive
                # - seconds   Between 0 and 86399 inclusive
                # - microseconds  Between 0 and 999999 inclusive
                #
                # '-838:59:59' to '838:59:59'

                if value.days < 0:
                    value = -value
                    self._ts.neg = 1
                else:
                    self._ts.neg = 0

                hours = PyInt_AsLong(value.days)*24 + PyInt_AsLong(value.seconds)/3600

                if hours > 838:
                    raise OverflowError('Time value is too large.')
                minutes = (PyInt_AsLong(value.seconds) % 3600) / 60
                seconds = PyInt_AsLong(value.seconds) % 60

                self._ts.hour = hours
                self._ts.minute = minutes
                self._ts.second = seconds
                self._ts.second_part = value.microseconds
            else:
                raise TypeError('Value must be a time or timedelta instance, was %r.' % (type(value),))

cdef class In_Date_Time(Input_Bind):

    """DATETIME input binding.

    The value should be a ``datetime.datetime`` object.
    """

    cdef extern_mysql.MYSQL_TIME _ts

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_DATETIME
        self._buffer = &self._ts

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._is_null = 1
        else:
            if not isinstance(value, datetime.datetime):
                raise TypeError('Value must be a datetime instance, was %r.' % (type(value),))
            self._ts.year = value.year
            self._ts.month = value.month
            self._ts.day = value.day
            self._ts.hour = value.hour
            self._ts.minute = value.minute
            self._ts.second = value.second
            self._ts.second_part = value.microsecond
            self._ts.neg = 0
            self._is_null = 0

cdef class In_Year(Input_Bind):

    """YEAR input binding.

    The value should be an integer.
    """

    cdef short int _value

    def __new__(self, *args, **kwargs):
        self._buffer_type = extern_mysql.MYSQL_TYPE_SHORT
        self._buffer = &self._value

    cdef set_value(self):
        value = getattr(self._who, self._what, None)
        if value is None:
            self._value = 0
            self._is_null = 1
        else:
            self._value = <short int> PyInt_AsLong(value)
            if self._value != value:
                raise OverflowError(value)
            self._is_null = 0
