# $Header: /home/cvs2/mysql/mysql/stmt/__init__.py,v 1.3 2006/08/26 20:19:52 ehuss Exp $
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

"""MySQL Statement API.

The Statement API is a way to pre-parse a SQL statement on the server-side, and
then reuse that SQL statement without requiring the server to reparse it.  It
also transfers the data as raw binary data, so there does not need to be an
intermediate conversion to and from a string (thus the statement API does not
use the `mysql.conversion` code).

A SQL statement is represented by the `mysql.stmt.Statement` object. Parameters
for the statement are stored in a `mysql.stmt.bind_in.Input_Bind` object.  You
can simply update the value inside the ``Input_Bind`` object and re-execute the
query.  The position in the SQL statement where you want your bound input value
to exist is denoted by a question mark.  The question marks are processed in
left-to-right order.

The results are placed into `mysql.stmt.bind_out.Output_Bind` objects.  You
must prepare these objects before you execute the statement.

An example of selecting data would be::

    class bar:

        def __init__(self, connection):
            self.thing = None
            self.foo = None
            self.s = connection.new_statement('SELECT foo FROM bar WHERE thing=?')
            self.s.bind_input(mysql.stmt.bind_in.In_Int(self, 'thing'))
            self.s.bind_output(mysql.stmt.bind_out.Out_Varchar(self, 'foo'))

    b = bar()
    b.thing = 7
    b.s.execute()
    b.s.fetch()
    print b.foo
    b.thing = 8
    b.s.execute()
    b.s.fetch()
    print b.foo

BLOB and TEXT columns can optionally use a streaming API for setting and
retrieving information.  For input parameters, it automatically sets the bound
input value to an object which has a ``write`` method.  For output parameters,
it similarly sets the output value to an object with a ``read`` method.

If you specified ``store_result`` as False (the default) to the ``execute``
method, then the results are buffered on the server side.  You can have only 1
live unbuffered statement object per connection in this case.  If you attempt
to execute another statement, then the original statment object will be
forcefully closed.  This goes for `mysql.result.Result` objects as well, only
one live unbuffered Result or Statement object may exist at one time.  Result
objects are capable of automatically, forcefully closing Statement objects and
vice-versa.

See `mysql.stmt.stmt` for more detail on the Statement object itself.

See `mysql.stmt.bind_in` for more detail on binding input values.

See `mysql.stmt.bind_out` for more detail on binding output values.

"""

__version__ = '$Revision: 1.3 $'

from mysql.stmt.stmt import Statement
