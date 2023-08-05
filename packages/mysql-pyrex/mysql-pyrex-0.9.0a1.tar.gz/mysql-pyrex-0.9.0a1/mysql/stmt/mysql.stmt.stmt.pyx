# $Header: /home/cvs2/mysql/mysql/stmt/mysql.stmt.stmt.pyx,v 1.7 2006/08/26 21:30:47 ehuss Exp $
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

"""MySQL Statement object.

The Statement object represents a parsed SQL statement on the server.

The Statement object is put into the top-level of the `mysql.stmt` subpackage
for convenience.
"""

# XXX:
# - Pyrex doesn't seem to like cyclical cimport.  Thus, creating bind_in and
#   bind_out objects requires passing everything from inside the Statement
#   object that the Bind objects need (rather than passing "self" as a
#   parameter).  This also means that Statement._raise_error needs to be a
#   Python method rather than a C function (which is what I would have
#   preferred it to be).

__version__ = '$Revision: 1.7 $'

include "../python.pxi"
include "../libc.pxi"
include "../util/inline.pyx"

import mysql.exceptions
cimport mysql.result
cimport bind_in
cimport bind_out
# XXX: Working around bug with sizeof function.
from extern_mysql cimport MYSQL_BIND
from bind_out import Base_Out_Stream

cdef class Statement:

    """Parsed SQL statement object.

    This object represents a parsed statement on the server-side. It provides
    the ability to efficiently re-execute the same SQL statement.

    Statement objects should only be created by the
    `mysql.connection.Connection.new_statement` method.

    **Note** Creating a new Statement object will close any live unbuffered
    result objects and reset any live statement objects.

    Note that when deleting a Statement object the system may delay deleting
    the actual structure stored on the server-side if you have not explicitly
    called `close`.  This is because the `close` method requires communicating
    with the server, and if you are in the middle of an unbuffered fetch, it
    would reset the state of the connection.  The Statement object may be
    involved in a reference cycle, and thus would only get removed by the
    garbage collector which can fire at unexpected times.  It accomplishes this
    by putting the MySQL data structure into a special holding area in the
    Connection object, which is checked periodically at safe opportunities.

    :IVariables:
        - `_stmt`: MYSQL_STMT structure.  May be NULL.  (C only.)
        - `_stored`:  Whether or not the result was stored in the execute
          method.  (C only.)
        - `_input_binds`: List or tuple of `mysql.stmt.bind_in.Input_Bind`
          instances. (C only.)
        - `_output_binds`: List or tuple of `mysql.stmt.bind_out.Output_Bind`
          instances. (C only.)
        - `_connection`: Reference to the connection that created this
          statement.  (Read only.)
        - `_old_statements`: The `mysql.connection._Statement_Cleaner` instance
          from the connection object.  We hold a local refernce to this object
          because the connection and statement objects are involved in a cycle,
          and thus we can't rely on the _connection object existing during
          dealloc.
    """

    def __init__(self, Connection connection, object query):
        cdef char * query_str
        cdef int query_len

        self._connection = connection
        self._old_statements = connection._old_statements
        self._connection._check_unbuffered_result(None)
        self._stmt = extern_mysql.mysql_stmt_init(connection._db)
        if self._stmt == NULL:
            raise MemoryError

        self._input_binds = []
        self._output_binds = []

        query_str = PyString_AsString(query)
        query_len = PyString_Size(query)

        if extern_mysql.mysql_stmt_prepare(self._stmt, query_str, query_len):
            self._raise_error()

    def __dealloc__(self):
        if self._stmt != NULL:
            # Garbage collector will call clear which sets all items to None.
            if self._old_statements is None:
                # I believe this is always safe because old_statements will
                # only be None if the connection is already gone or is going
                # away.
                extern_mysql.mysql_stmt_close(self._stmt)
            else:
                # Defer dealloc until later because this might cause communication
                # over the connection which would reset its state.
                self._old_statements.add_reference(self._stmt)

    def _raise_error(self):
        """Raise a statement-API error."""
        cdef unsigned int errno
        cdef char * err_str
        if self._stmt == NULL:
            # This should never happen.
            raise mysql.exceptions.Statement_Closed_Error
        errno = extern_mysql.mysql_stmt_errno(self._stmt)
        err_str = extern_mysql.mysql_stmt_error(self._stmt)
        raise mysql.exceptions.raise_error(errno, err_str)

    cdef _check_store_result(self):
        """Check if the result was stored.

        Raises the appropriate exception if the result was stored.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
            - `mysql.exceptions.Result_Unbuffered_Error`: The result is in
              unbuffered mode (``store_result`` was set to False).
        """
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error
        if not self._stored:
            raise mysql.exceptions.Result_Unbuffered_Error

    def close(self):
        """Close the statement object, releasing any internally held memory.

        This will render this Statement object useless.

        This is automatically called when the object is deleted.

        If the result is already closed, this does nothing.

        Further attempts to use the result object will raise
        `mysql.exceptions.Statement_Closed_Error`.

        **Note** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Exceptions:
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        if self._stmt != NULL:
            self._connection._check_unbuffered_result(None)
            extern_mysql.mysql_stmt_close(self._stmt)
            self._stmt = NULL

    def closed(self):
        """Check if the statement is closed.

        This can be used to check if the statement has been closed with the
        `close` method.  This is the only method you may call (besides `close`)
        on a closed Statement object.

        :Return:
            Returns True if this Statement object is closed, False if it is still
            live.
        """
        return self._stmt == NULL

    def get_param_count(self):
        """Return the number of parameter markers in the query.

        :Return:
            Returns an integer of the number of markers in the query.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        return extern_mysql.mysql_stmt_param_count(self._stmt)

    def bind_output(self, *args):
        """Bind output variables.

        This binds where the output for each fetch will go.  You should pass in
        the appropriate `mysql.stmt.bind_out.Output_Bind` instances as
        arguments in the appropriate order.  See the `mysql.stmt.bind_out` docs
        for more detail.

        If you call this again, it will reset the bindings.

        :Exceptions:
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef extern_mysql.MYSQL_BIND * binds
        cdef int size
        cdef int num
        cdef int i
        cdef extern_mysql.MYSQL_BIND * bind
        cdef bind_out.Output_Bind arg

        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        num = len(args)
        size = num * sizeof(MYSQL_BIND)
        binds = <extern_mysql.MYSQL_BIND *> PyMem_Malloc(size)
        try:
            memset(binds, 0, size)

            for i from 0 <= i < num:
                arg = args[i]
                arg.init(self._connection, self, self._stmt, self._raise_error, i)
                bind = &binds[i]
                bind.buffer_type = arg._buffer_type
                bind.buffer = arg._buffer
                bind.buffer_length = arg._buffer_length
                bind.is_null = &arg.is_null
                bind.length = &arg.length
                bind.error = &arg.error
                bind.is_unsigned = arg._is_unsigned

            # Since we're keeping pointers to data inside these objects, we
            # need to store a local copy to maintain the reference count.
            # We will also use this for calling load().
            self._output_binds = args

            if extern_mysql.mysql_stmt_bind_result(self._stmt, binds):
                self._raise_error()
        finally:
            # MySQL makes a copy of binds into a private data member in the
            # stmt structure.  We do not need to keep ours around.
            PyMem_Free(binds)

    def bind_input(self, *args):
        """Bind input variables.

        This binds the objects that will be inspected for input variables. You
        should pass in the appropriate `mysql.stmt.bind_in.Input_Bind`
        instances as arguments in the appropriate order.  See the
        `mysql.stmt.bind_in` docs for more detail.

        If you call this again, it will reset the bindings.

        :Exceptions:
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef extern_mysql.MYSQL_BIND * binds
        cdef int size
        cdef int num
        cdef int i
        cdef extern_mysql.MYSQL_BIND * bind
        cdef bind_in.Input_Bind arg

        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        num = len(args)
        size = num * sizeof(MYSQL_BIND)
        binds = <extern_mysql.MYSQL_BIND *> PyMem_Malloc(size)
        try:
            memset(binds, 0, size)

            for i from 0 <= i < num:
                arg = args[i]
                arg.init(self._connection, self, self._stmt, self._raise_error, i)
                bind = &binds[i]
                bind.buffer_type = arg._buffer_type
                bind.buffer = arg._buffer
                bind.buffer_length = arg._buffer_length
                bind.length = &arg._length
                bind.is_null = &arg._is_null
                bind.is_unsigned = arg._is_unsigned

            # Since we're keeping pointers to data inside these objects, we
            # need to store a local copy to maintain the reference count.
            self._input_binds = args

            if extern_mysql.mysql_stmt_bind_param(self._stmt, binds):
                self._raise_error()
        finally:
            # MySQL makes a copy of binds into a private data member in the
            # stmt structure.  We do not need to keep ours around.
            PyMem_Free(binds)

    def execute(self, store_result=False):
        """Execute the SQL statement.

        **Note** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Parameters:
            - `store_result`: Whether or not to fetch the entire result from
              the server immediately for SELECT-like queries.  If False,
              results will be fetched from the server on an as-needed basis.
              Defaults to False.  Note that some methods in the Statement
              object are not available if this is False.

              Beware that setting this to True may use a lot of memory.

              However, setting this to False will tie up server resources, thus
              you shouldn't do that if you may be taking a long time to fetch
              the results.

              By default, fetching data with a Statement object fetches one row
              of data from the server at a time.  You may enable partial
              buffering by creating a server-side cursor by calling
              `set_use_cursor`.  In this case you can control how many results
              are buffered on the client side with the `set_prefetch_rows`
              method.  Generally the Statement object will behave the same
              as-if ``store_result`` is False when using a cursor.

              On MySQL version 5.0.18 and earlier, setting ``store_result`` to
              True when you have enabled server-side cursors will result in a
              `mysql.exceptions.Commands_Out_Of_Sync`.  Later versions will
              fetch all rows.

              **Note** You can only have 1 live "unbuffered" (False) result set
              at once.  You *must* fetch all rows (until
              `mysql.exceptions.No_More_Rows` is raised) or call ``close`` on
              the result before executing another statement.  If you do not do
              that, then this method will automatically call ``close`` on your
              old result object for you! Several other methods in the
              Connection and Statement objects will also force a close.  This
              is indicated in those method's docstrings.

        :Exceptions:
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
            - `OverflowError`: One of the input values did not fit into buffer
              type of the input binding.
            - `TypeError`: One of the input values did not match the type of
              the input binding.
        """
        cdef bind_in.Input_Bind in_bind

        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        # This will implicitly call ``reset`` if necessary.
        self._connection._check_unbuffered_result(None)

        for bind in self._input_binds:
            in_bind = bind
            in_bind.set_value()

        if extern_mysql.mysql_stmt_execute(self._stmt):
            self._raise_error()

        if store_result:
            # According to docs, it is safe and without performance penalty to
            # call store_result for non-SELECT statements.
            if extern_mysql.mysql_stmt_store_result(self._stmt):
                self._raise_error()
            self._connection._set_unbuffered_statement(None)
            self._stored = 1
        else:
            if extern_mysql.mysql_stmt_field_count(self._stmt) == 0:
                self._connection._set_unbuffered_statement(None)
            else:
                self._connection._set_unbuffered_statement(self)
            self._stored = 0

    def fetch(self):
        """Fetch one row of data.

        **Note** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Exceptions:
            - `mysql.exceptions.No_More_Rows`: There is no more data.
            - `mysql.exceptions.Data_Truncated`: The data was truncated.  You
              can inspect the "error" field of the
              `mysql.stmt.bind_out.Output_Bind` objects to figure out which
              field was truncated.
            - `mysql.exceptions.Unsupported_Param_Type`: date, time, datetime,
              or timestamp parameter type did not match the column type.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef bind_out.Output_Bind output
        cdef int rc

        self._connection._check_unbuffered_result(self)
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        rc = extern_mysql.mysql_stmt_fetch(self._stmt)
        if rc == 1:
            self._raise_error()
        elif rc == extern_mysql.MYSQL_NO_DATA:
            raise mysql.exceptions.No_More_Rows

        # We do not want to report truncation for streaming data types.
        # So, instead of looking at rc for MYSQL_DATA_TRUNCATED, we just
        # examine each output here.  This also allows us to ignore the
        # MYSQL_REPORT_DATA_TRUNCATION option.
        #
        # The current version of MySQL documentation says that truncation
        # reporting is disabled by default.  This is not true, and I have
        # opened bug #16288 with MySQL. (Update: the documentation has
        # been adjusted to indicate that the default is enabled.)
        truncated = False
        for output in self._output_binds:
            output.load()
            if output.error and not isinstance(output, Base_Out_Stream):
                truncated = True

        if truncated:
            raise mysql.exceptions.Data_Truncated

    def affected_rows(self):
        """Return the number of rows affected.

        **Note** For SELECT queries, this is only available if the result was
        stored by passing True to the ``store_result`` parameter in the
        ``execute`` call.

        Rows "affected" is defined as rows that were actually modified by an
        UPDATE, INSERT, or DELETE statement.  All other statements return zero.

        :Return:
            Returns the number of rows affected.

        :Exceptions:
            - `mysql.exceptions.Affected_Rows_Unavailable`: The query was not
              successful, or for SELECT queries, ``store_result`` was not set.
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef unsigned long long result

        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        result = extern_mysql.mysql_stmt_affected_rows(self._stmt)
        if result == -1:
            raise mysql.exceptions.Affected_Rows_Unavailable
        return _minimal_ulonglong(result)

    def set_update_max_length(self):
        """Tell MySQL to compute the ``max_length`` attribute in the field
        objects.

        Note that this will slow down execution of queries.

        This must be called before the data is fetched.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef extern_mysql.my_bool flag

        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        flag = 1
        if extern_mysql.mysql_stmt_attr_set(self._stmt, extern_mysql.STMT_ATTR_UPDATE_MAX_LENGTH, &flag):
            self._raise_error()

    def set_use_cursor(self):
        """When fetching results, use a cursor.

        When the ``store_result`` attribute is set to False (the default) in
        the `execute` method, results are normally fetched one row at a time.
        Before executing the query, you can call this method to tell MySQL to
        fetch a few rows at a time.  Use the `set_prefetch_rows` method to
        control the number of rows buffered at one time.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef unsigned long flag

        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        flag = extern_mysql.CURSOR_TYPE_READ_ONLY
        if extern_mysql.mysql_stmt_attr_set(self._stmt, extern_mysql.STMT_ATTR_CURSOR_TYPE, &flag):
            self._raise_error()

    def set_prefetch_rows(self, unsigned long num):
        """Set the number of rows to prefetch when using a cursor.

        The default is 1.

        :Parameters:
            - `num`: The number of rows to prefetch when using a cursor.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        if extern_mysql.mysql_stmt_attr_set(self._stmt, extern_mysql.STMT_ATTR_PREFETCH_ROWS, &num):
            self._raise_error()

    def get_update_max_length(self):
        """Determine if MySQL is currently set to compute the ``max_length``
        attribute in the field objects.

        :Return:
            Returns True if the ``max_length`` parameter will be set, False
            otherwise.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        # Due to bug #16144, this is an unsigned long.  The documentation was
        # originally not clear.  This has been changed to my_bool in 5.1.7,
        # and should be updated appropriately when ported to 5.1.
        cdef unsigned long flag

        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        if extern_mysql.mysql_stmt_attr_get(self._stmt, extern_mysql.STMT_ATTR_UPDATE_MAX_LENGTH, &flag):
            raise AssertionError('Attribute STMT_ATTR_UPDATE_MAX_LENGTH not known?')
        return flag

    def get_use_cursor(self):
        """Determine whether or not a server-side cursor will be used for
        fetching results.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef unsigned long flag

        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        if extern_mysql.mysql_stmt_attr_get(self._stmt, extern_mysql.STMT_ATTR_CURSOR_TYPE, &flag):
            raise AssertionError('Attribute STMT_ATTR_CURSOR_TYPE not known?')
        if flag == extern_mysql.CURSOR_TYPE_NO_CURSOR:
            return False
        elif flag == extern_mysql.CURSOR_TYPE_READ_ONLY:
            return True
        else:
            raise AssertionError('Unknown cursor flag.')

    def get_prefetch_rows(self):
        """Get the number of rows that will be prefetched when using a cursor.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef unsigned long num

        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        if extern_mysql.mysql_stmt_attr_get(self._stmt, extern_mysql.STMT_ATTR_PREFETCH_ROWS, &num):
            raise AssertionError('Attribute STMT_ATTR_PREFETCH_ROWS not known?')
        return _minimal_ulong(num)

    def field_count(self):
        """Return the number of output fields.

        :Return:
            Returns the number of output fields.  This is zero for statements
            like INSERT or DELETE that do not produce output.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        return extern_mysql.mysql_stmt_field_count(self._stmt)

    def free_result(self):
        """Release memory used by internal result buffers.

        This process is normally taken care of when the Statement object is
        deleted, but you can call this to proactively free some memory.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        if extern_mysql.mysql_stmt_free_result(self._stmt):
            self._raise_error()

    def insert_id(self):
        """Get the ID generated for an AUTO_INCREMENT column.

        The result is undefined for statements that do not update an
        AUTO_INCREMENT column.

        :Return:
            Returns the ID generated by an INSERT or UPDATE statement.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        return _minimal_ulonglong(extern_mysql.mysql_stmt_insert_id(self._stmt))

    def num_rows(self):
        """Return the number of rows in the result set.

        **Note** For SELECT queries, this is only available if the result was
        stored by passing True to the ``store_result`` parameter in the
        ``execute`` call.

        The result is undefined for non-SELECT statements.

        :Return:
            Returns the number of rows returned from the query.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        return _minimal_ulonglong(extern_mysql.mysql_stmt_num_rows(self._stmt))

    def row_tell(self):
        """Indicate the current row position.

        **Note** For SELECT queries, this is only available if the result was
        stored by passing True to the ``store_result`` parameter in the
        ``execute`` call.

        It returns an opaque object to be used with `row_seek`.

        :Return:
            Returns a `mysql.result.Row_Offset` instance.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
            - `mysql.exceptions.Result_Unbuffered_Error`: The result is in
              unbuffered mode (``store_result`` was set to False).
        """
        cdef mysql.result.Row_Offset offset

        self._check_store_result()

        offset = mysql.result.Row_Offset()
        offset._offset = extern_mysql.mysql_stmt_row_tell(self._stmt)
        return offset

    def row_seek(self, offset):
        """Set the current row position.

        **Note** For SELECT queries, this is only available if the result was
        stored by passing True to the ``store_result`` parameter in the
        ``execute`` call.

        :Parameters:
            - `offset`: An offset object returned from `row_tell` or an integer
              of an explicit row number (starting at zero).  If it is a number,
              it must be a number from 0 to ``num_rows()-1``.

        :Return:
            Returns the previous row offset as a `mysql.result.Row_Offset`
            instance.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
            - `mysql.exceptions.Result_Unbuffered_Error`: The result is in
              unbuffered mode (``store_result`` was set to False).
        """
        cdef mysql.result.Row_Offset old_offset
        cdef mysql.result.Row_Offset new_offset
        cdef extern_mysql.my_ulonglong int_off

        self._check_store_result()

        old_offset = mysql.result.Row_Offset()
        if isinstance(offset, mysql.result.Row_Offset):
            new_offset = <mysql.result.Row_Offset> offset
            old_offset._offset = extern_mysql.mysql_stmt_row_seek(self._stmt, new_offset._offset)
        else:
            old_offset._offset = extern_mysql.mysql_stmt_row_tell(self._stmt)
            if PyInt_Check(offset):
                int_off = PyInt_AsLong(offset)
            elif PyLong_Check(offset):
                int_off = PyLong_AsUnsignedLongLong(offset)
            else:
                int_off = PyLong_AsUnsignedLongLong(long(offset))
            extern_mysql.mysql_stmt_data_seek(self._stmt, int_off)

        return old_offset

    def reset(self, reset_binds=False):
        """Clear all state.

        This will clear internal buffers and state on the client and the
        server.  This releases the connection after doing a SELECT-like query,
        allowing you to perform other tasks.

        :Parameters:
            - `reset_binds`: If True, will remove all input and output binds
              (resetting the state as-if you recreate the Statement object from
              scratch).  This defaults to False.

        :Exceptions:
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        if extern_mysql.mysql_stmt_reset(self._stmt):
            self._raise_error()
        if reset_binds:
            self._input_binds = None
            self._output_binds = None

    def fields(self):
        """Get information about the fields in the result.

        This returns a list of `mysql.result.Field` objects which you can use
        to inspect the types of fields in the result.

        Note that the ``max_length`` member of the Field object is only
        computed if you have called `set_update_max_length`.

        :Return:
            Returns a list of `mysql.result.Field` instances that describe the
            columns in a query.

        :Exceptions:
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef extern_mysql.MYSQL_RES * result
        cdef mysql.result.Result r

        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        result = extern_mysql.mysql_stmt_result_metadata(self._stmt)
        if result == NULL:
            self._raise_error()
        r = mysql.result.Result()
        r._init(self._connection._db, self._connection, result, 1)
        return r.fields()

    def sqlstate(self):
        """Return the current SQL state.

        :Return:
            Returns a 5-character string.  A value of '00000' means "no error".
            A value of 'HY000' is for a MySQL state that is not yet mapped to a
            standard state.

        :Exceptions:
            - `mysql.exceptions.Statement_Closed_Error`: `close` has been
              called on this object.
            - `mysql.exceptions.Not_Connected_Error`: The connection has been
              closed.
        """
        cdef char * result
        if not self._connection.connected:
            raise mysql.exceptions.Not_Connected_Error
        if self._stmt == NULL:
            raise mysql.exceptions.Statement_Closed_Error

        result = extern_mysql.mysql_stmt_sqlstate(self._stmt)
        # Work around bug in MySQL that does not initialize the sqlstate for
        # statements the same way it does for the connection.  Filed bug #16143
        # with MySQL.  (Update: fix was pushed to 5.0.19.  Leaving this code
        # here since it is relatively benign.)
        if result[0] == c'\0':
            return '00000'
        else:
            return result

