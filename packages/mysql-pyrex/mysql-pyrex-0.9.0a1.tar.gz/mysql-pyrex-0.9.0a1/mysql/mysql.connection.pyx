# $Header: /home/cvs2/mysql/mysql/mysql.connection.pyx,v 1.9 2006/08/26 22:13:04 ehuss Exp $
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

"""Connection object used to communicate with the MySQL server.

The `Connection` object is the basic primitive you use to connect to the MySQL
server and communicate with it.  You can issue queries directly with the
`Connection.execute` method.  Alternatively, you can call
`Connection.new_statement` to use the statement API (see `mysql.stmt` for more
detail).

MySQL is generally a state-based API.  In other words, you can only do one
thing at a time.  For example, if you fetch results from a SELECT query with
server-side buffering, you can have only 1 result set live per Connection
object.  In some situations you can work around this, by retrieving all results
on the client-side, for example.  If you try to create multiple "live" result
objects, newer result objects will forcefully (and silently!) close previous
result objects (rendering the old ones useless and will raise
`mysql.exceptions.Result_Closed_Error` whenever accessed).

Various methods may indicate they raise `mysql.exceptions.MySQL_Error`. This is
a generic error to indicate that there are various MySQL-related exceptions
that may get raised. Some typical exceptions are:

- `mysql.exceptions.Commands_Out_Of_Sync`: Commands were executed in an
  improper order.
- `mysql.exceptions.Out_Of_Memory`: Out of memory.
- `mysql.exceptions.Server_Gone_Error`: The MySQL server has gone away.
- `mysql.exceptions.Server_Lost`: The connection to the server was lost during
  the query.
- `mysql.exceptions.Unknown_Error`: An unknown error occurred.
- `mysql.exceptions.Unknown_Com_Error`: The MySQL server doesn't implement this
  command (probably an old server).
"""

__version__ = '$Revision: 1.9 $'

include "python.pxi"
include "util/inline.pyx"

import string

import mysql.conversion.input
import mysql.conversion.output
import mysql.exceptions
import mysql.stmt

cimport mysql.result

class Character_Set:

    """Information about a character set.

    This object provides details about a character set returned from the
    `Connection.get_current_character_set_info` method.

    :IVariables:
        - `name`: The name of the character set.
        - `collation_name`: The collation name.
        - `comment`: Comment about the character set.
        - `dir`: Character set directory.
        - `mb_min_len`: Multi-byte character minimum length.
        - `mb_max_len`: Multi-byte character maximum length.
    """

    def __init__(self, name, collation_name, comment, dir, mb_min_len, mb_max_len):
        self.name = name
        self.collation_name = collation_name
        self.comment = comment
        self.dir = dir
        self.mb_min_len = mb_min_len
        self.mb_max_len = mb_max_len

    def __repr__(self):
        return '<Character_Set name=%r collation_name=%r comment=%r dir=%r mb_min_len=%r mb_max_len=%r>' % (
                self.name, self.collation_name, self.comment, self.dir, self.mb_min_len, self.mb_max_len)

cdef class Connection:

    """MySQL connection object.

    Creating a new Connection object has the following parameters (all
    optional):

    - ``convert_in``: A `mysql.conversion.input.Input_Conversion` instance to
      use for input parameter conversion. If not specified, defaults to the
      implementation in the `mysql.conversion.input` module.
    - ``convert_out``: A `mysql.conversion.output.Output_Conversion` instance
      to use for output value conversion (when using the `execute` method to
      retrieve results, this does not apply to the statement API).  If not
      specified, defaults to the implementation in the
      `mysql.conversion.output` module.
    - ``paramstyle``: The style of parameter substitution to use in the
      `execute` method.  This may be one of the following:

      - ``"format"``: Use simple Python format replacement, such as ``"SELECT *
        FROM t WHERE x=%s AND y=%i"``.
      - ``"pyformat"``: Use Python dictionary format replacement, such as
        ``"SELECT * FROM t WHERE x=%(param1)s AND y=%(param2)i"``. You may pass
        in a mapping object as the next argument after the statement. When both
        a mapping object and keyword arguments are given and there are
        duplicates, the placeholders from the keyword arguments take
        precedence.
      - ``"pytemplate"``: Use Python string Template substitution, such as
        ``"SELECT * FROM t WHERE x=$param1 AND y=$param2"``.  You may pass in a
        mapping object as the next argument after the statement. When both a
        mapping object and keyword arguments are given and there are
        duplicates, the placeholders from the keyword arguments take
        precedence.

      The default is ``"pytemplate"``.

      See the `mysql.conversion.input` module for detail on how parameters are
      escaped.

    :IVariables:
        - `connected`: Boolean value that indicates whether or not the
          connection is currently established.  (Read only.)
        - `paramstyle`: The paramstyle string passed in the constructor.
        - `_convert_in`: `mysql.conversion.input.Input_Conversion` instance.
          (Read only.)
        - `_convert_out`: `mysql.conversion.output.Output_Conversion` instance.
          (Read only.)
        - `_db`: MYSQL database structure.  May be NULL.  (C only.)
        - `_param_formatter`: The ``_param_*`` method to call to format
          parameters based on the ``paramstyle`` argument given in
          ``__init__``.  (C only.)
        - `_unbuffered_result`:  A live `mysql.result.Result` instance that is
          not buffering results on the client side.  This is monitored so that
          it can be closed whenever an operation is performed that would reset
          the state of the connection.  (C only.)
        - `_unbuffered_statement`:  A list `mysql.stmt.Statement` instance
          that is currently retrieving results without buffering them on the
          client side.  This is monitored so that it can be closed whenever an
          operation is performed that would reset the state of the connection.
          (C only.)
        - `_old_statements`: A _Statement_Cleaner instance for cleaning up
          statement structures.  (C only).
    """

    def __init__(self, convert_in=None, convert_out=None, paramstyle='pytemplate'):
        self._db = extern_mysql.mysql_init(NULL)
        if self._db == NULL:
            raise MemoryError
        self.connected = False
        if convert_in is None:
            self._convert_in = mysql.conversion.input.Basic_Conversion()
        else:
            self._convert_in = convert_in

        if convert_out is None:
            self._convert_out = mysql.conversion.output.Basic_Conversion()
        else:
            self._convert_out = convert_out

        self._old_statements = _Statement_Cleaner()

        # I would have preferred to define the param convert methods as C
        # functions for performance reasons.  However, I was unable to get
        # Pyrex to allow me to set a function pointer to a class cdef function.
        self._param_formatter = getattr(self, '_param_' + paramstyle)
        self.paramstyle = paramstyle

    def __dealloc__(self):
        extern_mysql.mysql_close(self._db)

    cdef _init_db(self):
        if self._db == NULL:
            self._db = extern_mysql.mysql_init(NULL)
            if self._db == NULL:
                raise MemoryError

    def connect(self, char *host=NULL,
                      char *user=NULL,
                      char *password=NULL,
                      char *db=NULL,
                      unsigned int port=0,
                      char * unix_socket=NULL,
                      unsigned long clientflag=0):
        """Connect to the database.

        **Warning**

        If a connection is already established, it will be closed and a new one
        created.  Doing this will invalidate any live unbuffered result object
        or Statement objects.  It also clears all state of the Connection
        object, including any options you have given previously, as-if a new
        Connection object was created.

        :Parameters:
            - `host`: The host to connect to.  If not specified, defaults to
              the local host.
            - `user`: The user to log in as.  If not specified, defaults to the
              current user.
            - `password`: The password to use.  If not specified, only entries
              in the MySQL ``user`` table with a blank password will work.
            - `db`: The database to use.  If not specified, no database is
              selected and you must use the `select_db` method.
            - `port`: The port to use for TCP/IP connections.  You must call
              `set_protocol_tcp` to use this option.
            - `unix_socket`: The named pipe to use for the connection.
            - `clientflag`: A bitwise-or of flags to use.  The following are
              defined in `mysql.constants.client_flags`:

              - ``COMPRESS``: Use compression protocol.
              - ``FOUND_ROWS``: Return the number of found (matched) rows, not
                the number of affected rows.
              - ``IGNORE_SPACE``: Allow spaces after function names. Makes all
                functions names reserved words.
              - ``INTERACTIVE``: Allow interactive_timeout seconds (instead of
                wait_timeout seconds) of inactivity before closing the
                connection. The client's session wait_timeout variable is set
                to the value of the session interactive_timeout variable.
              - ``LOCAL_FILES``: Enable LOAD DATA LOCAL handling.
              - ``MULTI_STATEMENTS``: Tell the server that the client may send
                multiple statements in a single string (separated by ``;``). If
                this flag is not set, multiple-statement execution is disabled.
              - ``MULTI_RESULTS``: Tell the server that the client can handle
                multiple result sets from multiple-statement executions or
                stored procedures. This is automatically set if
                MULTI_STATEMENTS is set.
              - ``NO_SCHEMA``: Don't allow the db_name.tbl_name.col_name
                syntax. This is for ODBC. It causes the parser to generate an
                error if you use that syntax, which is useful for trapping bugs
                in some ODBC programs.
              - ``ODBC``: The client is an ODBC client. This changes mysqld to
                be more ODBC-friendly.

        :Exceptions:
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
            - `mysql.exceptions.Conn_Host_Error`: Failed to connect to the
              My_SQL server.
            - `mysql.exceptions.Connection_Error`: Failed to connect to the
              local My_SQL server.
            - `mysql.exceptions.IP_Sock_Error`: Failed to create an IP socket.
            - `mysql.exceptions.Socket_Create_Error`: Failed to create a Unix
              socket.
            - `mysql.exceptions.Unknown_Host`: Failed to find the IP address
              for the hostname.
            - `mysql.exceptions.Version_Error`: A protocol mismatch resulted
              from attempting to connect to a server with a client library that
              uses a different protocol version. This can happen if you use a
              very old client library to connect to a new server that wasn't
              started with the --old-protocol option.
            - `mysql.exceptions.Named_Pipe_Open_Error`: Failed to create a
              named pipe on Windows.
            - `mysql.exceptions.Named_Pipe_Wait_Error`: Failed to wait for a
              named pipe on Windows.
            - `mysql.exceptions.Named_Pipe_Set_State_Error`: Failed to get a
              pipe handler on Windows.
            - `mysql.exceptions.Server_Lost`: If connect_timeout > 0 and it
              took longer than connect_timeout seconds to connect to the server
              or if the server died while executing the init-command.
            - `mysql.exceptions.Access_Denied_Error`: The user or password was
              wrong.
            - `mysql.exceptions.Bad_DB_Error`: The database didn't exist.
            - `mysql.exceptions.DB_Access_Denied_Error`: The user did not have
              access rights to the database.
            - `mysql.exceptions.Wrong_DB_Name`: The database name was too long.
        """
        if self._db == NULL:
            self._db = extern_mysql.mysql_init(NULL)
        else:
            if self.connected:
                self._check_unbuffered_result(None)
                extern_mysql.mysql_close(self._db)
                self._db = extern_mysql.mysql_init(NULL)
                self.connected = False
        if self._db == NULL:
            raise MemoryError

        if extern_mysql.mysql_real_connect(self._db,
                                           host,
                                           user,
                                           password,
                                           db,
                                           port,
                                           unix_socket,
                                           clientflag) == NULL:
            self._raise_error()
        self.connected = True

    def disconnect(self):
        """Disconnect from the database.

        **Warning**

        This will invalidate any live, unbuffered result objects and Statement
        objects!  It also clears all state of the Connection object, including
        any options you have given, as-if a new Connection object was created.

        This never fails.
        """
        self._check_unbuffered_result(None)
        if self._db != NULL:
            extern_mysql.mysql_close(self._db)
            self._db = NULL
        self.connected = False

    def _raise_error(self):
        """Raise the appropriate MySQL error exception from the current MySQL
        error.

        If there is no error, then `mysql.exceptions.client.Unknown_Error` is
        raised.

        Never call this when self._db is NULL.
        """
        cdef unsigned int errno
        cdef char * err_str
        if self._db == NULL:
            # This should never happen.
            raise mysql.exceptions.Not_Connected_Error
        errno = extern_mysql.mysql_errno(self._db)
        err_str = extern_mysql.mysql_error(self._db)
        raise mysql.exceptions.raise_error(errno, err_str)

    def select_db(self, database):
        """Set the database to use.

        **Note:** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Parameters:
            - `database`: The name of the database.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._check_unbuffered_result(None)
        if extern_mysql.mysql_select_db(self._db, database):
            self._raise_error()

    def add_init_command(self, statement, *args, **kwargs):
        """Command to execute when connecting to the MySQL server. Will
        automatically be re-executed when reconnecting (when `set_reconnect_on`
        is used).

        You may call this multiple times to add multiple commands.

        Closing a connection will clear any init commands registered.

        The arguments and keyword arguments behave the same as the `execute`
        method paying attention to the ``paramstyle`` specified when creating
        the connection object.

        Note that this will not allow NUL characters in the statement or
        values.

        :Parameters:
            - `statement`: The SQL command to execute.
        """
        self._init_db()

        statement = self._param_formatter(statement, *args, **kwargs)

        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_INIT_COMMAND, statement):
            raise AssertionError('Command should never fail.')

    def set_use_compression(self):
        """Use the compressed client/server protocol.

        Will only take effect on the next connection attempt.
        """
        self._init_db()

        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_OPT_COMPRESS, NULL):
            raise AssertionError('Command should never fail.')

    def set_connect_timeout(self, unsigned int timeout):
        """Set the connect timeout in seconds.

        Will only take effect on the next connection attempt.

        :Parameters:
            - `timeout`: The connect timeout in seconds.
        """
        self._init_db()

        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_OPT_CONNECT_TIMEOUT, <char *> &timeout):
            raise AssertionError('Command should never fail.')

    def set_enable_local_infile(self):
        """Enable the "LOAD DATA LOCAL INFILE" command.

        Will only take effect on the next connection attempt.

        This option is only available if your MySQL installation was compiled
        to support it (with --enable-local-infile) and the MySQL server or
        client configuration files have not explicitly disabled its support
        (with --local-infile=0).  If it is not supported, you will get a
        `mysql.exceptions.Not_Allowed_Command` exception when you try to
        execute the statement.
        """
        self._init_db()

        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_OPT_LOCAL_INFILE, NULL):
            raise AssertionError('Command should never fail.')

    def set_disable_load_infile(self):
        """Disable the "LOAD DATA LOCAL INFILE" command.

        Will only take effect on the next connection attempt.

        See notes in `set_enable_local_infile` for more detail.
        """
        cdef unsigned int flag

        self._init_db()

        flag = 0
        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_OPT_LOCAL_INFILE, <char *> &flag):
            raise AssertionError('Command should never fail.')

    def set_protocol_default(self):
        """Use the default connection protocol.

        Will only take effect on the next connection attempt.
        """
        cdef unsigned int protocol

        self._init_db()

        protocol = extern_mysql.MYSQL_PROTOCOL_DEFAULT
        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_OPT_PROTOCOL, <char *> &protocol):
            raise AssertionError('Command should never fail.')

    def set_protocol_tcp(self):
        """Use the TCP connection protocol.

        Will only take effect on the next connection attempt.
        """
        cdef unsigned int protocol

        self._init_db()

        protocol = extern_mysql.MYSQL_PROTOCOL_TCP
        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_OPT_PROTOCOL, <char *> &protocol):
            raise AssertionError('Command should never fail.')

    def set_protocol_socket(self):
        """Use the socket connection protocol (Unix).

        Will only take effect on the next connection attempt.
        """
        cdef unsigned int protocol

        self._init_db()

        protocol = extern_mysql.MYSQL_PROTOCOL_SOCKET
        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_OPT_PROTOCOL, <char *> &protocol):
            raise AssertionError('Command should never fail.')

    def set_protocol_pipe(self):
        """Use the named pipe connection protocol (Windows).

        Will only take effect on the next connection attempt.
        """
        cdef unsigned int protocol

        self._init_db()

        protocol = extern_mysql.MYSQL_PROTOCOL_PIPE
        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_OPT_PROTOCOL, <char *> &protocol):
            raise AssertionError('Command should never fail.')

    def set_protocol_memory(self):
        """Use the shared memory connection protocol.

        Will only take effect on the next connection attempt.
        """
        cdef unsigned int protocol

        self._init_db()

        protocol = extern_mysql.MYSQL_PROTOCOL_MEMORY
        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_OPT_PROTOCOL, <char *> &protocol):
            raise AssertionError('Command should never fail.')

    def set_read_timeout(self, unsigned int timeout):
        """Set the read timeout for communicating with the server.

        Will only take effect on the next connection attempt.

        :Parameters:
            - `timeout`: The read timeout in seconds.
        """
        self._init_db()

        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_OPT_READ_TIMEOUT, <char *> &timeout):
            raise AssertionError('Command should never fail.')

    def set_write_timeout(self, unsigned int timeout):
        """Set the write timeout for communicating with the server.

        Will only take effect on the next connection attempt.

        :Parameters:
            - `timeout`: The write timeout in seconds.
        """
        self._init_db()

        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_OPT_WRITE_TIMEOUT, <char *> &timeout):
            raise AssertionError('Command should never fail.')

    def set_reconnect_on(self):
        """Automatically reconnect when the connection to the server is lost.

        Note that it will not attempt to reconnect if the connection is in the
        middle of a transaction.  Calls that need to interact with the server
        will immediately raise `mysql.exceptions.Server_Gone_Error`.

        This must be called after a connection is established.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
        """
        cdef extern_mysql.my_bool reconnect

        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._init_db()

        reconnect = 1
        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_OPT_RECONNECT, &reconnect):
            raise AssertionError('Command should never fail.')

    def set_reconnect_off(self):
        """Do *not* automatically reconnect when the connection to the server
        is lost.

        This is the default.

        This must be called after a connection is established.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
        """
        cdef extern_mysql.my_bool reconnect

        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._init_db()

        reconnect = 0
        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_OPT_RECONNECT, &reconnect):
            raise AssertionError('Command should never fail.')

    def set_default_conf_file(self, char * filename):
        """Set the configuration file to load instead of ``my.cnf``.

        Will only take effect on the next connection attempt.

        :Parameters:
            - `filename`: The file name to load the options from.
        """
        self._init_db()

        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_READ_DEFAULT_FILE, filename):
            raise AssertionError('Command should never fail.')

    def set_default_conf_group(self, char * group_name):
        """Set the group in my.cnf to read from.

        Will only take effect on the next connection attempt.

        :Parameters:
            - `group_name`: The name of the group from the configuration file.
        """
        self._init_db()

        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_READ_DEFAULT_GROUP, group_name):
            raise AssertionError('Command should never fail.')

    def set_secure_auth_on(self):
        """Only connect to servers that support the password hashing used in
        MySQL 4.1.1 and later.

        Will only take effect on the next connection attempt.
        """
        cdef extern_mysql.my_bool enabled

        self._init_db()

        enabled = 1
        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_SECURE_AUTH, &enabled):
            raise AssertionError('Command should never fail.')

    def set_secure_auth_off(self):
        """Allow you to connect to servers that do *not* support the password
        hashing used in MySQL 4.1.1 and later.

        Will only take effect on the next connection attempt.

        This is the default (unless overridden by a configuration file).
        """
        cdef extern_mysql.my_bool enabled

        self._init_db()

        enabled = 0
        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_SECURE_AUTH, &enabled):
            raise AssertionError('Command should never fail.')

    def set_charset_dir(self, char * directory):
        """Set the pathname to the directory that contains character set
        definition files.

        Will only take effect on the next connection attempt.

        :Parameters:
            - `directory`: The directory of character set definition files.
        """
        self._init_db()

        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_SET_CHARSET_DIR, directory):
            raise AssertionError('Command should never fail.')

    def set_charset_name(self, char * charset):
        """Set the name of the character set to use as the default character
        set.

        Will only take effect on the next connection attempt.

        :Parameters:
            - `charset`: The default character set to use.
        """
        self._init_db()

        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_SET_CHARSET_NAME, charset):
            raise AssertionError('Command should never fail.')

    def set_shared_memory_base_name(self, char * base_name):
        """Set the name of the shared memory object for communicating with the
        server.

        Will only take effect on the next connection attempt.

        :Parameters:
            - `base_name`: The name of the shared memory object.
        """
        self._init_db()

        if extern_mysql.mysql_options(self._db, extern_mysql.MYSQL_SHARED_MEMORY_BASE_NAME, base_name):
            raise AssertionError('Command should never fail.')

    def escape(self, statement, *args, **kwargs):
        """Escape arguments for a SQL statement.

        This performs the same argument substitution and character escaping
        that the `execute` method uses.

        The arguments and keyword arguments behave the same as the `execute`
        method paying attention to the ``paramstyle`` specified when creating
        the connection object.

        :Parameters:
            - `statement`: The SQL command to escape.

        :Return:
            Returns the statement as a string with the arguments included and
            properly escaped.
        """
        return self._param_formatter(statement, *args, **kwargs)

    def _param_format(self, statement, *args, **kwargs):
        """Convert args using simple python format replacement."""
        assert not kwargs
        return statement % self._escape_args(args)

    def _param_pyformat(self, statement, *args, **kwargs):
        """Convert args using python dictionary format replacement."""
        if len(args) == 0:
            return statement % self._escape_kwargs(kwargs)
        elif len(args) == 1:
            d = {}
            d.update(args[0])
            d.update(kwargs)
            return statement % self._escape_kwargs(d)
        else:
            raise ValueError('You must specify only 0 or 1 arguments when using pyformat paramstyle.')

    def _param_pytemplate(self, statement, *args, **kwargs):
        """Convert args using python string Template replacement."""
        if len(args) == 0:
            return string.Template(statement).safe_substitute(self._escape_kwargs(kwargs))
        elif len(args) == 1:
            mapping = args[0]
            return string.Template(statement).safe_substitute(self._escape_kwargs(mapping), **self._escape_kwargs(kwargs))
        else:
            raise ValueError('You must specify only 0 or 1 arguments when using pytemplate paramstyle.')

    cdef _escape_args(self, args):
        return self._convert_in.convert(*args)

    cdef _escape_kwargs(self, kwargs):
        new_kwargs = {}
        for kw_name, kw_value in kwargs.items():
            new_kwargs[kw_name] = self._convert_in.convert(kw_value)[0]
        return new_kwargs

    def execute(self, statement, *args, **kwargs):
        """Issue a SQL statement.

        Additional arguments and keywords are used for parameter substitution
        in the statement.  How these are used depends on the ``paramstyle``
        parameter used when creating the Connection object.  Beware that the
        keyword ``store_result`` is not available for use since it is used by
        this function.

        :Parameters:
            - `statement`: The SQL statement to issue.
            - `store_result`: Whether or not to fetch the entire result from
              the server immediately for SELECT-like queries.  If False,
              results will be fetched from the server on an as-needed basis.
              Defaults to False.  Note that some methods in the Result object
              are not available if this is False.

              Beware that setting this to True may use a lot of memory.

              However, setting this to False will tie up server resources, thus
              you shouldn't do that if you may be taking a long time to fetch
              the results.

              **Note:** You can only have 1 live "unbuffered" (False) result
              set at once.  You *must* fetch all rows (until ``No_More_Rows``
              is raised) or call ``close`` on the result before executing
              another statement.  If you do not do that, then this method will
              automatically call ``close`` on your old result object for you!
              Several other methods in the Connection and Statement objects
              will also force a close.  This is indicated in those method's
              docstrings.

        :Return:
            Returns a `mysql.result.Result` object for SELECT-like queries
            (SELECT, SHOW, DESCRIBE, EXPLAIN), otherwise returns the number of
            rows affected.

            Rows "affected" is defined as rows that were actually modified by
            an UPDATE, INSERT, or DELETE statement.  All other statements
            return zero.

            Note that when you use a REPLACE command, this returns 2 if the new
            row replaced an old row. This is because in this case one row was
            inserted after the duplicate was deleted.

            If you use INSERT ... ON DUPLICATE KEY UPDATE to insert a row, this
            returns 1 if the row is inserted as a new row and 2 if an existing
            row is updated.

            If you specify the flag CLIENT_FOUND_ROWS when connecting, this
            returns the number of rows matched by the WHERE statement for
            UPDATE statements, not the number of rows actually modified.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        cdef char * statement_str
        cdef int statement_len

        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._check_unbuffered_result(None)

        if kwargs.has_key('store_result'):
            store_result = kwargs['store_result']
            del kwargs['store_result']
        else:
            store_result = False

        statement = self._param_formatter(statement, *args, **kwargs)

        statement_str = PyString_AsString(statement)
        statement_len = PyString_Size(statement)

        if extern_mysql.mysql_real_query(self._db, statement_str, statement_len):
            self._raise_error()

        return self._return_statement_result(store_result)

    def exec_container(self, container, statement, store_result=False):
        """Execute a statement retrieving inputs from a container.

        This method is similar to the `execute` method, except it gets its
        inputs from a container object instead as method parameters.

        The paramstyle must by "pytemplate".  The variable names are obtained
        from the statement.  It uses ``getattr`` to obtain the values from the
        ``container`` object.

        :Parameters:
            - `container`: The object to look for the input parameters.
            - `statement`: The SQL statement to issue.
            - `store_result`: Whether or not to fetch the entire result from
              the server imediately for SELECT-like queries.  The default is
              False.  See the `execute` method for more detail.

        :Return:
            Returns a `mysql.result.Result` object for SELECT-like queries,
            otherwise returns the number of rows affected.  See the `execute`
            method for more detail.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        assert self.paramstyle == 'pytemplate'
        # Find the inputs.
        inputs = {}
        for match in string.Template.pattern.finditer(statement):
            named = match.group('named')
            if named is not None:
                inputs[named] = getattr(container, named)
            braced = match.group('braced')
            if braced is not None:
                inputs[braced] = getattr(container, braced)
        return self.execute(statement, inputs, store_result=store_result)

    def exec_fetch_container(self, container, statement, store_result=False):
        """Execute a statement retrieving inputs and storing ouputs from/to a
        container.

        This method is similar to the `execute` method, except it gets its
        inputs from a container object instead as method parameters.  The
        output for one row is stored in the container object.

        The paramstyle must by "pytemplate".  The variable names are obtained
        from the statement.  It uses ``getattr`` to obtain the values from the
        ``container`` object and ``setattr`` to set them.

        If a column name is aliased with "AS", then the aliased name will be
        used for setting the value in the container.

        :Parameters:
            - `container`: The object to look for the input parameters and to
              set the output.
            - `statement`: The SQL statement to issue.
            - `store_result`: Whether or not to fetch the entire result from
              the server imediately for SELECT-like queries.  The default is
              False.  See the `execute` method for more detail.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
            - `mysql.exceptions.No_More_Rows`: There are no more rows left.
        """
        result = self.exec_container(container, statement, store_result=store_result)
        result.fetch_container(container)

    cdef _return_statement_result(self, store_result):
        cdef extern_mysql.my_ulonglong affected
        cdef mysql.result.Result res
        cdef extern_mysql.MYSQL_RES * my_result

        affected = extern_mysql.mysql_affected_rows(self._db)
        if affected == <extern_mysql.my_ulonglong> -1:
            # SELECT statement.
            if store_result:
                my_result = extern_mysql.mysql_store_result(self._db)
            else:
                my_result = extern_mysql.mysql_use_result(self._db)
            if my_result == NULL:
                self._raise_error()
            res = mysql.result.Result()
            res._init(self._db, self, my_result, store_result)
            if not store_result:
                self._unbuffered_result = res
            return res
        else:
            return _minimal_ulonglong(affected)

    # Sigh, C functions cannot have default argument values.  I would like
    # stmt=None.
    cdef _check_unbuffered_result(self, stmt):
        if self._unbuffered_result is not None:
            # XXX: Consider issuing a warning with the warning module?
            self._unbuffered_result.close()
            self._unbuffered_result = None
        if self._unbuffered_statement is not None and self._unbuffered_statement is not stmt:
            self._unbuffered_statement.reset()
            self._unbuffered_statement = None
        self._old_statements.clean()

    def _set_unbuffered_statement(self, statement):
        """Set the current unbuffered statement object.

        This is used to keep track of which `mysql.stmt.Statement` object
        is currently live with unbuffered results.  It removes the previously
        set Statement object.
        """
        self._unbuffered_statement = statement

    def commit(self):
        """Commit the current transaction.

        If no transaction is in progress, this does nothing.  Note that the
        default mode of a connection is "autocommit" which makes this command
        not needed.

        **Note:** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._check_unbuffered_result(None)

        if extern_mysql.mysql_commit(self._db):
            self._raise_error()

    def rollback(self):
        """Roll back the current transaction.

        If no transaction is in progress, this does nothing.  Note that the
        default mode of a connection is "autocommit" which makes this command
        not needed.

        **Note:** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._check_unbuffered_result(None)

        if extern_mysql.mysql_rollback(self._db):
            self._raise_error()

    def change_user(self, char * user=NULL,
                          char * password=NULL,
                          char * db=NULL):
        """Switch user and current database.

        If the user cannot be authenticated or does not have permissions, the
        current user and database are not changed.

        This command always performs a ROLLBACK of any active transactions,
        closes all temporary tables, unlocks all locked tables and resets the
        state as if one had done a new connect. This happens even if the user
        didn't change.

        **Note:** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Parameters:
            - `user`: The user to log in as.  If not specified, defaults to the
              current user.
            - `password`: The password to use.  If not specified, only entries in
              the MySQL ``user`` table with a blank password will work.
            - `db`: The database to use.  If not specified, no database is
              selected and you must use the `select_db` method.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
            - `mysql.exceptions.Access_Denied_Error`: The user or password was
              wrong.
            - `mysql.exceptions.Bad_DB_Error`: The database didn't exist.
            - `mysql.exceptions.DB_Access_Denied_Error`: The user did not have
              access rights to the database.
            - `mysql.exceptions.Wrong_DB_Name`: The database name was too long.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._check_unbuffered_result(None)

        if extern_mysql.mysql_change_user(self._db, user, password, db):
            self._raise_error()

    def get_current_character_set_info(self):
        """Return information about the current character set.

        :Return:
            Returns a `Character_Set` object of the current connection.
        """
        cdef extern_mysql.MY_CHARSET_INFO cs
        self._init_db()
        extern_mysql.mysql_get_character_set_info(self._db, &cs)

        # I noticed that cs.dir can be NULL.  Not sure if any of the other
        # parameters can be NULL, but might as well be safe.
        if cs.csname == NULL:
            cs.csname = ''
        if cs.name == NULL:
            cs.name = ''
        if cs.comment == NULL:
            cs.comment = ''
        if cs.dir == NULL:
            cs.dir = ''

        return Character_Set(cs.csname, cs.name, cs.comment, cs.dir, cs.mbminlen, cs.mbmaxlen)

    def set_current_character_set(self, char * name):
        """Set the current character set name.

        This is similar to the SET NAMES statement.

        The connection collation becomes the default collation of the character
        set.

        **Note:** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Parameters:
            - `name`: The name of the character set to use.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._check_unbuffered_result(None)

        if extern_mysql.mysql_set_character_set(self._db, name):
            self._raise_error()

    def get_client_info(self):
        """Return the client version as a string.

        :Return:
            Returns a string that represents the client library version (such
            as '5.0.15').
        """
        return extern_mysql.mysql_get_client_info()

    def get_client_version(self):
        """Return the client version as an integer.

        :Return:
            Returns an integer that has the format XYYZZ where X is the major
            version, YY is the release level, and ZZ is the version number
            within the release level. For example, a value of 50015 represents
            a client library version of 5.0.15
        """
        return _minimal_ulong(extern_mysql.mysql_get_client_version())

    def get_host_info(self):
        """Return information about the type of connection in use.

        :Return:
            Returns a string that describes the current connection.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error
        return extern_mysql.mysql_get_host_info(self._db)

    def get_protocol_version(self):
        """Return the protocol used by the current connection.

        :Return:
            Returns an integer of the current protocol version.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error
        return extern_mysql.mysql_get_proto_info(self._db)

    def get_server_info(self):
        """Return the server version as a string.

        :Return:
            Returns a string that represents the server version (such as
            '5.0.15').

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error
        return extern_mysql.mysql_get_server_info(self._db)

    def get_server_version(self):
        """Return the server version as an integer.

        :Return:
            Returns an integer that has the format XYYZZ where X is the major
            version, YY is the release level, and ZZ is the version number
            within the release level. For example, a value of 50015 represents
            a server version of 5.0.15

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error
        return _minimal_ulong(extern_mysql.mysql_get_server_version(self._db))

    def last_statement_info(self):
        """Return an informational string about the last statement executed.

        The format of the string varies depending on the type of query, as
        described here. The numbers are illustrative only; the string contains
        values appropriate for the query.

        - ``INSERT INTO ... SELECT ...``

          String format: ``Records: 100 Duplicates: 0 Warnings: 0``

        - ``INSERT INTO ... VALUES (...),(...),(...)...``

          String format: ``Records: 3 Duplicates: 0 Warnings: 0``

          NOTE: Only returns information for the multiple-row form of the
          statement.

        - ``LOAD DATA INFILE ...``

          String format: ``Records: 1 Deleted: 0 Skipped: 0 Warnings: 0``

        - ``ALTER TABLE``

          String format: ``Records: 3 Duplicates: 0 Warnings: 0``

        - ``UPDATE``

          String format: ``Rows matched: 40 Changed: 40 Warnings: 0``

        :Return:
            Returns a string describing the last statement executed.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.No_Statement_Info_Error`: Information is not
              available for the last statement.
        """
        cdef char * result
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error
        result = extern_mysql.mysql_info(self._db)
        if result == NULL:
            raise mysql.exceptions.No_Statement_Info_Error
        return result

    def last_insert_id(self):
        """Return the last AUTO_INCREMENT id.

        Returns the value generated for an AUTO_INCREMENT column by the
        previous INSERT or UPDATE statement. Use this method after you have
        performed an INSERT statement into a table that contains an
        AUTO_INCREMENT field.

        More precisely, the last insert ID is updated under these conditions:

        - INSERT statements that store a value into an AUTO_INCREMENT column.
          This is true whether the value is automatically generated by storing
          the special values NULL or 0 into the column, or is an explicit
          non-special value.

        - In the case of a multiple-row INSERT statement, this returns the
          first automatically generated AUTO_INCREMENT value; if no such value
          is generated, it returns the last last explicit value inserted into
          the AUTO_INCREMENT column.

        - INSERT statements that generate an AUTO_INCREMENT value by inserting
          LAST_INSERT_ID(expr) into any column.

        - INSERT statements that generate an AUTO_INCREMENT value by updating
          any column to LAST_INSERT_ID(expr).

        - The value is not affected by statements such as SELECT that return a
          result set.

        - If the previous statement returned an error, the value is undefined.

        - Note that this raises No_Insert_ID_Error if the previous statement
          does not use an AUTO_INCREMENT value. If you need to save the value
          for later, be sure to call `last_insert_id` immediately after the
          statement that generates the value.

        The value is affected only by statements issued within the current
        client connection. It is not affected by statements issued by other
        clients.

        Also note that the value of the SQL LAST_INSERT_ID() function always
        contains the most recently generated AUTO_INCREMENT value, and is not
        reset between statements because the value of that function is
        maintained in the server. Another difference is that LAST_INSERT_ID()
        is not updated if you set an AUTO_INCREMENT column to a specific
        non-special value.

        The reason for the difference between LAST_INSERT_ID() and
        `last_insert_id` is that LAST_INSERT_ID() is made easy to use in
        scripts while `last_insert_id` tries to provide a little more exact
        information of what happens to the AUTO_INCREMENT column.

        :Return:
            Returns an integer of the last insert id.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.No_Insert_ID_Error`: The last insert ID is not
              available.
        """
        cdef extern_mysql.my_ulonglong result
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        result = extern_mysql.mysql_insert_id(self._db)
        if result == 0:
            raise mysql.exceptions.No_Insert_ID_Error

        return _minimal_ulonglong(result)

    def kill_server_thread(self, unsigned long thread_id):
        """Asks the server to kill a thread.

        **Note:** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Parameters:
            - `thread_id`: The thread ID to kill.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._check_unbuffered_result(None)

        if extern_mysql.mysql_kill(self._db, thread_id):
            self._raise_error()

    def ping(self):
        """Check if the connection to the server is working.

        If the connection has gone down, an automatic reconnection is attempted
        (if `set_reconnect_on` is used).

        This function can be used by clients that remain idle for a long while,
        to check whether the server has closed the connection and reconnect if
        necessary.

        **Note:** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._check_unbuffered_result(None)

        if extern_mysql.mysql_ping(self._db):
            self._raise_error()

    def enable_multi_statements(self):
        """Enable the support for issuing multiple statements in one call.

        Multiple statements can be seperated with a semicolon (;).

        This can also be enabled with the MULTI_STATEMENTS flag in the connect
        call.

        The `execute` method will return the first result.  To get additional
        results, call the `next_result` method.

        **Note:** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._check_unbuffered_result(None)

        if extern_mysql.mysql_set_server_option(self._db, extern_mysql.MYSQL_OPTION_MULTI_STATEMENTS_ON):
            self._raise_error()

    def disable_multi_statements(self):
        """Disable the use of multiple statements.

        **Note:** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._check_unbuffered_result(None)

        if extern_mysql.mysql_set_server_option(self._db, extern_mysql.MYSQL_OPTION_MULTI_STATEMENTS_OFF):
            self._raise_error()

    def has_more_results(self):
        """Return whether or not more results are available.

        This is used for multiple-statement execution.  You can call this
        method to check if more results are available.

        :Return:
            Returns a boolean of whether or not more results are available.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        return extern_mysql.mysql_more_results(self._db)

    def next_result(self, store_result=False):
        """Get the next result for multi-statement execution.

        When executing multiple statements at once, the `execute` method will
        return the first result for the first statement.  You may then call
        this method repeatedly to get the next result.

        See the module docstring for more detail about handling multiple
        results.

        See the `execute` method for more detail about the return value.

        **Note:** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Parameters:
            - `store_result`: Whether or not to fetch the entire result from
              the server immediately for SELECT-like queries.  If False,
              results will be fetched from the server on an as-needed basis.
              Defaults to False.

        :Return:
            Returns a `mysql.result.Result` object or a number of rows
            affected.

        :Exceptions:
            - `mysql.exceptions.No_More_Results`: No more results are
              available.
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        cdef int rc
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._check_unbuffered_result(None)

        rc = extern_mysql.mysql_next_result(self._db)
        if rc == 0:
            return self._return_statement_result(store_result)
        elif rc == -1:
            raise mysql.exceptions.No_More_Results
        else:
            self._raise_error()

    def shutdown_server(self):
        """Ask the server to shut down.

        You must have SHUTDOWN privileges to run this command.

        **Note:** This will close any live unbuffered result objects and reset
        any live statement objects.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._check_unbuffered_result(None)

        if extern_mysql.mysql_shutdown(self._db, extern_mysql.SHUTDOWN_DEFAULT):
            self._raise_error()

    def sqlstate(self):
        """Return the current SQL state.

        The error code consists of five characters. '00000' means "no error".
        The values are specified by ANSI SQL and ODBC.

        Note that not all MySQL errors are mapped to SQLSTATE error codes. The
        value 'HY000' (general error) is used for unmapped errors.

        :Return:
            Returns a 5-character string.
        """
        self._init_db()
        return extern_mysql.mysql_sqlstate(self._db)

    def ssl_set(self, char * key=NULL,
                      char * cert=NULL,
                      char * ca=NULL,
                      char * capath=NULL,
                      char * cipher=NULL):
        """Set SSL parameters for the connection.

        This applies to the next call to `connect`.  Errors are not returned
        until you try to connect.

        All parameters are optional.

        :Parameters:
            - `key`: The pathname to the key file.
            - `cert`: The pathname to the certificate file.
            - `ca`: The pathname to the certificate authority file.
            - `capath`: The pathname to a directory that contains trusted SSL CA
              certificates in pem format.
            - `cipher`: A list (comma separated string) of allowable ciphers to
              use for SSL encryption.
        """
        self._init_db()

        extern_mysql.mysql_ssl_set(self._db, key, cert, ca, capath, cipher)

    def status(self):
        """Return a status string.

         This returns information similar to that provided by the ``mysqladmin
         status`` command. This includes uptime in seconds and the number of
         running threads, questions, reloads, and open tables.

         **Note:** This will close any live unbuffered result objects and reset
         any live statement objects.

         :Return:
            Returns a status string.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
            - `mysql.exceptions.MySQL_Error`: Generic MySQL error.
        """
        cdef char * result
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        self._check_unbuffered_result(None)

        result = extern_mysql.mysql_stat(self._db)
        if result == NULL:
            self._raise_error()
        return result

    def server_thread_id(self):
        """Return the server thread ID for the current connection.

        The thread ID may be used with the `kill_server_thread` method.

        Note that some methods may cause an automatic reconnection attempt,
        which causes the thread ID to change.  This means you should not get
        the thread ID and store it for later. You should get it when you need
        it.

        :Return:
            Returns the thread ID.

        :Exceptions:
            - `mysql.exceptions.Not_Connected_Error`: Method was called before
              calling `connect`.
        """
        cdef unsigned long id
        if not self.connected:
            raise mysql.exceptions.Not_Connected_Error

        id = extern_mysql.mysql_thread_id(self._db)
        if id == 0:
            raise mysql.exceptions.Not_Connected_Error

        return id

    def warning_count(self):
        """Return the number of warnings generated by the previous SQL
        statement.

        Issue the SHOW WARNINGS statement to see what the warnings actually
        are.

        :Return:
            Returns an integer of the number of warnings generated by the
            previous SQL statement.
        """
        self._init_db()
        return extern_mysql.mysql_warning_count(self._db)

    def new_statement(self, statement):
        """Create a new Statement object.

        See `mysql.stmt` for more detail on using the statement API.

        :Parameters:
            - `statement`: The SQL statement.

        :Return:
            Returns a new `mysql.stmt.Statement` object.
        """
        return mysql.stmt.Statement(self, statement)


cdef class _Statement_Cleaner:

    """Statement cleaning object.

    This object is responsible for freeing unused Statement objects.

    References to the statement objects are kept in this external object
    because we cannot keep it in the Connection object.  Because the Connection
    and Statement object are involved in a cycle, they need a neutral
    third-party to hold references to the statement objects and free them
    appropriately.

    :IVariables:
        - `_statement_list`: List of MYSQL_STMT structures (wrapped in
          PyCObject objects).
    """

    def __init__(self):
        self._statement_list = []

    cdef add_reference(self, extern_mysql.MYSQL_STMT * stmt):
        obj = PyCObject_FromVoidPtr(stmt, <void (*)(void*)>extern_mysql.mysql_stmt_close)
        PyList_Append(self._statement_list, obj)

    cdef clean(self):
        if PyList_Size(self._statement_list):
            PyList_DelSlice_SAFE(self._statement_list, 0, -1)
