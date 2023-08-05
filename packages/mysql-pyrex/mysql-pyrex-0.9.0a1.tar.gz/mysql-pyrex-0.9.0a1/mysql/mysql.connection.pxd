# $Header: /home/cvs2/mysql/mysql/mysql.connection.pxd,v 1.4 2006/08/26 20:19:51 ehuss Exp $
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

cimport extern_mysql

cdef class _Statement_Cleaner:

    cdef _statement_list

    cdef add_reference(self, extern_mysql.MYSQL_STMT * stmt)
    cdef clean(self)

cdef class Connection:

    cdef extern_mysql.MYSQL * _db
    cdef readonly object connected
    cdef readonly object paramstyle

    cdef readonly object _convert_in
    cdef readonly object _convert_out
    cdef object _param_formatter

    cdef object _unbuffered_result
    cdef object _unbuffered_statement
    cdef _check_unbuffered_result(self, stmt)

    cdef _Statement_Cleaner _old_statements

    cdef _init_db(self)
    cdef _escape_args(self, args)
    cdef _escape_kwargs(self, kwargs)
    cdef _return_statement_result(self, store_result)
