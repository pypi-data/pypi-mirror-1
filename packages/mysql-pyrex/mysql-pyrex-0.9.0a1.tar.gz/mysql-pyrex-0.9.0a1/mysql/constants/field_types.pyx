# $Header: /home/cvs2/mysql/mysql/constants/field_types.pyx,v 1.3 2006/08/26 20:19:51 ehuss Exp $
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

"""Identifiers of different field types.

These field type identifiers are used in a variety of places, such as the
`mysql.result.Field` object.

:Variables:
    - `TINYINT`: TINYINT field.
    - `SMALLINT`: SMALLINT field.
    - `INTEGER`: INTEGER field.
    - `MEDIUMINT`: MEDIUMINT field.
    - `BIGINT`: BIGINT field.
    - `DECIMAL`: DECIMAL or NUMERIC field.
    - `NEWDECIMAL`: Precision math DECIMAL or NUMERIC field (MySQL 5.0.3 and up).
    - `FLOAT`: FLOAT field.
    - `DOUBLE`: DOUBLE or REAL field.
    - `BIT`: BIT field (MySQL 5.0.3 and up).
    - `TIMESTAMP`: TIMESTAMP field.
    - `DATE`: DATE field.
    - `TIME`: TIME field.
    - `DATETIME`: DATETIME field.
    - `YEAR`: YEAR field.
    - `STRING`: CHAR field.
    - `VAR_STRING`: VARCHAR field.
    - `BLOB`: BLOB or TEXT field (use max_length to determine the maximum
      length).
    - `SET`: SET field.
    - `ENUM`: ENUM field.
    - `GEOMETRY`: Spatial field.
"""

__version__ = '$Revision: 1.3 $'

cimport extern_mysql

TINYINT = extern_mysql.MYSQL_TYPE_TINY
SMALLINT = extern_mysql.MYSQL_TYPE_SHORT
INTEGER = extern_mysql.MYSQL_TYPE_LONG
MEDIUMINT = extern_mysql.MYSQL_TYPE_INT24
BIGINT = extern_mysql.MYSQL_TYPE_LONGLONG
DECIMAL = extern_mysql.MYSQL_TYPE_DECIMAL
NEWDECIMAL = extern_mysql.MYSQL_TYPE_NEWDECIMAL
FLOAT = extern_mysql.MYSQL_TYPE_FLOAT
DOUBLE = extern_mysql.MYSQL_TYPE_DOUBLE
BIT = extern_mysql.MYSQL_TYPE_BIT
TIMESTAMP = extern_mysql.MYSQL_TYPE_TIMESTAMP
DATE = extern_mysql.MYSQL_TYPE_DATE
TIME = extern_mysql.MYSQL_TYPE_TIME
DATETIME = extern_mysql.MYSQL_TYPE_DATETIME
YEAR = extern_mysql.MYSQL_TYPE_YEAR
CHAR = extern_mysql.MYSQL_TYPE_STRING
VARCHAR = extern_mysql.MYSQL_TYPE_VAR_STRING
BLOB = extern_mysql.MYSQL_TYPE_BLOB
SET = extern_mysql.MYSQL_TYPE_SET
ENUM = extern_mysql.MYSQL_TYPE_ENUM
GEOMETRY = extern_mysql.MYSQL_TYPE_GEOMETRY
