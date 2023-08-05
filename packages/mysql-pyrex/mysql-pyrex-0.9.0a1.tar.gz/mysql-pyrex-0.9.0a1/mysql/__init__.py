# $Header: /home/cvs2/mysql/mysql/__init__.py,v 1.6 2006/08/27 03:01:17 ehuss Exp $
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

"""MySQL 5 interface.

:Author: Eric Huss
:Contact: http://ehuss.org/mysql/
:License: BSD (See ``LICENSE`` file that came with distribution.)
:Copyright: |copy| 2006 Eric Huss
:Version: 0.9.0 Alpha 1

.. packagetree:: mysql

Introduction
============
This is an interface to MySQL 5 written in Pyrex.  See
http://www.cosc.canterbury.ac.nz/greg.ewing/python/Pyrex/ for more detail on
Pyrex.  Note that this library uses a slightly modified version of Pyrex. A
copy is included in the distribution in case you want to extend any of the
code.

There are 3 fundamental different ways to use the library.  They are:

1. "Simple" API.  This uses MySQL's normal query API.  It is a
   straightforward API of issuing SQL statements and getting results back.
2. "Container" API.  This API piggybacks on the "simple" API, but provides a
   slightly more convenient way to issue queries and retrieve results in an
   object-oriented environment.
3. "Statement" API.  The Statement API was introduced in MySQL 5.  It provides
   a method to pre-parse a SQL statement on the server-side.  You can then reuse
   that statement object repeatedly.  This offers a greater performance benefit
   if you are repeatedly issuing the same statements.

Connections
===========
Everything in the API centers around the connection object.  A connection
object represents a connection to the MySQL server.  It has a ``connect``
method to establish the connection::

    connection = mysql.connection.Connection()
    connection.connect(user=USER, password=PASSWORD)

Beware the MySQL typically only allows you to perform one operation at once
on the connection.  The interface will attempt to keep track of what you are
doing and abort any previous operations (such as reading results) if it would
conflict.  Details are sprinkled throughout the API with information on which
commands will abort other unfinished operations.

See the `mysql.connection` module for more details on the connection object.

Simple API
==========
Issuing SQL statements with the simple API is relatively, well, simple::

    connection.execute(
        'INSERT INTO sometable (foo, bar) VALUES ($foo, $bar)',
        foo=42, bar=24
    )

As you can see in this example, it uses Python's string template
interpolation scheme. See documentation for ``paramstyle`` in
`mysql.connection.Connection` for more detail and other schemes available.

For INSERT/UPDATE statements, the ``execute`` method will return the number
of rows affected.  For SELECT statements, it returns a `mysql.result.Result`
object which can be used to fetch rows::

    result = connection.execute('SELECT foo, bar FROM sometable')
    for foo, bar in result:
        ...

Data Conversion
---------------
The simple API provides a mechanism to convert between Python and MySQL data
types. MySQL values are always strings.  However, the conversion API allows
you to convert any type of input to a string, and convert certain types of
outputs to their Python data type equivalents.

When you create a connection object, one of the optional parameters is a
converter object.  There are some default converter objects that are used if
you do not specify one.  They have support for many data types, such as Sets,
datetime, decimal, integers, floats, strings, and more.

If you do not want result objects to convert values to Python data types, use
the `mysql.conversion.output.No_Conversion` object when creating the
connection. All values will be returned as strings as formatted by MySQL.

See `mysql.conversion` for more details on the conversion API.

Container API
=============
The container API is an extension of the simple API intended to simplify
object-oriented programming.  Essentially it provides an automatic method to
get and set values from/to an object.  It centers around the
`mysql.connection.Connection.exec_container` and
`mysql.connection.Connection.exec_fetch_container` for inserting and
retrieving data respectively.

An example of how this could be used is::

    class User:

        def __init__(self, connection):
            self.connection = connection

        def load(self, id):
            self.id = id
            self.connection.exec_fetch_container(self,
                'SELECT name FROM users WHERE id=$id')

        def update(self):
            self.connection.exec_container(self,
                'UPDATE users SET name=$name WHERE id=$id')

        def create(self, name):
            self.name = name
            self.connection.exec_container(self,
                'INSERT INTO users (name) VALUES ($name)')
            self.id = self.connection.last_insert_id()

You can think of this as a little more sophisticated than the simple API, but
not quite an Object-Relational Mapping library.

Statement API
=============
The statement API uses a new facility introduced in MySQL 5 that allows you
to pre-parse a SQL statement on the server-side, and then reuse that statement
object for higher performance.  It also provides a mechanism for streaming
BLOB objects.

See `mysql.stmt` for details and examples on using the statement API.

Exceptions
==========
All MySQL errors are mapped to error-specific exceptions so that you can
naturally catch the errors you are interested in.  See `mysql.exceptions` for
details about the exception heirarchy.

.. |copy| unicode:: 0xA9 .. copyright sign
"""

__version__ = '0.9.0a1'


__all__ = [
    'connection',
    'constants',
    'conversion',
    'exceptions',
    'result',
    'stmt',
    'util',
    'version',
]
