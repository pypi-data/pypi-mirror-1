# $Header: /home/cvs2/mysql/mysql/exceptions/client.py,v 1.3 2006/08/26 20:19:52 ehuss Exp $
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

"""Exceptions from the MySQL client API.

These are all errors that the client-side of the MySQL API may generate.
"""

__version__ = '$Revision: 1.3 $'

from mysql.exceptions.base import MySQL_Error


class Unknown_Error(MySQL_Error):

    """An unknown error occurred."""

class Socket_Create_Error(MySQL_Error):

    """Failed to create a Unix socket."""

class Connection_Error(MySQL_Error):

    """Failed to connect to the local MySQL server."""

class Conn_Host_Error(MySQL_Error):

    """Failed to connect to the MySQL server."""

class IP_Sock_Error(MySQL_Error):

    """Failed to create an IP socket."""

class Unknown_Host(MySQL_Error):

    """Failed to find the IP address for the hostname."""

class Server_Gone_Error(MySQL_Error):

    """MySQL server has gone away."""

class Version_Error(MySQL_Error):

    """A protocol mismatch resulted from attempting to connect to a server with
    a client library that uses a different protocol version. This can happen if
    you use a very old client library to connect to a new server that wasn't
    started with the --old-protocol option.
    """

class Out_Of_Memory(MySQL_Error):

    """MySQL client ran out of memory."""

class Wrong_Host_Info(MySQL_Error):

    """Wrong host info."""

class Localhost_Connection(MySQL_Error):

    """Localhost via UNIX socket."""

class TCP_Connection(MySQL_Error):

    """TCP connection error."""

class Server_Handshake_Err(MySQL_Error):

    """Error in server handshake."""

class Server_Lost(MySQL_Error):

    """If connect_timeout > 0 and it took longer than connect_timeout seconds
    to connect to the server or if the server died while executing the
    init-command.
    """

class Commands_Out_Of_Sync(MySQL_Error):

    """Commands out of sync; you can't run this command now."""

class Named_Pipe_Connection(MySQL_Error):

    """Failed to connect to a named pipe on Windows."""

class Named_Pipe_Wait_Error(MySQL_Error):

    """Failed to wait for a named pipe on Windows."""

class Named_Pipe_Open_Error(MySQL_Error):

    """Failed to create a named pipe on Windows."""

class Named_Pipe_Set_State_Error(MySQL_Error):

    """Failed to get a pipe handler on Windows."""

class Cant_Read_Charset(MySQL_Error):

    """Unable to read the character set file."""

class Net_Packet_Too_Large(MySQL_Error):

    """Got packet bigger than 'max_allowed_packet' bytes."""

class Embedded_Connection(MySQL_Error):

    """Embedded server."""

class Probe_Slave_Status(MySQL_Error):

    """Error on SHOW SLAVE STATUS:."""

class Probe_Slave_Hosts(MySQL_Error):

    """Error on SHOW SLAVE HOSTS:."""

class Probe_Slave_Connect(MySQL_Error):

    """Error connecting to slave:."""

class Probe_Master_Connect(MySQL_Error):

    """Error connecting to master:."""

class Ssl_Connection_Error(MySQL_Error):

    """SSL connection error."""

class Malformed_Packet(MySQL_Error):

    """Malformed packet."""

class Wrong_License(MySQL_Error):

    """Invalid license when connecting to server."""

class Null_Pointer(MySQL_Error):

    """Invalid use of null pointer."""

class No_Prepare_Stmt(MySQL_Error):

    """Statement not prepared."""

class Params_Not_Bound(MySQL_Error):

    """No data supplied for parameters in prepared statement."""

class Data_Truncated(MySQL_Error):

    """Data truncated."""

class No_Parameters_Exists(MySQL_Error):

    """No parameters exist in the statement."""

class Invalid_Parameter_Number(MySQL_Error):

    """Invalid parameter number."""

class Invalid_Buffer_Use(MySQL_Error):

    """Indicates if the bind is to supply the long data in chunks and if the
    buffer type is non string or binary.
    """

class Unsupported_Param_Type(MySQL_Error):

    """The conversion is not supported. Possibly the buffer_type value is
    illegal or is not one of the supported types.
    """

class Shared_Memory_Connection(MySQL_Error):

    """Connection failure when using shared memory."""

class Shared_Memory_Connect_Request_Error(MySQL_Error):

    """Can't open shared memory; client could not create request event."""

class Shared_Memory_Connect_Answer_Error(MySQL_Error):

    """Can't open shared memory; no answer event received from server."""

class Shared_Memory_Connect_File_Map_Error(MySQL_Error):

    """Can't open shared memory; server could not allocate file mapping."""

class Shared_Memory_Connect_Map_Error(MySQL_Error):

    """Can't open shared memory; server could not get pointer to file mapping."""

class Shared_Memory_File_Map_Error(MySQL_Error):

    """Can't open shared memory; client could not allocate file mapping."""

class Shared_Memory_Map_Error(MySQL_Error):

    """Can't open shared memory; client could not get pointer to file mapping."""

class Shared_Memory_Event_Error(MySQL_Error):

    """Can't open shared memory; client could not create an event."""

class Shared_Memory_Connect_Abandoned_Error(MySQL_Error):

    """Can't open shared memory; no answer from server."""

class Shared_Memory_Connect_Set_Error(MySQL_Error):

    """Can't open shared memory; cannot send request event to server."""

class Conn_Unknow_Protocol(MySQL_Error):

    """Wrong or unknown protocol."""

class Invalid_Conn_Handle(MySQL_Error):

    """Invalid connection handle."""

class Secure_Auth(MySQL_Error):

    """Connection using old (pre-4.1.1) authentication protocol refused (client option 'secure_auth' enabled)."""

class Fetch_Canceled(MySQL_Error):

    """Row retrieval was canceled by mysql_stmt_close() call."""

class No_Data(MySQL_Error):

    """Attempt to read column without prior row fetch."""

class No_Stmt_Metadata(MySQL_Error):

    """Prepared statement contains no metadata."""

class No_Result_Set(MySQL_Error):

    """Attempt to read a row while there is no result set associated with the statement."""

class Not_Implemented(MySQL_Error):

    """This feature is not implemented yet."""
