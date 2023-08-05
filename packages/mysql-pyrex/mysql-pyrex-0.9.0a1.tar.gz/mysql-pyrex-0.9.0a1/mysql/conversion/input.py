# $Header: /home/cvs2/mysql/mysql/conversion/input.py,v 1.5 2006/08/26 22:30:06 ehuss Exp $
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

"""Input Conversion converts Python data types to be made appropriate for MySQL
parameters.

The main function of these conversions for simple data types is to escape them
(such as escaping quotes in strings).  It also handles converting more
elaborate data structures, such as `datetime` objects, to strings that MySQL
can parse.

The base class `Input_Conversion` defines the API for converting values.

The class `Basic_Conversion` is the default conversion used if you do not specify
a conversion instance.
"""

__version__ = '$Revision: 1.5 $'

import datetime
import decimal
import sets
import types

import mysql.util.string

class Input_Conversion:

    """Base class for the input conversion API.

    The basic requirement is to implement the `convert` method which takes the
    values and must return a tuple of strings.
    """

    def convert(self, *values):
        """Convert Python values to strings suitable for MySQL.

        This method takes a sequence of Python values to convert. It must
        return a tuple of strings suitable for MySQL, with all appropriate
        escaping done.

        :Parameters:
            - `values`: A tuple of Python values to convert.

        :Return:
            Returns a tuple of strings.
        """
        raise NotImplementedError


class Basic_Conversion(Input_Conversion):

    """The default conversion class used if none is specified.

    It can handle the following Python types:

    - ``int``: Returned as-is.
    - ``long``: Returned as-is.
    - ``float``: Returned as-is.
    - ``None``: Converts to "NULL".
    - ``str``: Escaped string.
    - ``bool``: Converted to 1 or 0.
    - ``decimal.Decimal``: Returned as a string.
    - ``dict``: Comma seperated list of escaped values. (Useful for sets.)
    - ``list``: Comma seperated list of escaped values.
    - ``tuple``: Comma seperated list of escaped values.
    - ``sets.Set``: Comma seperated list of escaped values.
    - ``datetime.datetime``: ``%Y-%m-%d %H:%M:%S``
    - ``datetime.time``: ``%H:%M:%S``
    - ``datetime.timedelta``: ``%H:%M:%S`` possibly negative.
    - ``datetime.date``: ``%Y-%m-%d``

    For MySQL "BIT" fields, you may use integers, or binary strings (such as
    '\x10\x04' which has bits 13 and 3 set).

    If the type is not known, the default behavior is to first call ``str`` on
    the object, and then escape it.
    """

    def __init__(self):
        self._type_map = {int:      self._number,
                          long:     self._number,
                          float:    self._number,
                          types.NoneType: self._none,
                          str:      mysql.util.string.escape,
                          decimal.Decimal: str,
                          dict: self._dict,
                          list: self._sequence,
                          tuple: self._sequence,
                          sets.Set: self._sequence,
                          datetime.datetime: self._datetime,
                          datetime.time: self._time,
                          datetime.timedelta: self._timedelta,
                          datetime.date: self._date,
                          bool: self._bool,
                         }

    def convert(self, *values):
        return tuple([ self._type_map.get(type(value), self._escape)(value) for value in values ])

    def _number(self, value):
        return value

    def _bool(self, value):
        return int(value)

    def _none(self, value):
        return 'NULL'

    def _escape(self, value):
        return mysql.util.string.escape(str(value))

    def _dict(self, value):
        return self._sequence(value.keys())

    def _sequence(self, value):
        return mysql.util.string.escape(
            ','.join([ v for v in value ])
        )

    def _datetime(self, value):
        return value.strftime('\'%Y-%m-%d %H:%M:%S\'')

    def _time(self, value):
        return value.strftime('\'%H:%M:%S\'')

    def _timedelta(self, value):
        # Denormalize.
        if value.days < 0:
            value = -value
            neg = '-'
        else:
            neg = ''

        hours = value.days*24 + value.seconds/3600

        if hours > 838:
            raise OverflowError('Time value is too large.')
        minutes = (value.seconds % 3600) / 60
        seconds = value.seconds % 60

        return '\'%s%i:%i:%i\'' % (neg, hours, minutes, seconds)

    def _date(self, value):
        return value.strftime('\'%Y-%m-%d\'')
