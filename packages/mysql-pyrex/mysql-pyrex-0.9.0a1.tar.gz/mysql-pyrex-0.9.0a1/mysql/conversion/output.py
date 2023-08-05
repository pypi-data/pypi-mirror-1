# $Header: /home/cvs2/mysql/mysql/conversion/output.py,v 1.4 2006/08/26 21:30:47 ehuss Exp $
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

"""Output Conversion converts values from MySQL (which are always strings) to Python data types.

The base class `Output_Conversion` defines the API for converting values.

The class `Basic_Conversion` is the default conversion used if you do not
specify a conversion instance.

The class `No_Conversion` may be used if you do not want any values converted.

NULL values are always converted to None, and are not passed into the
``convert`` method.
"""

__version__ = '$Revision: 1.4 $'

import datetime
import decimal
import time
from mysql.util.misc import big_str_to_host_int
from mysql.constants import field_types

class Output_Conversion:

    """Base class for the output conversion API.

    The basic requirement is to implement the `convert` method which takes the
    value and returns a Python value.
    """

    def convert(self, mysql_type, value):
        """Convert a MySQL value to a Python object.

        :Parameters:
            - `mysql_type`: The type from `mysql.constants.field_types`.
            - `value`: The value from MySQL as a string.

        :Return:
            Returns the Python object.
        """
        raise NotImplementedError


class No_Conversion(Output_Conversion):

    """Does no conversion, all values are returned as strings.

    NULL columns are returned as the string 'NULL'.
    """

    def convert(self, mysql_type, value):
        return value


class Basic_Conversion(Output_Conversion):

    """The default conversion class used if none is specified.

    It will convert the following MySQL data types:

    - Integers (TINYINT, SMALLINT, INTEGER, MEDIUMINT, BIGINT): Integers or
      Longs.
    - DECIMAL: ``decimal.Decimal``.
    - FLOAT and DOUBLE: Floating point number.
    - BIT: Integer or Long.
    - TIMESTAMP: ``datetime.datetime``.
    - DATE: ``datetime.date``.
    - TIME: ``datetime.timedelta``.
    - DATETIME: ``datetime.datetime``.
    - YEAR: Integer.
    - SET: List of strings.
    - ENUM: String.

    All other types are returned as strings.  NULL values are returned as None.
    """

    def __init__(self):
        self._type_map = {field_types.TINYINT:  self._integer,
                          field_types.SMALLINT: self._integer,
                          field_types.INTEGER: self._integer,
                          field_types.MEDIUMINT: self._integer,
                          field_types.BIGINT: self._integer,
                          field_types.FLOAT: self._float,
                          field_types.DOUBLE: self._float,
                          field_types.DECIMAL: self._decimal,
                          field_types.NEWDECIMAL: self._decimal,
                          field_types.BIT: self._bit,
                          field_types.TIMESTAMP: self._datetime,
                          field_types.DATE: self._date,
                          field_types.TIME: self._time,
                          field_types.DATETIME: self._datetime,
                          field_types.YEAR: self._integer,
                          field_types.SET: self._set,
                         }

    def convert(self, mysql_type, value):
        return self._type_map.get(mysql_type, self._string)(value)

    def _integer(self, value):
        return int(value)

    def _float(self, value):
        return float(value)

    def _string(self, value):
        return value

    def _decimal(self, value):
        return decimal.Decimal(value)

    def _bit(self, value):
        return big_str_to_host_int(value)

    def _datetime(self, value):
        st = time.strptime(value, '%Y-%m-%d %H:%M:%S')
        return datetime.datetime(st.tm_year, st.tm_mon, st.tm_mday, st.tm_hour, st.tm_min, st.tm_sec)

    def _date(self, value):
        st = time.strptime(value, '%Y-%m-%d')
        return datetime.date(st.tm_year, st.tm_mon, st.tm_mday)

    def _time(self, value):
        if value.startswith('-'):
            negative = -1
            value = value[1:]
        else:
            negative = 1
        parts = value.split(':')
        return datetime.timedelta(
            seconds= negative*(int(parts[0])*3600 + int(parts[1])*60 + int(parts[2]))
        )

    def _set(self, value):
        return value.split(',')
