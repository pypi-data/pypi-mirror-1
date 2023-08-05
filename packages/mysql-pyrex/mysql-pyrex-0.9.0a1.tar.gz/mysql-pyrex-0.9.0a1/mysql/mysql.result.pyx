# $Header: /home/cvs2/mysql/mysql/mysql.result.pyx,v 1.6 2006/08/26 20:19:51 ehuss Exp $
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

"""Result object for SQL queries.

The `Result` object is the result of the `mysql.connection.Connection.execute`
method for SELECT-like queries.

There are also some objects (`Row_Offset` and `Field`) defined in this module
that are returned by the Result object.  These are described in more detail
in the Result methods.
"""

include "python.pxi"
include "util/inline.pyx"

import mysql.exceptions

cdef class Row_Offset:

    """Representation of a result offset.

    This is an opaque object used by the `mysql.result.Result.row_tell`,
    `mysql.stmt.Statement.row_tell`, `mysql.result.Result.row_seek`, and
    `mysql.stmt.Statement.row_seek` methods.

    :IVariables:
        - `_offset`: The MYSQL_ROW_OFFSET structure (C only).
    """


class Field:

    """The description of a column in a SELECT query.

    :IVariables:
        - `name`: The name of the field.  If the field was given an alias with
          an AS clause, the value of name is the alias.
        - `org_name`: The name of the field.  Aliases are ignored.
        - `table`: The name of the table containing this field, if it isn't a
          calculated field. For calculated fields, the table value is an empty
          string. If the table was given an alias with an AS clause, the value
          of table is the alias.
        - `org_table`: The name of the table.  Aliases are ignored.
        - `db`: The name of the database that the field comes from. If the
          field is a calculated field, db is an empty string.
        - `catalog`: The catalog name. This value is always "def".
        - `default`: The default value of this field. This is currently always
          None.
        - `length`: The width of the field, as specified in the table
          definition.  For integers, this is the space required to store the
          value as a string.  For BLOB or TEXT fields, it is the maximum size
          of the field.
        - `max_length`: The maximum width of the field for the result set (the
          length of the longest field value for the rows actually in the result
          set).  For integers, this is the space required to store the value as
          a string.

          If you use set ``store_result`` to True, this contains the maximum
          length for the field. Otherwise the value of this variable is zero.

          For statements, this is not set unless
          `mysql.stmt.Statement.set_update_max_length` is called on the
          statement object.
        - `flags`: Different bit-flags for the field. The flags value may have
          zero or more bits set that are defined in
          `mysql.constants.field_flags`.
        - `decimals`: The number of decimals for numeric fields.
        - `charset_number`: The character set number for the field.
        - `type`: The type of the field (from `mysql.constants.field_types`).
    """

    name = ''
    org_name = ''
    table = ''
    org_table = ''
    db = ''
    catalog = ''
    default = ''
    length = 0
    max_length = 0
    flags = 0
    decimals = 0
    charset_number = 0
    type = 0

    def is_not_null(self):
        """Determine if this is a NOT NULL column.

        :Return:
            Returns True if this column is defined NOT NULL.
            Returns False if the column allows NULLs.
        """
        return bool(extern_mysql.IS_NOT_NULL(self.flags))

    def is_primary_key(self):
        """Determine if this column has a primary key.

        :Return:
            Returns True if this column is a primary key, False if not.
        """
        return bool(extern_mysql.IS_PRI_KEY(self.flags))

    def is_numeric(self):
        """Determine if this column is a numeric type.

        :Return:
            Returns True if this column is a numeric type, False otherwise.
        """
        return bool(extern_mysql.IS_NUM(self.type))

    def __repr__(self):
        return '<Field name=%r org_name=%r table=%r org_table=%r db=%r \
catalog=%r default=%r length=%r max_length=%r flags=%r decimals=%r \
charset_number=%r type=%r>' % (self.name, self.org_name, self.table,
self.org_table, self.db, self.catalog, self.default, self.length,
self.max_length, self.flags, self.decimals, self.charset_number, self.type)


cdef class Result:

    """Query result object.

    This object provides a method to retrieve the results from a query
    using the `mysql.connection.Connection.execute` method.

    Typically you call `fetch_row` until it raises
    `mysql.exceptions.No_More_Rows` to retrieve the data.  You can also iterate
    over the result object to retrieve the data, or call `fetch_all_rows` to
    fetch all the data at once.

    The type of data returned depends on the field type and the conversion
    routines defined when you created the `mysql.connection.Connection` object.
    See `mysql.conversion` for more detail about data conversion and the
    default conversions available.

    If you specified ``store_result`` as False (the default) to the ``execute``
    method, then the results are buffered on the server side.  You can have
    only 1 live Result object per connection in this case.  If you attempt to
    create another result object, then your old result object will be
    forcefully closed.

    Attempting to access the result object after it is closed will result in
    raising `mysql.exceptions.Result_Closed_Error`.  Attempting to access the
    result object after the connection is closed will result in raising
    `mysql.exceptions.Not_Connected_Error`.

    The ``__len__`` method is also implemented, but you should read the
    `num_rows` docstring for limitations.

    """

    cdef _init(self, extern_mysql.MYSQL * db,
                     object connection,
                     extern_mysql.MYSQL_RES * result,
                     int stored):
        self._db = db
        self._result = result
        self._connection = connection
        self._stored = stored

    def __dealloc__(self):
        if self._result != NULL:
            extern_mysql.mysql_free_result(self._result)

    def __len__(self):
        return self.num_rows()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.fetch_row()
        except mysql.exceptions.No_More_Rows:
            raise StopIteration

    cdef _check_store_result(self):
        """Check if the result is stored.

        :Exceptions:
            - `mysql.exceptions.Result_Unbuffered_Error`: The result has not be
              stored locally.
            - `mysql.exceptions.Result_Closed_Error`: `close` has been called
              on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        if self._result == NULL:
            raise mysql.exceptions.Result_Closed_Error
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if not self._stored:
            raise mysql.exceptions.Result_Unbuffered_Error

    def close(self):
        """Release the internally buffered result data.

        This will release any internally held information about the result.
        This will render the result object useless.

        This is automatically called when the object is deleted.

        If the result is already closed, this does nothing.

        Further attempts to use the result object will raise
        `mysql.exceptions.Result_Closed_Error`.
        """
        if self._result != NULL:
            extern_mysql.mysql_free_result(self._result)
            self._result = NULL
        self._db = NULL
        self._connection = None

    def closed(self):
        """Check if the result is closed.

        This can be used to check if the result has been closed with the
        `close` method.  This is the only method you may call (besides `close`)
        on a closed Result object.

        :Return:
            Returns True if this Result object is closed, False if it is still
            live.
        """
        return self._result == NULL

    def row_tell(self):
        """Indicate the current row position.

        **Note** This is only available if the result was stored by passing
        True to the ``store_result`` parameter in the ``execute`` call.

        It returns an opaque object to be used with `row_seek`.

        :Exceptions:
            - `mysql.exceptions.Result_Unbuffered_Error`: The result is in
              unbuffered mode (``store_result`` was set to False).
            - `mysql.exceptions.Commands_Out_Of_Sync`: Commands were executed
              in an improper order.
            - `mysql.exceptions.Out_Of_Memory`: Out of memory.
            - `mysql.exceptions.Server_Gone_Error`: The MySQL server has gone
              away.
            - `mysql.exceptions.Server_Lost`: The connection to the server was
              lost during the query.
            - `mysql.exceptions.Unknown_Error`: An unknown error occurred.
            - `mysql.exceptions.Result_Closed_Error`: `close` has been called
              on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef Row_Offset offset

        self._check_store_result()

        offset = Row_Offset()
        offset._offset = extern_mysql.mysql_row_tell(self._result)
        return offset

    def row_seek(self, offset):
        """Set the current row position.

        **Note** This is only available if the result was stored by passing
        True to the ``store_result`` parameter in the ``execute`` call.

        :Parameters:
            - `offset`: An offset object returned from `row_tell` or an integer
              of an explicit row number (starting at zero).  If it is a number,
              it must be a number from 0 to ``num_rows()-1``.

        :Return:
            Returns the previous row offset as an opaque object.

        :Exceptions:
            - `mysql.exceptions.Result_Unbuffered_Error`: The result is in
              unbuffered mode (``store_result`` was set to False).
            - `mysql.exceptions.Commands_Out_Of_Sync`: Commands were executed
              in an improper order.
            - `mysql.exceptions.Out_Of_Memory`: Out of memory.
            - `mysql.exceptions.Server_Gone_Error`: The MySQL server has gone
              away.
            - `mysql.exceptions.Server_Lost`: The connection to the server was
              lost during the query.
            - `mysql.exceptions.Unknown_Error`: An unknown error occurred.
            - `mysql.exceptions.Result_Closed_Error`: `close` has been called
              on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef Row_Offset old_offset
        cdef Row_Offset new_offset
        cdef extern_mysql.my_ulonglong int_off

        self._check_store_result()

        old_offset = Row_Offset()
        if isinstance(offset, Row_Offset):
            new_offset = <Row_Offset> offset
            old_offset._offset = extern_mysql.mysql_row_seek(self._result, new_offset._offset)
        else:
            old_offset._offset = extern_mysql.mysql_row_tell(self._result)
            if PyInt_Check(offset):
                int_off = PyInt_AsLong(offset)
            elif PyLong_Check(offset):
                int_off = PyLong_AsUnsignedLongLong(offset)
            else:
                int_off = PyLong_AsUnsignedLongLong(long(offset))
            extern_mysql.mysql_data_seek(self._result, int_off)
        return old_offset

    def fetch_row(self):
        """Return one row from the result.

        :Return:
            Returns a tuple that is the row values.

        :Exceptions:
            - `mysql.exceptions.No_More_Rows`: There are no more rows left.
            - `mysql.exceptions.Commands_Out_Of_Sync`: Commands were executed
              in an improper order.
            - `mysql.exceptions.Out_Of_Memory`: Out of memory.
            - `mysql.exceptions.Server_Gone_Error`: The MySQL server has gone
              away.
            - `mysql.exceptions.Server_Lost`: The connection to the server was
              lost during the query.
            - `mysql.exceptions.Unknown_Error`: An unknown error occurred.
            - `mysql.exceptions.Result_Closed_Error`: `close` has been called
              on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef extern_mysql.MYSQL_ROW row
        cdef extern_mysql.MYSQL_FIELD * fields
        cdef unsigned long * lengths
        cdef object result
        cdef unsigned int num_fields
        cdef unsigned int i
        cdef object value
        cdef extern_mysql.enum_field_types field_type

        if self._result == NULL:
            raise mysql.exceptions.Result_Closed_Error
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error

        row = extern_mysql.mysql_fetch_row(self._result)
        if row == NULL:
            if extern_mysql.mysql_errno(self._db) == 0:
                # No more data.
                raise mysql.exceptions.No_More_Rows
            else:
                self._connection._raise_error()

        lengths = extern_mysql.mysql_fetch_lengths(self._result)
        if lengths == NULL:
            self._connection._raise_error()

        num_fields = extern_mysql.mysql_num_fields(self._result)

        result = PyTuple_New(num_fields)

        fields = extern_mysql.mysql_fetch_fields(self._result)
        if fields == NULL:
            # May not be necessary to check since num_fields will probably be
            # zero.
            raise MemoryError

        for i from 0 <= i < num_fields:
            if row[i] == NULL:
                Py_INCREF(None)
                PyTuple_SET_ITEM(result, i, None)
            else:
                value = PyString_FromStringAndSize(row[i], lengths[i])
                # Work around MySQL bug #17758.  Enum and Sets are not returned
                # as the correct type.  This may be changed in the future.
                field_type = fields[i].type
                if field_type == extern_mysql.MYSQL_TYPE_STRING:
                    if fields[i].flags & extern_mysql.ENUM_FLAG:
                        field_type = extern_mysql.MYSQL_TYPE_ENUM
                    elif fields[i].flags & extern_mysql.SET_FLAG:
                        field_type = extern_mysql.MYSQL_TYPE_SET
                value = self._connection._convert_out.convert(field_type, value)
                Py_INCREF(value)
                PyTuple_SET_ITEM(result, i, value)

        return result

    def fetch_all_rows(self):
        """Return all remaining rows in the result.

        This will return a list of rows (each row being a tuple itself).

        :Return:
            Returns a list of rows.
            Returns an empty list if there are no more rows.

        :Exceptions:
            - `mysql.exceptions.Commands_Out_Of_Sync`: Commands were executed
              in an improper order.
            - `mysql.exceptions.Out_Of_Memory`: Out of memory.
            - `mysql.exceptions.Server_Gone_Error`: The MySQL server has gone
              away.
            - `mysql.exceptions.Server_Lost`: The connection to the server was
              lost during the query.
            - `mysql.exceptions.Unknown_Error`: An unknown error occurred.
            - `mysql.exceptions.Result_Closed_Error`: `close` has been called
              on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        result = []

        while 1:
            try:
                row = self.fetch_row()
            except mysql.exceptions.No_More_Rows:
                break
            result.append(row)

        return result

    def fetch_container(self, container):
        """Fetch one row of data into a container.

        This will fetch one row of data.  It will set the output of each
        column into the container using ``setattr``.

        If a column name is aliased with "AS", then the aliased name will be
        used for setting the value in the container.

        :Parameters:
            - `container`: The object to set the output into.

        :Exceptions:
            - `mysql.exceptions.No_More_Rows`: There are no more rows left.
            - `mysql.exceptions.Commands_Out_Of_Sync`: Commands were executed
              in an improper order.
            - `mysql.exceptions.Out_Of_Memory`: Out of memory.
            - `mysql.exceptions.Server_Gone_Error`: The MySQL server has gone
              away.
            - `mysql.exceptions.Server_Lost`: The connection to the server was
              lost during the query.
            - `mysql.exceptions.Unknown_Error`: An unknown error occurred.
            - `mysql.exceptions.Result_Closed_Error`: `close` has been called
              on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef int num_fields
        cdef int i
        cdef extern_mysql.MYSQL_FIELD * fields

        row = self.fetch_row()
        num_fields = extern_mysql.mysql_num_fields(self._result)
        fields = extern_mysql.mysql_fetch_fields(self._result)
        for i from 0 <= i < num_fields:
            setattr(container, fields[i].name, row[i])

    def num_rows(self):
        """Return the number of rows in the result.

        **Note** The behavior of this method depends on whether
        ``store_result`` was set in the call to ``execute``.  If
        ``store_result`` was False, then this only returns the correct result
        after all the rows have been fetched.  If it was True, then it will
        always return the correct result.

        :Return:
            Returns the number of rows in the result.

        :Exceptions:
            - `mysql.exceptions.Commands_Out_Of_Sync`: Commands were executed
              in an improper order.
            - `mysql.exceptions.Out_Of_Memory`: Out of memory.
            - `mysql.exceptions.Server_Gone_Error`: The MySQL server has gone
              away.
            - `mysql.exceptions.Server_Lost`: The connection to the server was
              lost during the query.
            - `mysql.exceptions.Unknown_Error`: An unknown error occurred.
            - `mysql.exceptions.Result_Closed_Error`: `close` has been called
              on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        try:
            self._check_store_result()
        except mysql.exceptions.Result_Unbuffered_Error:
            pass
        return _minimal_ulonglong(extern_mysql.mysql_num_rows(self._result))

    def num_fields(self):
        """Returns the number of fields in the result.

        :Return:
            Returns an integer of the number of fields.

        :Exceptions:
            - `mysql.exceptions.Commands_Out_Of_Sync`: Commands were executed
              in an improper order.
            - `mysql.exceptions.Out_Of_Memory`: Out of memory.
            - `mysql.exceptions.Server_Gone_Error`: The MySQL server has gone
              away.
            - `mysql.exceptions.Server_Lost`: The connection to the server was
              lost during the query.
            - `mysql.exceptions.Unknown_Error`: An unknown error occurred.
            - `mysql.exceptions.Result_Closed_Error`: `close` has been called
              on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        if self._result == NULL:
            raise mysql.exceptions.Result_Closed_Error
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error

        return extern_mysql.mysql_num_fields(self._result)

    def fields(self):
        """Return all field types.

        :Return:
            Returns a list of `Field` instances that describe the columns in a
            query.

        :Exceptions:
            - `mysql.exceptions.Commands_Out_Of_Sync`: Commands were executed
              in an improper order.
            - `mysql.exceptions.Out_Of_Memory`: Out of memory.
            - `mysql.exceptions.Server_Gone_Error`: The MySQL server has gone
              away.
            - `mysql.exceptions.Server_Lost`: The connection to the server was
              lost during the query.
            - `mysql.exceptions.Unknown_Error`: An unknown error occurred.
            - `mysql.exceptions.Result_Closed_Error`: `close` has been called
              on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef extern_mysql.MYSQL_FIELD * fields
        cdef int i
        cdef int num_fields
        cdef object result

        if self._result == NULL:
            raise mysql.exceptions.Result_Closed_Error
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error

        fields = extern_mysql.mysql_fetch_fields(self._result)
        if fields == NULL:
            # May not be necessary to check since num_fields will probably be
            # zero.
            raise MemoryError
        num_fields = extern_mysql.mysql_num_fields(self._result)
        result = PyTuple_New(num_fields)
        for i from 0 <= i < num_fields:
            field = Field()
            field.name = PyString_FromStringAndSize(fields[i].name, fields[i].name_length)
            field.org_name = PyString_FromStringAndSize(fields[i].org_name, fields[i].org_name_length)
            field.table = PyString_FromStringAndSize(fields[i].table, fields[i].table_length)
            field.org_table = PyString_FromStringAndSize(fields[i].org_table, fields[i].org_table_length)
            field.db = PyString_FromStringAndSize(fields[i].db, fields[i].db_length)
            field.catalog = PyString_FromStringAndSize(fields[i].catalog, fields[i].catalog_length)
            if fields[i].default == NULL:
                field.default = None
            else:
                default = PyString_FromStringAndSize(fields[i].default, fields[i].def_length)
                field.default = self._connection._convert_out.convert(fields[i].type, default)
            field.length = fields[i].length
            field.max_length = fields[i].max_length
            field.flags = fields[i].flags
            field.decimals = fields[i].decimals
            field.charset_number = fields[i].charsetnr
            field.type = fields[i].type
            Py_INCREF(field)
            PyTuple_SET_ITEM(result, i, field)
        return result
