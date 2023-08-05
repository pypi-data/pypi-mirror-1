# $Header: /home/cvs2/mysql/test/test_stmt.py,v 1.5 2006/08/26 20:19:52 ehuss Exp $
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

"""Unittests for mysql.stmt API."""

__version__ = '$Revision: 1.5 $'

import datetime
import decimal
import sets
import time
import unittest

import base_test
import mysql.constants
import mysql.exceptions
import mysql.stmt
import mysql.stmt.bind_in as bi
import mysql.stmt.bind_out as bo
import mysql.result

class Empty:
    pass

class Test(base_test.Base_Mysql_Test_Case2):

    def test_all(self):
        """Basic statement test."""
        # Excluded are:
        # - DECIMAL (see test_decimal)
        # - DATE/DATETIME/TIMESTAMP/TIME/YEAR (see test_time)
        # - ENUM (see test_enum)
        # - SET (see test_set)
        s = self.connection.new_statement("""
            INSERT INTO test1 (
                                utiny,
                                tiny,
                                usmall,
                                small,
                                umedium,
                                medium,
                                ui,
                                i,
                                ubigi,
                                bigi,
                                bits,
                                boo,
                                uflo,
                                flo,
                                udoub,
                                doub,
                                vc,
                                vbin,
                                blob_tiny,
                                blob_medium,
                                blob_blob,
                                blob_long,
                                text_tiny,
                                text_medium,
                                text_text,
                                text_long
                              ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """)
        self.assertEqual(s.get_param_count(), 26)
        container = Empty()
        s.bind_input(bi.In_U_Tiny_Int(container, 'utiny'),
                     bi.In_Tiny_Int(container, 'tiny'),
                     bi.In_U_Small_Int(container, 'usmall'),
                     bi.In_Small_Int(container, 'small'),
                     bi.In_U_Medium_Int(container, 'umedium'),
                     bi.In_Medium_Int(container, 'medium'),
                     bi.In_U_Int(container, 'ui'),
                     bi.In_Int(container, 'i'),
                     bi.In_U_Big_Int(container, 'ubigi'),
                     bi.In_Big_Int(container, 'bigi'),
                     bi.In_Bit(container, 'bits'),
                     bi.In_Bool(container, 'boo'),
                     bi.In_U_Float(container, 'uflo'),
                     bi.In_Float(container, 'flo'),
                     bi.In_U_Double(container, 'udoub'),
                     bi.In_Double(container, 'doub'),
                     bi.In_Varchar(container, 'vc', 100),
                     bi.In_Varbinary(container, 'vbin', 100),
                     bi.In_Tiny_Blob(container, 'blob_tiny', use_stream=1),
                     bi.In_Medium_Blob(container, 'blob_medium', use_stream=1),
                     bi.In_Blob(container, 'blob_blob', use_stream=1),
                     bi.In_Long_Blob(container, 'blob_long', use_stream=1),
                     bi.In_Tiny_Text(container, 'text_tiny', use_stream=1),
                     bi.In_Medium_Text(container, 'text_medium', use_stream=1),
                     bi.In_Text(container, 'text_text', use_stream=1),
                     bi.In_Long_Text(container, 'text_long', use_stream=1),
                    )
        container.utiny = 1
        container.tiny = -1
        container.usmall = 2
        container.small = -2
        container.umedium = 5
        container.medium = -5
        container.ui = 3
        container.i = -3
        container.ubigi = 4
        container.bigi = -4
        #container.bits = '\x12\x34\x56\x78\x9a\xbc\xde\xff'
        container.bits = 1311768467463790335
        container.boo = True
        container.uflo = 3.14
        container.flo = -3.14
        container.udoub = 2.718
        container.doub = -2.718
        container.vc = 'Variable'
        container.vbin = 'Bin\x00ary\x01\x02'
        container.blob_tiny.write('I\'m very tiny.')
        container.blob_medium.write('Medium.')
        container.blob_blob.write('Blobby.')
        container.blob_long.write('Huge.')

        container.text_tiny.write('one')
        container.text_medium.write('two')
        container.text_text.write('three')
        container.text_long.write('four')

        s.execute()
        self.assertEqual(s.insert_id(), 1)

        container.utiny = 255
        container.tiny = 127
        container.usmall = 65535
        container.small = 32767
        container.umedium = 16777215
        container.medium = 8388607
        container.ui = 4294967295
        container.i = 2147483647
        container.ubigi = 18446744073709551615
        container.bigi = 9223372036854775807
        #container.bits = '\x01'
        container.bits = 1
        container.boo = False
        container.uflo = 1.414
        container.flo = -1.414
        container.udoub = 0.577
        container.doub = -0.577
        container.vc = 'i am varchar'
        container.vbin = ''
        container.blob_tiny.write('i am tiny')
        container.blob_medium.write('i am medium')
        container.blob_blob.write('i am normal')
        container.blob_long.write('i am long')

        container.text_tiny.write('text tiny')
        container.text_medium.write('text medium')
        container.text_text.write('text text')
        container.text_long.write('text long')

        s.execute()
        self.assertEqual(s.insert_id(), 2)

        container.utiny = 0
        container.tiny = -128
        container.usmall = 0
        container.small = -32768
        container.umedium = 0
        container.medium = -8388608
        container.ui = 0
        container.i = -2147483648
        container.ubigi = 0
        container.bigi = -9223372036854775808
        #container.bits = ''
        container.bits = 0
        container.boo = 0
        container.uflo = 0
        container.flo = 0
        container.udoub = 0
        container.doub = 0

        s.execute()
        self.assertEqual(s.insert_id(), 3)

        # Insert all NULL's
        container.utiny = None
        container.tiny = None
        container.usmall = None
        container.small = None
        container.umedium = None
        container.medium = None
        container.ui = None
        container.i = None
        container.ubigi = None
        container.bigi = None
        container.bits = None
        container.boo = None
        container.uflo = None
        container.flo = None
        container.udoub = None
        container.doub = None
        container.vc = None
        container.vbin = None

        s.execute()
        self.assertEqual(s.insert_id(), 4)

        s = self.connection.new_statement("""SELECT id,
                                                    utiny,
                                                    tiny,
                                                    usmall,
                                                    small,
                                                    umedium,
                                                    medium,
                                                    ui,
                                                    i,
                                                    ubigi,
                                                    bigi,
                                                    bits,
                                                    boo,
                                                    uflo,
                                                    flo,
                                                    udoub,
                                                    doub,
                                                    vc,
                                                    vbin,
                                                    blob_tiny,
                                                    blob_medium,
                                                    blob_blob,
                                                    blob_long,
                                                    text_tiny,
                                                    text_medium,
                                                    text_text,
                                                    text_long
                                                        FROM test1 ORDER BY id""")
        container = Empty()
        s.bind_output(bo.Out_Int(container, 'id'),
                      bo.Out_U_Tiny_Int(container, 'utiny'),
                      bo.Out_Tiny_Int(container, 'tiny'),
                      bo.Out_U_Small_Int(container, 'usmall'),
                      bo.Out_Small_Int(container, 'small'),
                      bo.Out_U_Medium_Int(container, 'umedium'),
                      bo.Out_Medium_Int(container, 'medium'),
                      bo.Out_U_Int(container, 'ui'),
                      bo.Out_Int(container, 'i'),
                      bo.Out_U_Big_Int(container, 'ubigi'),
                      bo.Out_Big_Int(container, 'bigi'),
                      bo.Out_Bit(container, 'bits'),
                      bo.Out_Bool(container, 'boo'),
                      bo.Out_U_Float(container, 'uflo'),
                      bo.Out_Float(container, 'flo'),
                      bo.Out_U_Double(container, 'udoub'),
                      bo.Out_Double(container, 'doub'),
                      bo.Out_Varchar(container, 'vc', 100),
                      bo.Out_Varbinary(container, 'vbin', 100),
                      bo.Out_Tiny_Blob(container, 'blob_tiny', 100),
                      bo.Out_Medium_Blob(container, 'blob_medium', 100),
                      bo.Out_Blob(container, 'blob_blob', 100),
                      bo.Out_Long_Blob(container, 'blob_long', 100),
                      bo.Out_Tiny_Text(container, 'text_tiny', 100),
                      bo.Out_Medium_Text(container, 'text_medium', 100),
                      bo.Out_Text(container, 'text_text', 100),
                      bo.Out_Long_Text(container, 'text_long', 100),
                     )
        s.execute()
        s.fetch()
        self.assertEqual(container.id, 1)
        self.assertEqual(container.utiny, 1)
        self.assertEqual(container.tiny, -1)
        self.assertEqual(container.usmall, 2)
        self.assertEqual(container.small, -2)
        self.assertEqual(container.umedium, 5)
        self.assertEqual(container.medium, -5)
        self.assertEqual(container.ui, 3)
        self.assertEqual(container.i, -3)
        self.assertEqual(container.ubigi, 4)
        self.assertEqual(container.bigi, -4)
        self.assertEqual(container.bits, 1311768467463790335)
        self.assertTrue(container.boo)
        self.assertAlmostEqual(container.uflo, 3.14, 4)
        self.assertAlmostEqual(container.flo, -3.14, 4)
        self.assertAlmostEqual(container.udoub, 2.718, 4)
        self.assertAlmostEqual(container.doub, -2.718, 4)
        self.assertEqual(container.vc, 'Variable')
        self.assertEqual(container.vbin, 'Bin\x00ary\x01\x02')
        self.assertEqual(container.blob_tiny, 'I\'m very tiny.')
        self.assertEqual(container.blob_medium, 'Medium.')
        self.assertEqual(container.blob_blob, 'Blobby.')
        self.assertEqual(container.blob_long, 'Huge.')
        self.assertEqual(container.text_tiny, 'one')
        self.assertEqual(container.text_medium, 'two')
        self.assertEqual(container.text_text, 'three')
        self.assertEqual(container.text_long, 'four')

        s.fetch()
        self.assertEqual(container.id, 2)
        self.assertEqual(container.utiny, 255)
        self.assertEqual(container.tiny, 127)
        self.assertEqual(container.usmall, 65535)
        self.assertEqual(container.small, 32767)
        self.assertEqual(container.umedium, 16777215)
        self.assertEqual(container.medium, 8388607)
        self.assertEqual(container.ui, 4294967295)
        self.assertEqual(container.i, 2147483647)
        self.assertEqual(container.ubigi, 18446744073709551615)
        self.assertEqual(container.bigi, 9223372036854775807)
        self.assertEqual(container.bits, 1)
        self.assertFalse(container.boo)
        self.assertAlmostEqual(container.uflo, 1.414, 4)
        self.assertAlmostEqual(container.flo, -1.414, 4)
        self.assertAlmostEqual(container.udoub, 0.577, 4)
        self.assertAlmostEqual(container.doub, -0.577, 4)
        self.assertEqual(container.vc, 'i am varchar')
        self.assertEqual(container.vbin, '')
        self.assertEqual(container.blob_tiny, 'i am tiny')
        self.assertEqual(container.blob_medium, 'i am medium')
        self.assertEqual(container.blob_blob, 'i am normal')
        self.assertEqual(container.blob_long, 'i am long')
        self.assertEqual(container.text_tiny, 'text tiny')
        self.assertEqual(container.text_medium, 'text medium')
        self.assertEqual(container.text_text, 'text text')
        self.assertEqual(container.text_long, 'text long')

        s.fetch()
        self.assertEqual(container.id, 3)
        self.assertEqual(container.utiny, 0)
        self.assertEqual(container.tiny, -128)
        self.assertEqual(container.usmall, 0)
        self.assertEqual(container.small, -32768)
        self.assertEqual(container.umedium, 0)
        self.assertEqual(container.medium, -8388608)
        self.assertEqual(container.ui, 0)
        self.assertEqual(container.i, -2147483648)
        self.assertEqual(container.ubigi, 0)
        self.assertEqual(container.bigi, -9223372036854775808)
        self.assertEqual(container.bits, 0)
        self.assertFalse(container.boo)
        self.assertAlmostEqual(container.uflo, 0, 4)
        self.assertAlmostEqual(container.flo, 0, 4)
        self.assertAlmostEqual(container.udoub, 0, 4)
        self.assertAlmostEqual(container.doub, 0, 4)
        self.assertEqual(container.vc, 'i am varchar')
        self.assertEqual(container.vbin, '')
        self.assertEqual(container.blob_tiny, None)
        self.assertEqual(container.blob_medium, None)
        self.assertEqual(container.blob_blob, None)
        self.assertEqual(container.blob_long, None)
        self.assertEqual(container.text_tiny, None)
        self.assertEqual(container.text_medium, None)
        self.assertEqual(container.text_text, None)
        self.assertEqual(container.text_long, None)

        s.fetch()
        self.assertEqual(container.id, 4)
        self.assertEqual(container.utiny, None)
        self.assertEqual(container.tiny, None)
        self.assertEqual(container.usmall, None)
        self.assertEqual(container.small, None)
        self.assertEqual(container.umedium, None)
        self.assertEqual(container.medium, None)
        self.assertEqual(container.ui, None)
        self.assertEqual(container.i, None)
        self.assertEqual(container.ubigi, None)
        self.assertEqual(container.bigi, None)
        self.assertEqual(container.bits, None)
        self.assertEqual(container.boo, None)
        self.assertEqual(container.uflo, None)
        self.assertEqual(container.flo, None)
        self.assertEqual(container.udoub, None)
        self.assertEqual(container.doub, None)
        self.assertEqual(container.vc, None)
        self.assertEqual(container.vbin, None)
        self.assertEqual(container.blob_tiny, None)
        self.assertEqual(container.blob_medium, None)
        self.assertEqual(container.blob_blob, None)
        self.assertEqual(container.blob_long, None)
        self.assertEqual(container.text_tiny, None)
        self.assertEqual(container.text_medium, None)
        self.assertEqual(container.text_text, None)
        self.assertEqual(container.text_long, None)

        self.assertRaises(mysql.exceptions.No_More_Rows, s.fetch)
        self.assertEqual(s.sqlstate(), '00000')

        # Do char test.
        s = self.connection.new_statement("""INSERT INTO test2 (c, bin) VALUES (?, ?)""")
        container = Empty()
        s.bind_input(bi.In_Char(container, 'c', 100),
                     bi.In_Binary(container, 'bin', 100),
                    )
        container.c = 'foo'
        container.bin = '\xff'
        s.execute()
        container.c = 'bar'
        container.bin = '\x00'
        s.execute()

        s = self.connection.new_statement("""SELECT id, c, bin FROM test2 ORDER BY id""")
        container = Empty()
        s.bind_output(bo.Out_U_Int(container, 'id'),
                      bo.Out_Char(container, 'c', 100),
                      bo.Out_Binary(container, 'bin', 100),
                      )
        s.execute()
        s.fetch()
        self.assertEqual(container.id, 1)
        self.assertEqual(container.c, 'foo')
        self.assertEqual(container.bin, '\xff' + '\x00'*99)
        s.fetch()
        self.assertEqual(container.id, 2)
        self.assertEqual(container.c, 'bar')
        self.assertEqual(container.bin, '\x00' + '\x00'*99)
        self.assertRaises(mysql.exceptions.No_More_Rows, s.fetch)

    def test_enum(self):
        """Test enum data type."""
        s = self.connection.new_statement("""INSERT INTO test1 (e) VALUES (?)""")
        container = Empty()
        s.bind_input(bi.In_Enum(container, 'e', 100))
        container.e = 'one'
        s.execute()
        container.e = '2'
        s.execute()
        container.e = 3
        s.execute()
        container.e = 4L
        s.execute()
        container.e = 'a'*101
        self.assertRaises(OverflowError, s.execute)

        s = self.connection.new_statement("""SELECT e FROM test1 ORDER BY id""")
        container = Empty()
        s.bind_output(bo.Out_Enum(container, 'e', 100))
        s.execute()
        s.fetch()
        self.assertEqual(container.e, 'one')
        s.fetch()
        self.assertEqual(container.e, 'two')
        s.fetch()
        self.assertEqual(container.e, 'three')
        s.fetch()
        self.assertEqual(container.e, 'four')

        self.assertRaises(mysql.exceptions.No_More_Rows, s.fetch)

        s = self.connection.new_statement("""SELECT e+0 FROM test1 ORDER BY id""")
        container = Empty()
        s.bind_output(bo.Out_Enum(container, 'e', 100))
        s.execute()
        s.fetch()
        self.assertEqual(container.e, '1')
        s.fetch()
        self.assertEqual(container.e, '2')
        s.fetch()
        self.assertEqual(container.e, '3')
        s.fetch()
        self.assertEqual(container.e, '4')

        self.assertRaises(mysql.exceptions.No_More_Rows, s.fetch)

    def test_set(self):
        """Test set data type."""
        s = self.connection.new_statement("""INSERT INTO test1 (s) VALUES (?)""")
        container = Empty()
        s.bind_input(bi.In_Set(container, 's', 100))
        container.s = 'red'
        s.execute()
        container.s = 'red,green'
        s.execute()
        container.s = 7
        s.execute()
        container.s = sets.Set(['green', 'blue'])
        s.execute()
        container.s = 5L
        s.execute()
        container.s = {'red':True, 'green':True}
        s.execute()
        container.s = ['blue', 'green']
        s.execute()
        container.s = ('red', 'green')
        s.execute()
        class Foo:
            def __init__(self):
                self.x = ('red', 'blue')
            def keys(self):
                return self.x
        f = Foo()
        container.s = f
        s.execute()
        container.s = 'a'*101
        self.assertRaises(OverflowError, s.execute)

        s = self.connection.new_statement("""SELECT s FROM test1 ORDER BY id""")
        container = Empty()
        s.bind_output(bo.Out_Set(container, 's', 100))
        s.execute()
        s.fetch()
        self.assertEqual(container.s, sets.Set(('red',)))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('red', 'green')))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('red', 'green', 'blue')))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('green', 'blue')))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('red', 'blue')))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('red', 'green')))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('green', 'blue')))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('red', 'green')))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('red', 'blue')))

        self.assertRaises(mysql.exceptions.No_More_Rows, s.fetch)

        s = self.connection.new_statement("""SELECT s+0 FROM test1 ORDER BY id""")
        container = Empty()
        s.bind_output(bo.Out_Set(container, 's', 100))
        s.execute()
        s.fetch()
        self.assertEqual(container.s, sets.Set(('1',)))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('3',)))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('7',)))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('6',)))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('5',)))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('3',)))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('6',)))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('3',)))
        s.fetch()
        self.assertEqual(container.s, sets.Set(('5',)))

        self.assertRaises(mysql.exceptions.No_More_Rows, s.fetch)

    def test_decimal(self):
        """Test decimal data type."""
        s = self.connection.new_statement("""INSERT INTO test1 (udeci, deci) VALUES (?, ?)""")
        container = Empty()
        testcount = 1
        if self.connection.get_server_version() < 50019:
            # Decimal input binding is broken, see bug #16511.
            s.bind_input(bi.In_Varchar(container, 'udeci', 100),
                         bi.In_Varchar(container, 'deci', 100)
                        )
            container.udeci = '1.1'
            container.deci = '-1.1'
            s.execute()
            container.udeci = '12345678901234567890123456789012345.678901234567890123456789012345'
            container.deci = '-12345678901234567890123456789012345.678901234567890123456789012345'
            s.execute()
            container.udeci = '2.8'
            container.deci = '-12.43'
            s.execute()
            container.udeci = None
            container.deci = None
            s.execute()
        else:
            testcount = 2
            s.bind_input(bi.In_U_Decimal(container, 'udeci'),
                         bi.In_Decimal(container, 'deci')
                        )

            def doit(s):
                container.udeci = decimal.Decimal('1.1')
                container.deci = decimal.Decimal('-1.1')
                s.execute()
                container.udeci = decimal.Decimal('12345678901234567890123456789012345.678901234567890123456789012345')
                container.deci = decimal.Decimal('-12345678901234567890123456789012345.678901234567890123456789012345')
                s.execute()
                container.udeci = decimal.Decimal('2.8')
                container.deci = decimal.Decimal('-12.43')
                s.execute()
                container.udeci = None
                container.deci = None
                s.execute()
                container.udeci = '1.1'
                container.deci = '-1.1'
                self.assertRaises(TypeError, s.execute)
                container.udeci = decimal.Decimal('-1')
                container.deci = decimal.Decimal('1')
                self.assertRaises(OverflowError, s.execute)
                container.udeci = decimal.Decimal('1234567890123456789012345678901234567890123456789012345678901234567890')
                self.assertRaises(OverflowError, s.execute)

            doit(s)

            # Test "new" decimal.
            s = self.connection.new_statement("""INSERT INTO test1 (udeci, deci) VALUES (?, ?)""")
            s.bind_input(bi.In_U_New_Decimal(container, 'udeci'),
                         bi.In_New_Decimal(container, 'deci')
                        )

            doit(s)

        s = self.connection.new_statement("""SELECT udeci, deci FROM test1 ORDER BY id""")
        container = Empty()
        s.bind_output(bo.Out_U_Decimal(container, 'udeci'),
                      bo.Out_Decimal(container, 'deci')
                     )

        def doit(s):
            s.execute()
            for unused in xrange(testcount):
                s.fetch()
                self.assertEqual(container.udeci, decimal.Decimal('1.1'))
                self.assertEqual(container.deci, decimal.Decimal('-1.1'))
                s.fetch()
                self.assertEqual(container.udeci, decimal.Decimal('12345678901234567890123456789012345.678901234567890123456789012345'))
                self.assertEqual(container.deci, decimal.Decimal('-12345678901234567890123456789012345.678901234567890123456789012345'))
                s.fetch()
                self.assertEqual(container.udeci, decimal.Decimal('2.8'))
                self.assertEqual(container.deci, decimal.Decimal('-12.43'))
                s.fetch()
                self.assertEqual(container.udeci, None)
                self.assertEqual(container.deci, None)

            self.assertRaises(mysql.exceptions.No_More_Rows, s.fetch)

        doit(s)

        s = self.connection.new_statement("""SELECT udeci, deci FROM test1 ORDER BY id""")
        container = Empty()
        s.bind_output(bo.Out_U_New_Decimal(container, 'udeci'),
                      bo.Out_New_Decimal(container, 'deci')
                     )
        doit(s)


    def test_blob(self):
        """Test blob streaming."""
        container = Empty()
        s = self.connection.new_statement("""INSERT INTO test1 (blob_long, blob_blob, blob_tiny) VALUES (?, ?, ?)""")
        s.bind_input(bi.In_Long_Blob(container, 'blob_long', use_stream=True),
                     bi.In_Blob(container, 'blob_blob', use_stream=True),
                     bi.In_Blob(container, 'blob_tiny')
                    )
        for x in xrange(1024):
            char = chr(97 + (x % 26))
            block = char * 1024
            container.blob_long.write(block)
        s.execute()

        s = self.connection.new_statement("""SELECT blob_long, blob_blob, blob_tiny FROM test1""")
        container = Empty()
        s.bind_output(bo.Out_Long_Blob(container, 'blob_long', 100, store_stream=True),
                      bo.Out_Blob(container, 'blob_blob', 100, store_stream=True),
                      bo.Out_Tiny_Blob(container, 'blob_tiny', 100),
                     )
        s.execute()
        s.fetch()
        for x in xrange(1024):
            char = chr(97 + (x % 26))
            expected_block = char * 1024
            block = container.blob_long.read(1024)
            self.assertEqual(block, expected_block)
        self.assertEqual(container.blob_long.read(1024), '')
        self.assertEqual(container.blob_blob, None)
        self.assertEqual(container.blob_tiny, None)

        # Test reading all at once.
        s.execute()
        s.fetch()
        data = container.blob_long.read()
        result = []
        for x in xrange(1024):
            char = chr(97 + (x % 26))
            expected_block = char * 1024
            result.append(expected_block)
        expected_data = ''.join(result)
        self.assertEqual(data, expected_data)

    def test_empty_blob(self):
        """Test empty blob."""
        container = Empty()
        s = self.connection.new_statement("""INSERT INTO test1 (blob_blob) VALUES (?)""")
        s.bind_input(bi.In_Blob(container, 'blob_blob', use_stream=True))
        s.execute()
        container.blob_blob.write('')
        s.execute()

        container = Empty()
        s = self.connection.new_statement("""INSERT INTO test1 (blob_blob) VALUES (?)""")
        s.bind_input(bi.In_Blob(container, 'blob_blob', use_stream=False))
        container.blob_blob = ''
        s.execute()
        container.blob_blob = None
        s.execute()

        container = Empty()
        s = self.connection.new_statement("""SELECT blob_blob FROM test1 ORDER BY id""")
        s.bind_output(bo.Out_Blob(container, 'blob_blob', store_stream=False))
        s.execute()
        s.fetch()
        self.assertEqual(container.blob_blob, None)
        s.fetch()
        self.assertEqual(container.blob_blob, '')
        s.fetch()
        self.assertEqual(container.blob_blob, '')
        s.fetch()
        self.assertEqual(container.blob_blob, None)
        self.assertRaises(mysql.exceptions.No_More_Rows, s.fetch)

    def test_time(self):
        """Test time types."""
        # XXX: How to insert/select as ints or strings.
        s = self.connection.new_statement("""INSERT INTO test1 (dt_date, dt_datetime, dt_timestamp, dt_time, dt_year) VALUES (?, ?, ?, ?, ?)""")
        container = Empty()
        s.bind_input(bi.In_Date(container, 'dt_date'),
                     bi.In_Date_Time(container, 'dt_datetime'),
                     bi.In_Timestamp(container, 'dt_timestamp'),
                     bi.In_Time(container, 'dt_time'),
                     bi.In_Year(container, 'dt_year'),
                    )
        container.dt_date = datetime.date(year=2006, month=1, day=16)
        container.dt_datetime = datetime.datetime(year=2006, month=1, day=16, hour=13, minute=56, second=25)
        container.dt_timestamp = datetime.datetime(year=2001, month=1, day=1, hour=0, minute=0, second=0)
        container.dt_time = datetime.time(hour=12, minute=30, second=15)
        container.dt_year = 2006
        s.execute()

        container.dt_date = None
        container.dt_datetime = None
        container.dt_timestamp = None
        container.dt_time = None
        container.dt_year = None
        s.execute()

        container.dt_time = datetime.timedelta(days=-1)
        s.execute()
        container.dt_time = datetime.timedelta(hours=-1)
        s.execute()
        container.dt_time = datetime.timedelta(minutes=-1)
        s.execute()
        container.dt_time = datetime.timedelta(seconds=-1)
        s.execute()
        container.dt_time = datetime.timedelta(days=1)
        s.execute()
        container.dt_time = datetime.timedelta(hours=1)
        s.execute()
        container.dt_time = datetime.timedelta(minutes=1)
        s.execute()
        container.dt_time = datetime.timedelta(seconds=1)
        s.execute()
        container.dt_time = datetime.timedelta(hours=839)
        self.assertRaises(OverflowError, s.execute)
        container.dt_time = datetime.timedelta(hours=-839)
        self.assertRaises(OverflowError, s.execute)

        s = self.connection.new_statement("""SELECT dt_date, dt_datetime, dt_timestamp, dt_time, dt_year FROM test1 ORDER BY id""")
        container = Empty()
        s.bind_output(bo.Out_Date(container, 'dt_date'),
                      bo.Out_Date_Time(container, 'dt_datetime'),
                      bo.Out_Timestamp(container, 'dt_timestamp'),
                      bo.Out_Time(container, 'dt_time'),
                      bo.Out_Year(container, 'dt_year'),
                     )
        s.execute()
        s.fetch()
        self.assertEqual(container.dt_date, datetime.date(year=2006, month=1, day=16))
        self.assertEqual(container.dt_datetime, datetime.datetime(year=2006, month=1, day=16, hour=13, minute=56, second=25))
        self.assertEqual(container.dt_timestamp, datetime.datetime(year=2001, month=1, day=1, hour=0, minute=0, second=0))
        self.assertEqual(container.dt_time, datetime.timedelta(hours=12, minutes=30, seconds=15))
        self.assertEqual(container.dt_year, 2006)

        s.fetch()
        self.assertEqual(container.dt_date, None)
        self.assertEqual(container.dt_datetime, None)
        # Inserting a NULL into a TIMESTAMP field inserts the current time.
        self.assertTrue(isinstance(container.dt_timestamp, datetime.datetime))
        self.assertEqual(container.dt_time, None)
        self.assertEqual(container.dt_year, None)

        s.fetch()
        self.assertEqual(container.dt_time, datetime.timedelta(days=-1))
        s.fetch()
        self.assertEqual(container.dt_time, datetime.timedelta(hours=-1))
        s.fetch()
        self.assertEqual(container.dt_time, datetime.timedelta(minutes=-1))
        s.fetch()
        self.assertEqual(container.dt_time, datetime.timedelta(seconds=-1))
        s.fetch()
        self.assertEqual(container.dt_time, datetime.timedelta(days=1))
        s.fetch()
        self.assertEqual(container.dt_time, datetime.timedelta(hours=1))
        s.fetch()
        self.assertEqual(container.dt_time, datetime.timedelta(minutes=1))
        s.fetch()
        self.assertEqual(container.dt_time, datetime.timedelta(seconds=1))

        self.assertRaises(mysql.exceptions.No_More_Rows, s.fetch)

    def test_time_int(self):
        """Test time as integers."""
        s = self.connection.new_statement("""INSERT INTO test1 (dt_date, dt_datetime, dt_timestamp, dt_time, dt_year) VALUES (?, ?, ?, ?, ?)""")
        container = Empty()
        s.bind_input(bi.In_Int(container, 'dt_date'),
                     bi.In_Big_Int(container, 'dt_datetime'),
                     bi.In_Big_Int(container, 'dt_timestamp'),
                     bi.In_Int(container, 'dt_time'),
                     bi.In_Small_Int(container, 'dt_year'),
                    )
        container.dt_date = 20060116
        container.dt_datetime = 20060116143712
        container.dt_timestamp = 20060101123030
        container.dt_time = 143730
        container.dt_year = 2006
        s.execute()

        s = self.connection.new_statement("""SELECT dt_date, dt_datetime, dt_timestamp, dt_time, dt_year FROM test1 ORDER BY id""")
        container = Empty()
        s.bind_output(bo.Out_Int(container, 'dt_date'),
                      bo.Out_Big_Int(container, 'dt_datetime'),
                      bo.Out_Big_Int(container, 'dt_timestamp'),
                      bo.Out_Int(container, 'dt_time'),
                      bo.Out_Small_Int(container, 'dt_year'),
                     )
        s.execute()
        s.fetch()
        self.assertEqual(container.dt_date, 20060116)
        self.assertEqual(container.dt_datetime, 20060116143712)
        self.assertEqual(container.dt_timestamp, 20060101123030)
        self.assertEqual(container.dt_time, 143730)
        self.assertEqual(container.dt_year, 2006)
        self.assertRaises(mysql.exceptions.No_More_Rows, s.fetch)

    def test_time_str(self):
        """Test time as strings."""
        s = self.connection.new_statement("""INSERT INTO test1 (dt_date, dt_datetime, dt_timestamp, dt_time, dt_year) VALUES (?, ?, ?, ?, ?)""")
        container = Empty()
        s.bind_input(bi.In_Varchar(container, 'dt_date', 30),
                     bi.In_Varchar(container, 'dt_datetime', 30),
                     bi.In_Varchar(container, 'dt_timestamp', 30),
                     bi.In_Varchar(container, 'dt_time', 30),
                     bi.In_Varchar(container, 'dt_year', 30),
                    )
        container.dt_date = '2006-01-16'
        container.dt_datetime = '2006-01-16 14:37:12'
        container.dt_timestamp = '2006-01-01 12:30:30'
        container.dt_time = '14:37:30'
        container.dt_year = '2006'
        s.execute()

        s = self.connection.new_statement("""SELECT dt_date, dt_datetime, dt_timestamp, dt_time, dt_year FROM test1 ORDER BY id""")
        container = Empty()
        s.bind_output(bo.Out_Varchar(container, 'dt_date', 30),
                      bo.Out_Varchar(container, 'dt_datetime', 30),
                      bo.Out_Varchar(container, 'dt_timestamp', 30),
                      bo.Out_Varchar(container, 'dt_time', 30),
                      bo.Out_Varchar(container, 'dt_year', 30),
                     )
        s.execute()
        s.fetch()
        self.assertEqual(container.dt_date, '2006-01-16')
        self.assertEqual(container.dt_datetime, '2006-01-16 14:37:12')
        self.assertEqual(container.dt_timestamp, '2006-01-01 12:30:30')
        self.assertEqual(container.dt_time, '14:37:30')
        self.assertEqual(container.dt_year, '2006')
        self.assertRaises(mysql.exceptions.No_More_Rows, s.fetch)

    def test_microsecond(self):
        """Test microseconds."""
        # Microseconds can't be stored, but are supported by the protocol.
        s = self.connection.new_statement("""SELECT ?""")
        container = Empty()
        s.bind_input(bi.In_Date_Time(container, 'input'))
        s.bind_output(bo.Out_Date_Time(container, 'dt'))
        container.input = datetime.datetime(year=2006, month=1, day=16, hour=14, minute=27, second=12, microsecond=12345)
        s.execute()
        s.fetch()
        self.assertEqual(container.dt, datetime.datetime(year=2006, month=1, day=16, hour=14, minute=27, second=12, microsecond=12345))

    def test_result_metadata(self):
        """Test result metatdata."""
        s = self.connection.new_statement("""
            INSERT INTO test1 (
                                utiny,
                                tiny,
                                usmall,
                                small,
                                ui,
                                i,
                                ubigi,
                                bigi,
                                uflo,
                                flo,
                                udoub,
                                doub,
                                vc,
                                blob_tiny,
                                blob_medium,
                                blob_blob,
                                blob_long
                              ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """)
        self.assertEqual(s.get_param_count(), 17)
        container = Empty()

        s.bind_input(bi.In_U_Tiny_Int(container, 'utiny'),
                     bi.In_Tiny_Int(container, 'tiny'),
                     bi.In_U_Small_Int(container, 'usmall'),
                     bi.In_Small_Int(container, 'small'),
                     bi.In_U_Int(container, 'ui'),
                     bi.In_Int(container, 'i'),
                     bi.In_U_Big_Int(container, 'ubigi'),
                     bi.In_Big_Int(container, 'bigi'),
                     bi.In_U_Float(container, 'uflo'),
                     bi.In_Float(container, 'flo'),
                     bi.In_U_Double(container, 'udoub'),
                     bi.In_Double(container, 'doub'),
                     bi.In_Varchar(container, 'vc', 100),
                     bi.In_Tiny_Blob(container, 'blob_tiny'),
                     bi.In_Medium_Blob(container, 'blob_medium'),
                     bi.In_Blob(container, 'blob_blob'),
                     bi.In_Long_Blob(container, 'blob_long'),
                    )
        container.utiny = 1
        container.tiny = -1
        container.usmall = 2
        container.small = -2
        container.ui = 3
        container.i = -3
        container.ubigi = 4
        container.bigi = -4
        container.uflo = 3.14
        container.flo = -3.14
        container.udoub = 2.718
        container.doub = -2.718
        container.vc = 'Variable'
        container.blob_tiny = 'I\'m very tiny.'
        container.blob_medium = 'Medium.'
        container.blob_blob = 'Blobby.'
        container.blob_long = 'Huge.'

        s.execute()
        s = self.connection.new_statement('SELECT id, utiny, tiny, usmall, small, ui, i, ubigi, bigi, uflo, flo, udoub, doub, vc, blob_tiny, blob_medium, blob_blob, blob_long FROM test1 ORDER BY id')
        s.execute()

        fields = s.fields()
        self.assertEqual(len(fields), 18)
        ff = mysql.constants.field_flags
        ft = mysql.constants.field_types
        def assert_field_equal(field, name, org_name, table, org_table, db, catalog, default, length, max_length, flags, decimals, type):
            self.assertEqual(field.name, name)
            self.assertEqual(field.org_name, org_name)
            self.assertEqual(field.table, table)
            self.assertEqual(field.org_table, org_table)
            self.assertEqual(field.db, db)
            self.assertEqual(field.catalog, catalog)
            self.assertEqual(field.default, default)
            self.assertEqual(field.length, length)
            self.assertEqual(field.max_length, max_length)
            self.assertEqual(field.flags & ff.KNOWN_FLAGS, flags)
            self.assertEqual(field.decimals, decimals)
            self.assertEqual(field.type, type)

        assert_field_equal(fields[0],  'id',            'id',           'test1', 'test1', 'py_mysql_test', 'def', None, 10,           0, (ff.AUTO_INCREMENT|ff.NOT_NULL|ff.PRI_KEY|ff.UNSIGNED), 0, ft.INTEGER)
        assert_field_equal(fields[1],  'utiny',         'utiny',        'test1', 'test1', 'py_mysql_test', 'def', None, 3,            0, (ff.UNSIGNED),   0,  ft.TINYINT)
        assert_field_equal(fields[2],  'tiny',          'tiny',         'test1', 'test1', 'py_mysql_test', 'def', None, 4,            0, (0),             0,  ft.TINYINT)
        assert_field_equal(fields[3],  'usmall',        'usmall',       'test1', 'test1', 'py_mysql_test', 'def', None, 5,            0, (ff.UNSIGNED),   0,  ft.SMALLINT)
        assert_field_equal(fields[4],  'small',         'small',        'test1', 'test1', 'py_mysql_test', 'def', None, 6,            0, (0),             0,  ft.SMALLINT)
        assert_field_equal(fields[5],  'ui',            'ui',           'test1', 'test1', 'py_mysql_test', 'def', None, 10,           0, (ff.UNSIGNED),   0,  ft.INTEGER)
        assert_field_equal(fields[6],  'i',             'i',            'test1', 'test1', 'py_mysql_test', 'def', None, 11,           0, (0),             0,  ft.INTEGER)
        assert_field_equal(fields[7],  'ubigi',         'ubigi',        'test1', 'test1', 'py_mysql_test', 'def', None, 20,           0, (ff.UNSIGNED),   0,  ft.BIGINT)
        assert_field_equal(fields[8],  'bigi',          'bigi',         'test1', 'test1', 'py_mysql_test', 'def', None, 20,           0, (0),             0,  ft.BIGINT)
        assert_field_equal(fields[9],  'uflo',          'uflo',         'test1', 'test1', 'py_mysql_test', 'def', None, 12,           0, (ff.UNSIGNED),   31, ft.FLOAT)
        assert_field_equal(fields[10], 'flo',           'flo',          'test1', 'test1', 'py_mysql_test', 'def', None, 12,           0, (0),             31, ft.FLOAT)
        assert_field_equal(fields[11], 'udoub',         'udoub',        'test1', 'test1', 'py_mysql_test', 'def', None, 22,           0, (ff.UNSIGNED),   31, ft.DOUBLE)
        assert_field_equal(fields[12], 'doub',          'doub',         'test1', 'test1', 'py_mysql_test', 'def', None, 22,           0, (0),             31, ft.DOUBLE)
        assert_field_equal(fields[13], 'vc',            'vc',           'test1', 'test1', 'py_mysql_test', 'def', None, 100,          0, (0),             0,  ft.VARCHAR)
        assert_field_equal(fields[14], 'blob_tiny',     'blob_tiny',    'test1', 'test1', 'py_mysql_test', 'def', None, 255,          0, (ff.BINARY),     0,  ft.BLOB)
        assert_field_equal(fields[15], 'blob_medium',   'blob_medium',  'test1', 'test1', 'py_mysql_test', 'def', None, 16777215,     0, (ff.BINARY),     0,  ft.BLOB)
        assert_field_equal(fields[16], 'blob_blob',     'blob_blob',    'test1', 'test1', 'py_mysql_test', 'def', None, 65535,        0, (ff.BINARY),     0,  ft.BLOB)
        assert_field_equal(fields[17], 'blob_long',     'blob_long',    'test1', 'test1', 'py_mysql_test', 'def', None, 4294967295,   0, (ff.BINARY),     0,  ft.BLOB)

        # Test with set_update_max_length.
        s = self.connection.new_statement('SELECT id, utiny, tiny, usmall, small, ui, i, ubigi, bigi, uflo, flo, udoub, doub, vc, blob_tiny, blob_medium, blob_blob, blob_long FROM test1 ORDER BY id')
        s.set_update_max_length()
        s.execute(store_result=True)

        fields = s.fields()
        self.assertEqual(len(fields), 18)

        assert_field_equal(fields[0],  'id',            'id',           'test1', 'test1', 'py_mysql_test', 'def', None, 10,           11, (ff.AUTO_INCREMENT|ff.NOT_NULL|ff.PRI_KEY|ff.UNSIGNED), 0, ft.INTEGER)
        assert_field_equal(fields[1],  'utiny',         'utiny',        'test1', 'test1', 'py_mysql_test', 'def', None, 3,            4,  (ff.UNSIGNED),   0,  ft.TINYINT)
        assert_field_equal(fields[2],  'tiny',          'tiny',         'test1', 'test1', 'py_mysql_test', 'def', None, 4,            4,  (0),             0,  ft.TINYINT)
        assert_field_equal(fields[3],  'usmall',        'usmall',       'test1', 'test1', 'py_mysql_test', 'def', None, 5,            6,  (ff.UNSIGNED),   0,  ft.SMALLINT)
        assert_field_equal(fields[4],  'small',         'small',        'test1', 'test1', 'py_mysql_test', 'def', None, 6,            6,  (0),             0,  ft.SMALLINT)
        assert_field_equal(fields[5],  'ui',            'ui',           'test1', 'test1', 'py_mysql_test', 'def', None, 10,           11, (ff.UNSIGNED),   0,  ft.INTEGER)
        assert_field_equal(fields[6],  'i',             'i',            'test1', 'test1', 'py_mysql_test', 'def', None, 11,           11, (0),             0,  ft.INTEGER)
        assert_field_equal(fields[7],  'ubigi',         'ubigi',        'test1', 'test1', 'py_mysql_test', 'def', None, 20,           21, (ff.UNSIGNED),   0,  ft.BIGINT)
        assert_field_equal(fields[8],  'bigi',          'bigi',         'test1', 'test1', 'py_mysql_test', 'def', None, 20,           21, (0),             0,  ft.BIGINT)
        assert_field_equal(fields[9],  'uflo',          'uflo',         'test1', 'test1', 'py_mysql_test', 'def', None, 12,           331,(ff.UNSIGNED),   31, ft.FLOAT)
        assert_field_equal(fields[10], 'flo',           'flo',          'test1', 'test1', 'py_mysql_test', 'def', None, 12,           331,(0),             31, ft.FLOAT)
        assert_field_equal(fields[11], 'udoub',         'udoub',        'test1', 'test1', 'py_mysql_test', 'def', None, 22,           331,(ff.UNSIGNED),   31, ft.DOUBLE)
        assert_field_equal(fields[12], 'doub',          'doub',         'test1', 'test1', 'py_mysql_test', 'def', None, 22,           331,(0),             31, ft.DOUBLE)
        assert_field_equal(fields[13], 'vc',            'vc',           'test1', 'test1', 'py_mysql_test', 'def', None, 100,          8,  (0),             0,  ft.VARCHAR)
        assert_field_equal(fields[14], 'blob_tiny',     'blob_tiny',    'test1', 'test1', 'py_mysql_test', 'def', None, 255,          14, (ff.BINARY),     0,  ft.BLOB)
        assert_field_equal(fields[15], 'blob_medium',   'blob_medium',  'test1', 'test1', 'py_mysql_test', 'def', None, 16777215,     7,  (ff.BINARY),     0,  ft.BLOB)
        assert_field_equal(fields[16], 'blob_blob',     'blob_blob',    'test1', 'test1', 'py_mysql_test', 'def', None, 65535,        7,  (ff.BINARY),     0,  ft.BLOB)
        assert_field_equal(fields[17], 'blob_long',     'blob_long',    'test1', 'test1', 'py_mysql_test', 'def', None, 4294967295,   5,  (ff.BINARY),     0,  ft.BLOB)

    def test_store(self):
        """Test features that need store_result."""
        s = self.connection.new_statement("""
            INSERT INTO test1 ( utiny ) VALUES (?)
            """)
        container = Empty()
        self.assertEqual(s.get_param_count(), 1)
        s.bind_input(bi.In_U_Tiny_Int(container, 'utiny'))
        container.utiny = 1
        s.execute(store_result=False)
        self.assertEqual(s.affected_rows(), 1)
        self.assertEqual(s.field_count(), 0)
        container.utiny = 2
        s.execute(store_result=False)
        self.assertEqual(s.affected_rows(), 1)
        container.utiny = 3
        s.execute(store_result=False)
        self.assertEqual(s.affected_rows(), 1)
        container.utiny = 4
        s.execute(store_result=False)
        self.assertEqual(s.affected_rows(), 1)

        s = self.connection.new_statement('SELECT id, utiny FROM test1 ORDER BY id')
        container = Empty()
        s.bind_output(bo.Out_Int(container, 'id'),
                      bo.Out_U_Tiny_Int(container, 'utiny'),
                     )
        s.execute(store_result=False)

        self.assertRaises(mysql.exceptions.Affected_Rows_Unavailable, s.affected_rows)
        self.assertEqual(s.num_rows(), 0)
        self.assertEqual(s.field_count(), 2)
        self.assertRaises(mysql.exceptions.Result_Unbuffered_Error, s.row_tell)
        self.assertRaises(mysql.exceptions.Result_Unbuffered_Error, s.row_seek, 0)

        s.fetch()
        self.assertEqual(container.id, 1)
        self.assertEqual(container.utiny, 1)

        s.execute(store_result=True)
        self.assertEqual(s.affected_rows(), 4)
        self.assertEqual(s.num_rows(), 4)
        self.assertEqual(s.field_count(), 2)

        s.row_seek(2)
        s.fetch()
        self.assertEqual(container.id, 3)
        self.assertEqual(container.utiny, 3)
        pos = s.row_tell()
        s.row_seek(0)
        s.fetch()
        self.assertEqual(container.id, 1)
        self.assertEqual(container.utiny, 1)

        s.row_seek(pos)
        s.fetch()
        self.assertEqual(container.id, 4)
        self.assertEqual(container.utiny, 4)

        s.free_result()
        self.assertRaises(mysql.exceptions.No_Result_Set, s.fetch)

    def test_concurrent_statements(self):
        """Test concurrent statements."""
        s1 = self.connection.new_statement("""INSERT INTO test1 (i) VALUES (?)""")
        s2 = self.connection.new_statement("""INSERT INTO test1 (ui) VALUES (?)""")
        container = Empty()
        s1.bind_input(bi.In_Int(container, 'i'))
        s2.bind_input(bi.In_U_Int(container, 'ui'))
        container.i = -7
        container.ui = 8
        s1.execute()
        s2.execute()
        container.i = -6
        container.ui = 9
        s1.execute()
        s2.execute()

        s3 = self.connection.new_statement("""SELECT i FROM test1 ORDER BY i""")
        s4 = self.connection.new_statement("""SELECT ui FROM test1 ORDER BY ui""")
        s5 = self.connection.new_statement("""SELECT id FROM test1 ORDER BY id""")
        container = Empty()
        s3.bind_output(bo.Out_Int(container, 'i'))
        s4.bind_output(bo.Out_U_Int(container, 'ui'))
        s5.bind_output(bo.Out_U_Int(container, 'id'))

        s3.execute(store_result=False)
        s3.fetch()
        s4.execute(store_result=True)
        s5.execute(store_result=True)

        s4.fetch()
        s5.fetch()

        self.assertEqual(container.i, None)
        self.assertEqual(container.ui, None)
        self.assertEqual(container.id, 1)

        self.assertRaises(mysql.exceptions.No_Result_Set, s3.fetch)

        s4.fetch()
        s5.fetch()
        self.assertEqual(container.ui, None)
        self.assertEqual(container.id, 2)

        s4.fetch()
        s5.fetch()
        self.assertEqual(container.ui, 8)
        self.assertEqual(container.id, 3)

        s4.fetch()
        s5.fetch()
        self.assertEqual(container.ui, 9)
        self.assertEqual(container.id, 4)

        # XXX: Should probably test all methods that should cause unbuffered
        # results to be reset.

    def test_reset(self):
        """Test reset."""
        si = self.connection.new_statement("""INSERT INTO test1 (i, blob_blob) VALUES (?, ?)""")
        container = Empty()
        ii = bi.In_Int(container, 'i')
        ib = bi.In_Blob(container, 'blob_blob', use_stream=True)
        si.reset()
        si.bind_input(ii, ib)
        si.reset()
        container.i = -7
        container.blob_blob.write('hi there')
        si.reset()
        container.blob_blob.write('nobody')
        si.execute()
        si.reset()
        container.blob_blob.write('is there')
        si.execute()
        so = self.connection.new_statement("""SELECT i, blob_blob from test1 ORDER BY id""")
        container = Empty()
        so.reset()
        so.bind_output(bo.Out_Int(container, 'i'),
                       bo.Out_Blob(container, 'blob', 100)
                      )
        so.reset()
        so.execute()
        so.fetch()
        self.assertEqual(container.i, -7)
        self.assertEqual(container.blob, 'nobody')
        so.fetch()
        self.assertEqual(container.i, -7)
        self.assertEqual(container.blob, 'is there')
        self.assertRaises(mysql.exceptions.No_More_Rows, so.fetch)
        so.reset()
        self.assertRaises(mysql.exceptions.No_Result_Set, so.fetch)

    def test_cursor(self):
        """Test using a cursor."""
        container = Empty()
        s = self.connection.new_statement("""INSERT INTO test1 (i) VALUES (?)""")
        s.bind_input(bi.In_Int(container, 'i'))
        container.i = 7
        s.execute()
        container.i = 8
        s.execute()
        container.i = 9
        s.execute()
        container.i = 10
        s.execute()
        container.i = 11
        s.execute()
        container.i = 12
        s.execute()
        container.i = 13
        s.execute()
        container.i = 14
        s.execute()

        s = self.connection.new_statement("""SELECT i FROM test1 ORDER BY i""")
        s.set_use_cursor()
        container = Empty()
        s.bind_output(bo.Out_Int(container, 'i'))
        s.execute()

        def check_select_i():
            s.fetch()
            self.assertEqual(container.i, 7)
            s.fetch()
            self.assertEqual(container.i, 8)
            s.fetch()
            self.assertEqual(container.i, 9)
            s.fetch()
            self.assertEqual(container.i, 10)
            s.fetch()
            self.assertEqual(container.i, 11)
            s.fetch()
            self.assertEqual(container.i, 12)
            s.fetch()
            self.assertEqual(container.i, 13)
            s.fetch()
            self.assertEqual(container.i, 14)
            self.assertRaises(mysql.exceptions.No_More_Rows, s.fetch)

        check_select_i()

        # Check what happens when you say "store result".
        s = self.connection.new_statement("""SELECT i FROM test1 ORDER BY i""")
        s.set_use_cursor()
        container = Empty()
        s.bind_output(bo.Out_Int(container, 'i'))
        if self.connection.get_server_version() < 50019:
            self.assertRaises(mysql.exceptions.Commands_Out_Of_Sync, s.execute, store_result=True)
        else:
            s.execute(store_result=True)
            check_select_i()


    def test_attrs(self):
        """Test setting attributes."""
        s = self.connection.new_statement("""SELECT * FROM test1""")
        self.assertFalse(s.get_update_max_length())
        self.assertFalse(s.get_use_cursor())
        self.assertEqual(s.get_prefetch_rows(), 1)

        s.set_update_max_length()
        self.assertTrue(s.get_update_max_length())

        s.set_use_cursor()
        self.assertTrue(s.get_use_cursor())

        s.set_prefetch_rows(5)
        self.assertEqual(s.get_prefetch_rows(), 5)

    def test_data_truncation(self):
        """Test data truncation reporting."""
        self.connection.execute("""INSERT INTO test1 (vc) VALUES ($vc)""", vc='0'*100)
        s = self.connection.new_statement("""SELECT vc FROM test1""")
        container = Empty()
        out = bo.Out_Varchar(container, 'vc', 50)
        s.bind_output(out)
        s.execute()
        self.assertRaises(mysql.exceptions.Data_Truncated, s.fetch)
        self.assertTrue(out.error)
        self.assertEqual(len(container.vc), 50)

    def test_overflow(self):
        """Test overflow."""
        # Excluded are:
        # - DECIMAL (see test_decimal)
        # - DATE/DATETIME/TIMESTAMP/TIME/YEAR (see test_time)
        # - ENUM (see test_enum)
        # - SET (see test_set)
        # - BOOL (N/A)
        s = self.connection.new_statement("""
            INSERT INTO test1 (
                                utiny,
                                tiny,
                                usmall,
                                small,
                                umedium,
                                medium,
                                ui,
                                i,
                                ubigi,
                                bigi,
                                bits,
                                uflo,
                                flo,
                                udoub,
                                doub,
                                vc,
                                vbin
                              ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """)
        self.assertEqual(s.get_param_count(), 17)
        container = Empty()
        s.bind_input(bi.In_U_Tiny_Int(container, 'utiny'),
                     bi.In_Tiny_Int(container, 'tiny'),
                     bi.In_U_Small_Int(container, 'usmall'),
                     bi.In_Small_Int(container, 'small'),
                     bi.In_U_Medium_Int(container, 'umedium'),
                     bi.In_Medium_Int(container, 'medium'),
                     bi.In_U_Int(container, 'ui'),
                     bi.In_Int(container, 'i'),
                     bi.In_U_Big_Int(container, 'ubigi'),
                     bi.In_Big_Int(container, 'bigi'),
                     bi.In_Bit(container, 'bits'),
                     bi.In_U_Float(container, 'uflo'),
                     bi.In_Float(container, 'flo'),
                     bi.In_U_Double(container, 'udoub'),
                     bi.In_Double(container, 'doub'),
                     bi.In_Varchar(container, 'vc', 100),
                     bi.In_Varbinary(container, 'vbin', 100),
                    )
        for column, values in [('utiny', (-1, 256, 0xff00, 255*2, 0xffffffff, -255, -256)),
                               ('tiny', (-129, 128, 0xff00, -128*2, 0xffffffff, 127*2)),
                               ('usmall', (-1, 65536, 0xff0000, 65535*2, 0xffffffff, -32768, -32769)),
                               ('small', (-32769, 32768, 0xff0000, 32767*2, 0xffffffff, -32767*2)),
                               ('umedium', (-1, 16777216, 0xff000000, 16777215*2, 0xffffffff, -8388608)),
                               ('medium', (-8388609, 8388608, 0xff000000, 8388607*2, 0xffffffff, -8388608*2)),
                               ('ui', (-1, 4294967296, 0xff00000000, 4294967295*2)),
                               ('i', (-2147483649, 2147483648, 0xffffffff)),
                               ('ubigi', (-1, 18446744073709551616)),
                               ('bigi', (-9223372036854775809, 9223372036854775808, 0xffffffffffffffff)),
                               ('bits', (4722366482869645213695L,)),
                               # XXX These tests probably depend on the current platform.
                               ('uflo', (-1,)),
                               ('flo', ()), # Overflow checking disabled.
                               ('udoub', (-1, -1.8E+310)),
                               ('doub', ()), # Don't know of a way to get overflow here.
                               ('vc', ('a'*101,)),
                               ('vbin', ('a'*101,)),
                              ]:
            for value in values:
                setattr(container, column, value)
                try:
                    s.execute()
                except OverflowError:
                    pass
                else:
                    self.fail('column %r with value %r did not raise OverflowError' % (column, value))
            setattr(container, column, None)
            s.execute()

        # Test infinity floats.
        container.flo = -1.8E+310
        s.execute()
        container.doub = -1.8E+310
        s.execute()
        container.uflo = 1.8E+310
        s.execute()
        container.flo = 1.8E+310
        s.execute()
        container.udoub = 1.8E+310
        s.execute()
        container.doub = 1.8E+310
        s.execute()

        # Do char test.
        s = self.connection.new_statement("""INSERT INTO test2 (c, bin) VALUES (?, ?)""")
        container = Empty()
        s.bind_input(bi.In_Char(container, 'c', 100),
                     bi.In_Binary(container, 'bin', 100),
                    )
        container.c = 'a'*101
        self.assertRaises(OverflowError, s.execute)
        container.c = ''
        s.execute()

        container.bin = 'a'*101
        self.assertRaises(OverflowError, s.execute)
        container.bin = ''
        s.execute()

        # Blob test.
        # Other sizes besides tiny are not practical.
        s = self.connection.new_statement("""INSERT INTO test1 (blob_tiny) VALUES (?)""")
        container = Empty()
        s.bind_input(bi.In_Tiny_Blob(container, 'blob_tiny', use_stream=True))
        self.assertRaises(OverflowError, container.blob_tiny.write, 'a'*257)
        # Make sure state was reset.
        s.execute()
        container.blob_tiny.write('a')
        s.execute()

        s.bind_input(bi.In_Tiny_Blob(container, 'blob_tiny', use_stream=False))
        container.blob_tiny = 'a'*257
        self.assertRaises(OverflowError, s.execute)
        container.blob_tiny = ''
        s.execute()

    def test_long_int(self):
        """Test long<->int conversion."""
        s = self.connection.new_statement("""
            INSERT INTO test1 (
                                utiny,
                                tiny,
                                usmall,
                                small,
                                umedium,
                                medium,
                                ui,
                                i,
                                ubigi,
                                bigi
                              ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """)
        self.assertEqual(s.get_param_count(), 10)
        container = Empty()
        s.bind_input(bi.In_U_Tiny_Int(container, 'utiny'),
                     bi.In_Tiny_Int(container, 'tiny'),
                     bi.In_U_Small_Int(container, 'usmall'),
                     bi.In_Small_Int(container, 'small'),
                     bi.In_U_Medium_Int(container, 'umedium'),
                     bi.In_Medium_Int(container, 'medium'),
                     bi.In_U_Int(container, 'ui'),
                     bi.In_Int(container, 'i'),
                     bi.In_U_Big_Int(container, 'ubigi'),
                     bi.In_Big_Int(container, 'bigi'),
                    )
        container.utiny = 1L
        container.tiny = 1L
        container.usmall = 1L
        container.small = 1L
        container.umedium = 1L
        container.medium = 1L
        container.ui = 1L
        container.i = 1L
        container.ubigi = 1L
        container.bigi = 1L
        s.execute()

        container.utiny = 1
        container.tiny = 1
        container.usmall = 1
        container.small = 1
        container.umedium = 1
        container.medium = 1
        container.ui = 1
        container.i = 1
        container.ubigi = 1
        container.bigi = 1
        s.execute()

        s = self.connection.new_statement("""SELECT id,
                                                    utiny,
                                                    tiny,
                                                    usmall,
                                                    small,
                                                    umedium,
                                                    medium,
                                                    ui,
                                                    i,
                                                    ubigi,
                                                    bigi
                                                        FROM test1 ORDER BY id""")
        container = Empty()
        s.bind_output(bo.Out_Int(container, 'id'),
                      bo.Out_U_Tiny_Int(container, 'utiny'),
                      bo.Out_Tiny_Int(container, 'tiny'),
                      bo.Out_U_Small_Int(container, 'usmall'),
                      bo.Out_Small_Int(container, 'small'),
                      bo.Out_U_Medium_Int(container, 'umedium'),
                      bo.Out_Medium_Int(container, 'medium'),
                      bo.Out_U_Int(container, 'ui'),
                      bo.Out_Int(container, 'i'),
                      bo.Out_U_Big_Int(container, 'ubigi'),
                      bo.Out_Big_Int(container, 'bigi'),
                     )
        s.execute()
        s.fetch()

        self.assertEquals(type(container.utiny), int)
        self.assertEquals(type(container.tiny), int)
        self.assertEquals(type(container.usmall), int)
        self.assertEquals(type(container.small), int)
        self.assertEquals(type(container.umedium), int)
        self.assertEquals(type(container.medium), int)
        self.assertEquals(type(container.ui), int)
        self.assertEquals(type(container.i), int)
        self.assertEquals(type(container.ubigi), int)
        self.assertEquals(type(container.bigi), int)

        self.assertEquals(container.utiny, 1)
        self.assertEquals(container.tiny, 1)
        self.assertEquals(container.usmall, 1)
        self.assertEquals(container.small, 1)
        self.assertEquals(container.umedium, 1)
        self.assertEquals(container.medium, 1)
        self.assertEquals(container.ui, 1)
        self.assertEquals(container.i, 1)
        self.assertEquals(container.ubigi, 1)
        self.assertEquals(container.bigi, 1)

        s.fetch()
        self.assertEquals(type(container.utiny), int)
        self.assertEquals(type(container.tiny), int)
        self.assertEquals(type(container.usmall), int)
        self.assertEquals(type(container.small), int)
        self.assertEquals(type(container.umedium), int)
        self.assertEquals(type(container.medium), int)
        self.assertEquals(type(container.ui), int)
        self.assertEquals(type(container.i), int)
        self.assertEquals(type(container.ubigi), int)
        self.assertEquals(type(container.bigi), int)

        self.assertEquals(container.utiny, 1)
        self.assertEquals(container.tiny, 1)
        self.assertEquals(container.usmall, 1)
        self.assertEquals(container.small, 1)
        self.assertEquals(container.umedium, 1)
        self.assertEquals(container.medium, 1)
        self.assertEquals(container.ui, 1)
        self.assertEquals(container.i, 1)
        self.assertEquals(container.ubigi, 1)
        self.assertEquals(container.bigi, 1)

        self.assertRaises(mysql.exceptions.No_More_Rows, s.fetch)

    def test_disconnect(self):
        """Test disconnect."""
        s = self.connection.new_statement("""INSERT INTO test1 (i) VALUES (?)""")
        container = Empty()
        s.bind_input(bi.In_Int(container, 'i'))
        container.i = 3
        s.execute()
        self.connection.kill_server_thread(self.connection.server_thread_id())
        time.sleep(0.5)
        self.assertRaises(mysql.exceptions.Server_Gone_Error, s.execute)


if __name__ == '__main__':
    unittest.main()
