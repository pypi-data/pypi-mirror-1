# $Header: /home/cvs2/mysql/mysql/constants/field_flags.pyx,v 1.3 2006/08/26 20:19:51 ehuss Exp $
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

"""Flags used in the ``flags`` attribute of the `mysql.result.Field` object.

Note that the flags attribute in the Field object may contain internally used
flags that are not documented here.

:Variables:
    - `NOT_NULL`: Field can't be NULL.
    - `PRI_KEY`: Field is part of a primary key.
    - `UNIQUE_KEY`: Field is part of a unique key.
    - `MULTIPLE_KEY`: Field is part of a non-unique key.
    - `UNSIGNED`: Field has the UNSIGNED attribute.
    - `ZEROFILL`: Field has the ZEROFILL attribute.
    - `BINARY`: Field has the BINARY attribute.
    - `AUTO_INCREMENT`: Field has the AUTO_INCREMENT attribute.
    - `KNOWN_FLAGS`: Bitwise OR of all documented flags.
"""

__version__ = '$Revision: 1.3 $'

cimport extern_mysql

NOT_NULL = extern_mysql.NOT_NULL_FLAG
PRI_KEY = extern_mysql.PRI_KEY_FLAG
UNIQUE_KEY = extern_mysql.UNIQUE_KEY_FLAG
MULTIPLE_KEY = extern_mysql.MULTIPLE_KEY_FLAG
UNSIGNED = extern_mysql.UNSIGNED_FLAG
ZEROFILL = extern_mysql.ZEROFILL_FLAG
BINARY = extern_mysql.BINARY_FLAG
AUTO_INCREMENT = extern_mysql.AUTO_INCREMENT_FLAG

KNOWN_FLAGS = (extern_mysql.NOT_NULL_FLAG |
               extern_mysql.PRI_KEY_FLAG |
               extern_mysql.UNIQUE_KEY_FLAG |
               extern_mysql.MULTIPLE_KEY_FLAG |
               extern_mysql.UNSIGNED_FLAG |
               extern_mysql.ZEROFILL_FLAG |
               extern_mysql.BINARY_FLAG |
               extern_mysql.AUTO_INCREMENT_FLAG
              )
