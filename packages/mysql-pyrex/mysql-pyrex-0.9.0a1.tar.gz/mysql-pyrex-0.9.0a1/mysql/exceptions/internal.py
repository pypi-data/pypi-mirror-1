# $Header: /home/cvs2/mysql/mysql/exceptions/internal.py,v 1.2 2006/08/26 20:19:52 ehuss Exp $
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

"""Internal errors from the MySQL Python code.
"""

__version__ = '$Revision: 1.2 $'

from mysql.exceptions.base import Error

class Not_Connected_Error(Error):

    """Tried to run a command when no connection is established."""

class Connected_Error(Error):

    """Attempted to use a command that cannot be used while connected."""

class Data_Truncated(Error):

    """Data was truncated in the last fetch."""

class Affected_Rows_Unavailable(Error):

    """The number of affected rows is not available.

    This can be because the query returned an error, or ``store_result`` was
    not set on a SELECT query.
    """

class Result_Unbuffered_Error(Error):

    """Attempted to call a method that requires the results to be buffered
    (stored) locally.
    """

class Result_Closed_Error(Error):

    """Attempted to use a result object that has been closed."""

class No_Statement_Info_Error(Error):

    """Information is not available for the last statement when using the
    `mysql.connection.Connection.last_statement_info` method.
    """

class No_Insert_ID_Error(Error):

    """The last insert ID is not available when calling the
    `mysql.connection.Connection.last_insert_id` method.
    """

class No_More_Results(Error):

    """No more results are available in the `mysql.connection.Connection.next_result` method."""

class No_More_Rows(Error):

    """The last row was reached in the `mysql.result.Result.fetch_row` method."""

class Statement_Closed_Error(Error):

    """Attempted to use a statement object that has been closed."""

class Connected_Error(Error):

    """Attempted to use a command that cannot be used while connected."""
