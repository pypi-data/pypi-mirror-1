# $Header: /home/cvs2/mysql/test/test_performance.py,v 1.3 2006/08/26 20:19:52 ehuss Exp $
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

"""Performance unittests.

Run these with -v to see the elapsed time for each one.

XXX: Should add rusage data.
"""

__version__ = '$Revision: 1.3 $'

import time
import unittest

import base_test
import mysql.stmt.bind_in as bi
import mysql.stmt.bind_out as bo

class Empty:
    pass

repeat_count = 10000

class Test(base_test.Base_Mysql_Test_Case2):

    def test_insert(self):
        """Test normal insert."""
        start = time.time()
        values = {'tiny': 3,
                  'i': 7,
                  'bigi': 0x123456789,
                  'vc': 'Hi there',
                 }
        for x in xrange(repeat_count):
            self.connection.execute("""INSERT INTO test1 (tiny, i, bigi, vc) VALUES ($tiny, $i, $bigi, $vc)""", **values)
        end = time.time()
        print end - start

    def test_stmt_insert(self):
        """Test statement insert."""
        start = time.time()
        s = self.connection.new_statement("""INSERT INTO test1 (tiny, i, bigi, vc) VALUES (?, ?, ?, ?)""")
        container = Empty()
        s.bind_input(bi.In_Tiny_Int(container, 'tiny'),
                     bi.In_Int(container, 'i'),
                     bi.In_Big_Int(container, 'bigi'),
                     bi.In_Varchar(container, 'vc', 100),
                    )
        container.tiny = 3
        container.i = 7
        container.bigi = 0x123456789
        container.vc = 'Hi there'

        for x in xrange(repeat_count):
            s.execute()

        end = time.time()
        print end - start

    def test_stmt_insert2(self):
        """Test statement insert (rebuilding statements)."""
        start = time.time()
        container = Empty()
        container.tiny = 3
        container.i = 7
        container.bigi = 0x123456789
        container.vc = 'Hi there'
        for x in xrange(repeat_count):
            s = self.connection.new_statement("""INSERT INTO test1 (tiny, i, bigi, vc) VALUES (?, ?, ?, ?)""")
            s.bind_input(bi.In_Tiny_Int(container, 'tiny'),
                         bi.In_Int(container, 'i'),
                         bi.In_Big_Int(container, 'bigi'),
                         bi.In_Varchar(container, 'vc', 100),
                        )

            s.execute()

        end = time.time()
        print end - start

    def test_container(self):
        """Test container API insert."""
        class test1:

            def __init__(self, connection):
                self.connection = connection

            def store(self):
                self.connection.exec_container(self, """INSERT INTO test1 (tiny, i, bigi, vc) VALUES ($tiny, $i, $bigi, $vc)""")

        start = time.time()
        c = test1(self.connection)
        c.tiny = 3
        c.i = 7
        c.bigi = 0x123456789
        c.vc = 'Hi there'
        for x in xrange(repeat_count):
            c.store()
        end = time.time()
        print end - start

if __name__ == '__main__':
    unittest.main()
