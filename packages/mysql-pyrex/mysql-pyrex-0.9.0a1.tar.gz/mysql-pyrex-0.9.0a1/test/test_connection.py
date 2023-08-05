# $Header: /home/cvs2/mysql/test/test_connection.py,v 1.7 2006/09/11 01:42:28 ehuss Exp $
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

"""Connection object unittests."""

__version__ = '$Revision: 1.7 $'

import datetime
import decimal
import os
import sets
import tempfile
import time
import unittest

import base_test
import mysql.connection
import mysql.constants.client_flags
import mysql.conversion.input
import mysql.conversion.output

class Test(base_test.Base_Mysql_Test_Case):

    def tearDown(self):
        self._shutdown()

    def test_connect(self):
        """Test connecting."""
        c = mysql.connection.Connection()
        # Assuming current user does not have default access.
        self.assertRaises(mysql.exceptions.Access_Denied_Error, c.connect)
        self._connect()
        self._make_test_tables()
        self.connection.disconnect()
        c.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
        c.disconnect()

        # Test host.
        c = mysql.connection.Connection()
        self.assertRaises(mysql.exceptions.Unknown_Host, c.connect, host='foo')
        c.connect(host='localhost', user=base_test.test_user, password=base_test.test_password)
        c.disconnect()

        # Test port.
        c = mysql.connection.Connection()
        c.set_protocol_tcp()
        self.assertRaises(mysql.exceptions.Conn_Host_Error, c.connect, port=9999)
        c.connect(port=3306, user=base_test.test_user, password=base_test.test_password)
        c.disconnect()

        # Test unix socket.
        c = mysql.connection.Connection()
        self.assertRaises(mysql.exceptions.Connection_Error, c.connect, unix_socket='/notthere')
        c.connect(unix_socket='/tmp/mysql.sock', user=base_test.test_user, password=base_test.test_password)
        c.disconnect()

        # For now, only going to check that 1 flag actually does something.
        c = mysql.connection.Connection()
        c.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
        self.assertRaises(mysql.exceptions.Parse_Error, c.execute, """INSERT INTO test1 (i) VALUES (1); INSERT INTO test1 (i) VALUES (2)""")
        c.disconnect()
        c.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db, clientflag=mysql.constants.client_flags.MULTI_STATEMENTS)
        self.assertEquals(1, c.execute("""INSERT INTO test1 (i) VALUES (1); INSERT INTO test1 (i) VALUES (2)"""))
        self.assertEquals(1, c.next_result())
        c.disconnect()
        c.connect(user=base_test.test_user,
                  password=base_test.test_password,
                  db=base_test.test_db,
                  clientflag=(mysql.constants.client_flags.FOUND_ROWS |
                              mysql.constants.client_flags.COMPRESS |
                              mysql.constants.client_flags.IGNORE_SPACE |
                              mysql.constants.client_flags.INTERACTIVE |
                              mysql.constants.client_flags.LOCAL_FILES |
                              mysql.constants.client_flags.MULTI_STATEMENTS |
                              mysql.constants.client_flags.MULTI_RESULTS |
                              mysql.constants.client_flags.NO_SCHEMA |
                              mysql.constants.client_flags.ODBC |
                              mysql.constants.client_flags.SSL
                             )
                 )
        c.disconnect()

    def test_input_conversion(self):
        """Test input conversion."""
        self._connect()
        self._make_test_tables()

        # Simple test.
        self.connection.execute("""INSERT INTO test1 (i, vc) VALUES ($i, $vc)""", i=1, vc='hi there \'bob\'')
        r = self.connection.execute("""SELECT i, vc FROM test1 WHERE id=1""")
        self.assertEquals(r.fetch_row(), (1, 'hi there \'bob\''))

        # Test various data types.
        self._clear_tables()
        # Sets via lists, tuples, dicts, and set module.
        self.connection.execute("""INSERT INTO test1 (s) VALUES ($s)""", s=('red','green'))
        self.connection.execute("""INSERT INTO test1 (s) VALUES ($s)""", s=['green','blue'])
        self.connection.execute("""INSERT INTO test1 (s) VALUES ($s)""", s={'red':None, 'blue': None})
        self.connection.execute("""INSERT INTO test1 (s) VALUES ($s)""", s=sets.Set(('red','green','blue')))
        r = self.connection.execute("""SELECT s FROM test1 ORDER BY id""")
        self.assertEquals(r.fetch_row(), (['red','green'],))
        self.assertEquals(r.fetch_row(), (['green','blue'],))
        self.assertEquals(r.fetch_row(), (['red','blue'],))
        self.assertEquals(r.fetch_row(), (['red','green','blue'],))
        self.assertRaises(mysql.exceptions.No_More_Rows, r.fetch_row)

        # Test decimal.
        self._clear_tables()
        self.connection.execute("""INSERT INTO test1 (deci) VALUES ($d)""", d=decimal.Decimal('1.1'))
        r = self.connection.execute("""SELECT ROUND(deci,1) FROM test1""")
        self.assertEquals(r.fetch_row(), (decimal.Decimal('1.1'),))

        # Test None.
        self._clear_tables()
        self.connection.execute("""INSERT INTO test1 (vc) VALUES ($vc)""", vc=None)
        r = self.connection.execute("""SELECT vc FROM test1""")
        self.assertEquals(r.fetch_row(), (None,))

        # Test datetime.
        self._clear_tables()
        self.connection.execute("""INSERT INTO test1 (dt_date, dt_datetime, dt_timestamp, dt_time)
                                    VALUES ($dt_date, $dt_datetime, $dt_timestamp, $dt_time)""",
                                    dt_date=datetime.date(year=2006, month=7, day=16),
                                    dt_datetime=datetime.datetime(year=2006, month=7, day=16, hour=19, minute=46, second=45),
                                    dt_timestamp=datetime.datetime(year=2001, month=1, day=1, hour=0, minute=0, second=0),
                                    dt_time=datetime.time(hour=12, minute=30, second=15),
                               )
        r = self.connection.execute("""SELECT dt_date, dt_datetime, dt_timestamp, dt_time FROM test1""")
        self.assertEquals(r.fetch_row(), (datetime.date(2006, 7, 16),
                                          datetime.datetime(2006, 7, 16, 19, 46, 45),
                                          datetime.datetime(2001, 1, 1, 0, 0, 0),
                                          datetime.timedelta(hours=12, minutes=30, seconds=15)
                                         )
                         )

        self._clear_tables()
        self.connection.execute("""INSERT INTO test1 (dt_time) VALUES ($dt_time)""",
                                dt_time=datetime.timedelta(days=-1)
                               )
        self.connection.execute("""INSERT INTO test1 (dt_time) VALUES ($dt_time)""",
                                dt_time=datetime.timedelta(hours=-1)
                               )
        self.connection.execute("""INSERT INTO test1 (dt_time) VALUES ($dt_time)""",
                                dt_time=datetime.timedelta(minutes=-1)
                               )
        self.connection.execute("""INSERT INTO test1 (dt_time) VALUES ($dt_time)""",
                                dt_time=datetime.timedelta(seconds=-1)
                               )
        self.connection.execute("""INSERT INTO test1 (dt_time) VALUES ($dt_time)""",
                                dt_time=datetime.timedelta(days=1)
                               )
        self.connection.execute("""INSERT INTO test1 (dt_time) VALUES ($dt_time)""",
                                dt_time=datetime.timedelta(hours=1)
                               )
        self.connection.execute("""INSERT INTO test1 (dt_time) VALUES ($dt_time)""",
                                dt_time=datetime.timedelta(minutes=1)
                               )
        self.connection.execute("""INSERT INTO test1 (dt_time) VALUES ($dt_time)""",
                                dt_time=datetime.timedelta(seconds=1)
                               )
        self.assertRaises(OverflowError, self.connection.execute,
                            """INSERT INTO test1 (dt_time) VALUES ($dt_time)""",
                            dt_time=datetime.timedelta(hours=839)
                         )
        self.assertRaises(OverflowError, self.connection.execute,
                            """INSERT INTO test1 (dt_time) VALUES ($dt_time)""",
                            dt_time=datetime.timedelta(hours=-839)
                         )
        r = self.connection.execute("""SELECT dt_time FROM test1 ORDER BY id""")
        self.assertEqual(r.fetch_row(), (datetime.timedelta(hours=-24),))
        self.assertEqual(r.fetch_row(), (datetime.timedelta(hours=-1),))
        self.assertEqual(r.fetch_row(), (datetime.timedelta(minutes=-1),))
        self.assertEqual(r.fetch_row(), (datetime.timedelta(seconds=-1),))
        self.assertEqual(r.fetch_row(), (datetime.timedelta(hours=24),))
        self.assertEqual(r.fetch_row(), (datetime.timedelta(hours=1),))
        self.assertEqual(r.fetch_row(), (datetime.timedelta(minutes=1),))
        self.assertEqual(r.fetch_row(), (datetime.timedelta(seconds=1),))


        # Test with a custom input conversion.
        class IC(mysql.conversion.input.Input_Conversion):

            def convert(self, *values):
                return values

        self._clear_tables()
        self.connection.disconnect()
        self.connection = mysql.connection.Connection(convert_in=IC())
        self.connection.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
        self.assertRaises(mysql.exceptions.Parse_Error, self.connection.execute, """INSERT INTO test1 (i, vc) VALUES ($i, $vc)""", i=1, vc='hi there')
        self.connection.execute("""INSERT INTO test1 (i, vc) VALUES ($i, $vc)""", i='1', vc='\'hi there\'')

    def test_output_conversion(self):
        """Test output conversion."""
        self._connect()
        self._make_test_tables()
        self.connection.execute("""INSERT INTO test1 (utiny, tiny,
                                                      usmall, small,
                                                      umedium, medium,
                                                      ui, i,
                                                      ubigi, bigi,
                                                      boo,
                                                      uflo, flo,
                                                      udoub, doub,
                                                      udeci, deci,
                                                      dt_date, dt_datetime, dt_timestamp, dt_time, dt_year,
                                                      c, vc, bin, vbin,
                                                      e, s,
                                                      blob_tiny, blob_medium, blob_blob, blob_long,
                                                      text_tiny, text_medium, text_text, text_long
                                                      ) VALUES (
                                                          $utiny, $tiny,
                                                          $usmall, $small,
                                                          $umedium, $medium,
                                                          $ui, $i,
                                                          $ubigi, $bigi,
                                                          $boo,
                                                          $uflo, $flo,
                                                          $udoub, $doub,
                                                          $udeci, $deci,
                                                          $dt_date, $dt_datetime, $dt_timestamp, $dt_time, $dt_year,
                                                          $c, $vc, $bin, $vbin,
                                                          $e, $s,
                                                          $blob_tiny, $blob_medium, $blob_blob, $blob_long,
                                                          $text_tiny, $text_medium, $text_text, $text_long
                                                          )""",
                                                            utiny=255, tiny=-128,
                                                            usmall=65535, small=-32768,
                                                            umedium=16777215, medium=-8388608,
                                                            ui=4294967295, i=-2147483648,
                                                            ubigi=18446744073709551615, bigi=-9223372036854775808,
                                                            boo=True,
                                                            uflo=1.1, flo=-1.1,
                                                            udoub=2.2, doub=-2.2,
                                                            udeci=decimal.Decimal('3.14'), deci=decimal.Decimal('-2.718'),
                                                            dt_date=datetime.date(2006, 7, 22),
                                                            dt_datetime=datetime.datetime(2006, 7, 22, 12, 50, 34),
                                                            dt_timestamp=datetime.datetime(2001, 1, 1, 0, 0, 15),
                                                            dt_time=datetime.timedelta(days=-30, seconds=-5),
                                                            dt_year=2020,
                                                            c='hi there', vc='variable char',
                                                            bin='bin\xe1ry', vbin='variable bin\xe1ry',
                                                            e='two', s='red,green,blue',
                                                            blob_tiny='\x01tiny blob', blob_medium='\x02medium blob', blob_blob='\x03blob blob', blob_long='\x04long blob',
                                                            text_tiny='tiny text', text_medium='medium text', text_text='text text', text_long='long text',
                                                            )
        # A few data types require special attention.
        self.connection.execute('INSERT INTO test1 (dt_time) VALUES ($dt_time)', dt_time=datetime.timedelta(days=30, seconds=5))
        self.connection.execute('INSERT INTO test1 (bits) VALUES ($bits)', bits='')
        self.connection.execute('INSERT INTO test1 (bits) VALUES ($bits)', bits='\x01')
        self.connection.execute('INSERT INTO test1 (bits) VALUES ($bits)', bits='\x7f\xff\xff\xff')
        self.connection.execute('INSERT INTO test1 (bits) VALUES ($bits)', bits='\xff\xff\xff\xff')
        self.connection.execute('INSERT INTO test1 (bits) VALUES ($bits)', bits='\xff\xff\xff\xff\xff\xff\xff\xff')
        self.connection.execute('INSERT INTO test1 (bits) VALUES ($bits)', bits='\x01\x02\x03\x04\x05\x06\x07\x08')
        self.connection.execute('INSERT INTO test1 (bits) values ($bits)', bits=0)
        self.connection.execute('INSERT INTO test1 (bits) values ($bits)', bits=1)
        self.connection.execute('INSERT INTO test1 (bits) values ($bits)', bits=0x543212345)
        self.connection.execute('INSERT INTO test1 (i) VALUES ($i)', i=None)

        r = self.connection.execute("""SELECT id, utiny, tiny,
                                              usmall, small,
                                              umedium, medium,
                                              ui, i,
                                              ubigi, bigi,
                                              bits, boo,
                                              uflo, flo,
                                              udoub, doub,
                                              udeci, deci,
                                              dt_date, dt_datetime, dt_timestamp, dt_time, dt_year,
                                              c, vc, bin, vbin,
                                              e, s,
                                              blob_tiny, blob_medium, blob_blob, blob_long,
                                              text_tiny, text_medium, text_text, text_long FROM test1 ORDER BY id""")
        row = r.fetch_row()
        expected_result = (1, 255, -128,
                           65535, -32768,
                           16777215, -8388608,
                           4294967295, -2147483648,
                           18446744073709551615, -9223372036854775808,
                           None, True,
                           1.1, -1.1,
                           2.2, -2.2,
                           decimal.Decimal('3.14'), decimal.Decimal('-2.718'),
                           datetime.date(2006, 7, 22),
                           datetime.datetime(2006, 7, 22, 12, 50, 34),
                           datetime.datetime(2001, 1, 1, 0, 0, 15),
                           datetime.timedelta(days=-30, seconds=-5),
                           2020,
                           'hi there', 'variable char',
                           'bin\xe1ry\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 'variable bin\xe1ry',
                           'two', ['red','green','blue'],
                           '\x01tiny blob', '\x02medium blob', '\x03blob blob', '\x04long blob',
                           'tiny text', 'medium text', 'text text', 'long text'
                          )
        for value, expected_value in zip(row, expected_result):
            self.assertEqual(value, expected_value)
        data = r.fetch_row()
        self.assertEquals(data[0], 2)
        self.assertEquals(data[22], datetime.timedelta(days=30, seconds=5))
        data = r.fetch_row()
        self.assertEquals(data[0], 3)
        self.assertEquals(data[11], 0)
        data = r.fetch_row()
        self.assertEquals(data[0], 4)
        self.assertEquals(data[11], 1)
        data = r.fetch_row()
        self.assertEquals(data[0], 5)
        self.assertEquals(data[11], 2147483647)
        data = r.fetch_row()
        self.assertEquals(data[0], 6)
        self.assertEquals(data[11], 4294967295)
        data = r.fetch_row()
        self.assertEquals(data[0], 7)
        self.assertEquals(data[11], 18446744073709551615)
        data = r.fetch_row()
        self.assertEquals(data[0], 8)
        self.assertEquals(data[11], 72623859790382856)
        data = r.fetch_row()
        self.assertEquals(data[0], 9)
        self.assertEquals(data[11], 0)
        data = r.fetch_row()
        self.assertEquals(data[0], 10)
        self.assertEquals(data[11], 1)
        data = r.fetch_row()
        self.assertEquals(data[0], 11)
        self.assertEquals(data[11], 0x543212345)
        data = r.fetch_row()

        self.assertEquals(data[0], 12)
        self.assertEquals(data[8], None)
        self.connection.disconnect()


        self.connection = mysql.connection.Connection(convert_out=mysql.conversion.output.No_Conversion())
        self.connection.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
        r = self.connection.execute("""SELECT id, utiny, tiny,
                                              usmall, small,
                                              umedium, medium,
                                              ui, i,
                                              ubigi, bigi,
                                              bits, boo,
                                              uflo, flo,
                                              udoub, doub,
                                              udeci, deci,
                                              dt_date, dt_datetime, dt_timestamp, dt_time, dt_year,
                                              c, vc, bin, vbin,
                                              e, s,
                                              blob_tiny, blob_medium, blob_blob, blob_long,
                                              text_tiny, text_medium, text_text, text_long FROM test1 ORDER BY id""")
        row = r.fetch_row()
        expected_result = ('1', '255', '-128',
                           '65535', '-32768',
                           '16777215', '-8388608',
                           '4294967295', '-2147483648',
                           '18446744073709551615', '-9223372036854775808',
                           None, '1',
                           '1.1', '-1.1',
                           '2.2', '-2.2',
                           '3.140000000000000000000000000000', '-2.718000000000000000000000000000',
                           '2006-07-22',
                           '2006-07-22 12:50:34',
                           '2001-01-01 00:00:15',
                           '-720:00:05',
                           '2020',
                           'hi there', 'variable char',
                           'bin\xe1ry\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 'variable bin\xe1ry',
                           'two', 'red,green,blue',
                           '\x01tiny blob', '\x02medium blob', '\x03blob blob', '\x04long blob',
                           'tiny text', 'medium text', 'text text', 'long text'
                          )
        for value, expected_value in zip(row, expected_result):
            self.assertEqual(value, expected_value)
        data = r.fetch_row()
        self.assertEquals(data[0], '2')
        self.assertEquals(data[22], '720:00:05')
        data = r.fetch_row()
        self.assertEquals(data[0], '3')
        self.assertEquals(data[11], '\x00\x00\x00\x00\x00\x00\x00\x00')
        data = r.fetch_row()
        self.assertEquals(data[0], '4')
        self.assertEquals(data[11], '\x00\x00\x00\x00\x00\x00\x00\x01')
        data = r.fetch_row()
        self.assertEquals(data[0], '5')
        self.assertEquals(data[11], '\x00\x00\x00\x00\x7f\xff\xff\xff')
        data = r.fetch_row()
        self.assertEquals(data[0], '6')
        self.assertEquals(data[11], '\x00\x00\x00\x00\xff\xff\xff\xff')
        data = r.fetch_row()
        self.assertEquals(data[0], '7')
        self.assertEquals(data[11], '\xff\xff\xff\xff\xff\xff\xff\xff')
        data = r.fetch_row()
        self.assertEquals(data[0], '8')
        self.assertEquals(data[11], '\x01\x02\x03\x04\x05\x06\x07\x08')
        data = r.fetch_row()
        self.assertEquals(data[0], '9')
        self.assertEquals(data[8], None)

    def test_paramstyle(self):
        """Test paramstyle."""
        self._connect()
        self._make_test_tables()
        self.connection.execute("""INSERT INTO test1 (i, tiny, vc) VALUES ($i, $tiny, $vc)""", {'i': 2, 'tiny': 3}, i=1, vc='hi there')
        r = self.connection.execute("""SELECT i, tiny, vc FROM test1 WHERE id=1""")
        self.assertEquals(r.fetch_row(), (1, 3, 'hi there'))
        self.connection.disconnect()

        self.connection = mysql.connection.Connection(paramstyle='format')
        self.connection.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
        self.connection.execute("""INSERT INTO test1 (i, tiny, vc) VALUES (%i, %i, %s)""", 4, 5, 'boo')
        r = self.connection.execute("""SELECT i, tiny, vc FROM test1 WHERE id=2""")
        self.assertEquals(r.fetch_row(), (4, 5, 'boo'))
        self.connection.disconnect()

        self.connection = mysql.connection.Connection(paramstyle='pyformat')
        self.connection.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
        self.connection.execute("""INSERT INTO test1 (i, tiny, vc) VALUES (%(i)i, %(tiny)i, %(vc)s)""", {'i': 6, 'tiny': 7}, i=8, vc='foo')
        r = self.connection.execute("""SELECT i, tiny, vc FROM test1 WHERE id=3""")
        self.assertEquals(r.fetch_row(), (8, 7, 'foo'))
        self.connection.disconnect()

    def test_disconnect(self):
        """Test disconnect."""
        c = mysql.connection.Connection()
        c.disconnect()
        c.disconnect()
        c.connect(user=base_test.test_user, password=base_test.test_password)
        c.disconnect()
        self.assertRaises(mysql.exceptions.Not_Connected_Error, c.execute, 'foo')

    def test_select_db(self):
        """Test select db."""
        self._connect()
        self._make_test_tables()
        c = mysql.connection.Connection()
        c.connect(user=base_test.test_user, password=base_test.test_password)
        self.assertRaises(mysql.exceptions.No_DB_Error, c.execute, """DESCRIBE test1""")
        c.select_db(base_test.test_db)
        c.execute("""DESCRIBE test1""")

    def test_init_command(self):
        """Test init command."""
        self._connect()
        self._make_test_tables()
        c = mysql.connection.Connection()
        c.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
        c.execute("""INSERT INTO test2 (c) VALUES ($c)""", c='hi')
        c.disconnect()
        c.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
        r = c.execute("""SELECT id, c FROM test2""", store_result=True)
        self.assertEquals(r.num_rows(), 1)
        self.assertEquals(r.fetch_row(), (1, 'hi'))
        c.disconnect()
        c.add_init_command("""SET AUTOCOMMIT=0""")
        c.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
        c.execute("""INSERT INTO test2 (c) VALUES ($c)""", c='bye')
        r = c.execute("""SELECT id, c FROM test2""", store_result=True)
        self.assertEquals(r.num_rows(), 2)
        c.disconnect()
        c.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
        r = c.execute("""SELECT id, c FROM test2""", store_result=True)
        self.assertEquals(r.num_rows(), 1)
        c.disconnect()

    def test_compression(self):
        """Test connection compression."""
        # XXX: Hmm, how should we test this?
        c = mysql.connection.Connection()
        c.set_use_compression()
        c.connect(user=base_test.test_user, password=base_test.test_password)
        r = c.execute("""SHOW DATABASES""")
        c.disconnect()

    def test_timeouts(self):
        """Test timeouts."""
        # XXX: Hmm, how should we test this?
        c = mysql.connection.Connection()
        c.set_connect_timeout(1)
        c.set_read_timeout(1)
        c.set_write_timeout(1)
        c.connect(user=base_test.test_user, password=base_test.test_password)
        r = c.execute("""SHOW DATABASES""")
        c.disconnect()

    def test_enable_localfile(self):
        """Test enable "LOAD DATA LOCAL INFILE" command."""
        self._connect()
        self._make_test_tables()
        fd, temp_filename = tempfile.mkstemp()
        try:
            os.write(fd, 'one\n')
            os.write(fd, 'two\n')
            os.write(fd, 'three\n')
            os.fsync(fd)
            try:
                self.connection.execute('LOAD DATA LOCAL INFILE $filename INTO TABLE test2', filename=temp_filename)
            except mysql.exceptions.Not_Allowed_Command:
                print 'Your MySQL installation does not allow testing the LOAD DATA LOCAL INFILE command.'

            self.connection.disconnect()
            self.connection.set_disable_load_infile()
            self.connection.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
            self.assertRaises(mysql.exceptions.Not_Allowed_Command,
                                self.connection.execute,
                                'LOAD DATA LOCAL INFILE $filename INTO TABLE test2', filename=temp_filename)

        finally:
            os.close(fd)
            os.unlink(temp_filename)

    def test_protocol(self):
        """Test connection protocol."""
        # XXX: Hmm, how should we test this?
        #set_protocol_default
        #set_protocol_tcp
        #set_protocol_socket
        #set_protocol_pipe
        #set_protocol_memory
        #set_shared_memory_base_name

    def test_reconnect(self):
        """Test auto reconnect."""
        # Default is off.
        self._connect()
        self._make_test_tables()
        self.connection.disconnect()
        self.assertRaises(mysql.exceptions.Not_Connected_Error, self.connection.set_reconnect_on)
        self.assertRaises(mysql.exceptions.Not_Connected_Error, self.connection.set_reconnect_off)
        self.connection.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
        self.connection.set_reconnect_on()
        self.connection.execute('INSERT INTO test1 (i) VALUES (1)')
        self.connection.kill_server_thread(self.connection.server_thread_id())
        # Killing a thread appears to be asynchronous.  If we don't sleep here,
        # at least on my system, there is a race condition that causes the
        # connection to be broken in the middle of processing the result
        # (cli_read_query_result) which cannot reconnect.
        time.sleep(0.5)
        self.connection.execute('INSERT INTO test1 (i) VALUES (2)')
        self.connection.set_reconnect_off()
        self.connection.kill_server_thread(self.connection.server_thread_id())
        time.sleep(0.5)
        self.assertRaises(mysql.exceptions.Server_Gone_Error, self.connection.execute, 'INSERT INTO test1 (i) VALUES (3)')

    def test_conf_file(self):
        """Test setting the configuration file."""
        self._connect()
        self._make_test_tables()
        fd, temp_filename = tempfile.mkstemp()
        try:
            c = mysql.connection.Connection()
            self.assertRaises(mysql.exceptions.Access_Denied_Error, c.connect, user='foo', password=base_test.test_password)
            os.write(fd, '[somegroup]\n')
            os.write(fd, 'user=%s\n' % (base_test.test_user,))
            os.fsync(fd)
            c.set_default_conf_file(temp_filename)
            c.set_default_conf_group('somegroup')
            c.connect(password=base_test.test_password)
        finally:
            os.close(fd)
            os.unlink(temp_filename)

    def test_secure_auth(self):
        """Test secure auth."""
        # XXX: Hmm, how should we test this?
        c = mysql.connection.Connection()
        c.set_secure_auth_off()
        c.connect(user=base_test.test_user, password=base_test.test_password)
        c.disconnect()
        c.set_secure_auth_on()
        c.connect(user=base_test.test_user, password=base_test.test_password)
        c.disconnect()

    def test_charset(self):
        """Test character set commands."""
        # XXX
        #set_charset_dir
        #set_charset_name
        #get_current_character_set_info
        #set_current_character_set
        self._connect()
        charset = self.connection.get_current_character_set_info()
        self.assertEquals(charset.name, 'latin1')
        self.assertEquals(charset.collation_name, 'latin1_swedish_ci')
        self.assertEquals(charset.mb_min_len, 1)
        self.assertEquals(charset.mb_max_len, 1)

    def test_statement_escape(self):
        """Test statement escaping."""
        c = mysql.connection.Connection()
        # XXX: unicode, complex
        # XXX: Additional types I need add, like sets.
        self.assertEqual(
            c.escape('INSERT INTO foo VALUES ($i, $l, $f, $s)', i=7, l=4000000000L, f=3.14, s='hi there'),
            'INSERT INTO foo VALUES (7, 4000000000, 3.14, \'hi there\')'
        )
        self.assertEqual(
            c.escape('INSERT INTO foo VALUES ($i, $l, $f, $s)', {'i': 8, 'l': 4000000000L}, i=7, f=3.14, s='hi there'),
            'INSERT INTO foo VALUES (7, 4000000000, 3.14, \'hi there\')'
        )

    def test_commit(self):
        """Test commit commands."""
        self._connect()
        self._make_test_tables()
        self.connection.execute('SET AUTOCOMMIT=0')
        self.connection.execute('INSERT INTO test2 (c) VALUES ($c)', c='hi there')
        r = self.connection.execute('SELECT id, c FROM test2')
        self.assertEquals(r.fetch_row(), (1, 'hi there'))
        self.connection.disconnect()
        c = mysql.connection.Connection()
        c.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
        r = c.execute('SELECT id, c FROM test2')
        self.assertRaises(mysql.exceptions.No_More_Rows, r.fetch_row)
        c.execute('SET AUTOCOMMIT=0')
        c.execute('INSERT INTO test2 (c) VALUES ($c)', c='hi there')
        r = c.execute('SELECT id, c FROM test2')
        self.assertEquals(r.fetch_row(), (2, 'hi there'))
        c.rollback()
        r = c.execute('SELECT id, c FROM test2')
        self.assertRaises(mysql.exceptions.No_More_Rows, r.fetch_row)
        c.execute('INSERT INTO test2 (c) VALUES ($c)', c='foobar')
        r = c.execute('SELECT id, c FROM test2')
        self.assertEquals(r.fetch_row(), (3, 'foobar'))
        c.commit()
        c.disconnect()
        c.connect(user=base_test.test_user, password=base_test.test_password, db=base_test.test_db)
        r = c.execute('SELECT id, c FROM test2')
        self.assertEquals(r.fetch_row(), (3, 'foobar'))
        c.disconnect()

    def test_change_user(self):
        """Test change user."""
        self._connect()
        self.assertRaises(mysql.exceptions.Access_Denied_Error, self.connection.change_user, 'foo', 'bar', 'thing')
        self.connection.change_user(user=base_test.test_user, password=base_test.test_password)

    def test_info(self):
        """Test info commands."""
        self._connect()
        # client_version/client_info
        client_version = self.connection.get_client_version()
        client_info = self.connection.get_client_info()
        major = client_version / 10000
        minor = (client_version / 100) - major*100
        sub = client_version - major*10000 - minor*100
        my_info = '%i.%i.%i' % (major, minor, sub)
        # Special releases (such as 5.0.24a) don't have additional information
        # available in the version command.
        self.assertTrue(client_info.startswith(my_info))

        # server_version/server_info
        server_version = self.connection.get_server_version()
        server_info = self.connection.get_server_info()
        major = server_version / 10000
        minor = (server_version / 100) - major*100
        sub = server_version - major*10000 - minor*100
        my_info = '%i.%i.%i' % (major, minor, sub)
        # Using startswith because alpha/beta releases have additional info.
        self.assertTrue(server_info.startswith(my_info))

        #get_host_info
        info = self.connection.get_host_info()
        self.assertEquals(type(info), str)
        self.assertTrue(len(info) > 0)

        #get_protocol_version
        version = self.connection.get_protocol_version()
        self.assertTrue(version >= 10)

        #last_statement_info
        self.assertRaises(mysql.exceptions.No_Statement_Info_Error, self.connection.last_statement_info)
        self._make_test_tables()
        self.connection.execute('INSERT INTO test1 (i) VALUES (1),(2)')
        self.assertEquals(self.connection.last_statement_info(), 'Records: 2  Duplicates: 0  Warnings: 0')

        #sqlstate
        self.assertEquals(self.connection.sqlstate(), '00000')
        self.assertRaises(mysql.exceptions.Parse_Error, self.connection.execute, 'foo')
        self.assertEquals(self.connection.sqlstate(), '42000')

        #status
        status = self.connection.status()
        self.assertEquals(type(status), str)
        self.assertTrue(len(status) > 0)

        #warning_count
        self.assertEquals(self.connection.warning_count(), 0)
        self.connection.execute('INSERT INTO test1 (tiny) VALUES (100000)')
        self.assertEquals(self.connection.warning_count(), 1)

    def test_last_insert_id(self):
        """Test last insert id."""
        self._connect()
        self._make_test_tables()
        self.connection.execute('INSERT INTO test1 (i) VALUES (7)')
        self.assertEquals(self.connection.last_insert_id(), 1)
        self.connection.execute('INSERT INTO test1 (i) VALUES (8)')
        self.assertEquals(self.connection.last_insert_id(), 2)

    def test_server_commands(self):
        """Test server commands."""
        self._connect()
        self.connection.ping()
        self.connection.disconnect()
        self.assertRaises(mysql.exceptions.Not_Connected_Error, self.connection.ping)
        self.connection.connect(user=base_test.test_user, password=base_test.test_password)
        self.connection.kill_server_thread(self.connection.server_thread_id())
        time.sleep(0.5)
        self.assertRaises(mysql.exceptions.Server_Gone_Error, self.connection.ping)
        self.connection.connect(user=base_test.test_user, password=base_test.test_password)
        # XXX: Hmm, not easy to unittest shutdown_server().

    def test_multi_statements(self):
        """Test multi statements."""
        self._connect()
        self._make_test_tables()
        self.assertRaises(mysql.exceptions.Parse_Error, self.connection.execute, """INSERT INTO test1 (i) VALUES (1); INSERT INTO test1 (i) VALUES (2)""")
        self.connection.enable_multi_statements()
        r = self.connection.execute("""INSERT INTO test1 (i) VALUES (1); INSERT INTO test1 (i) VALUES (2)""")
        self.assertEqual(r, 1)
        self.assertTrue(self.connection.has_more_results())
        r = self.connection.next_result()
        self.assertEqual(r, 1)
        self.assertFalse(self.connection.has_more_results())
        r = self.connection.execute("""SELECT id, i FROM test1 ORDER BY id; SELECT i FROM test1 ORDER BY id""")
        self.assertTrue(self.connection.has_more_results())
        self.assertEqual(r.fetch_row(), (1, 1))
        self.assertEqual(r.fetch_row(), (2, 2))
        self.assertRaises(mysql.exceptions.No_More_Rows, r.fetch_row)
        r = self.connection.next_result()
        self.assertFalse(self.connection.has_more_results())
        self.assertEqual(r.fetch_row(), (1,))
        self.assertEqual(r.fetch_row(), (2,))
        self.assertRaises(mysql.exceptions.No_More_Rows, r.fetch_row)
        self.connection.disable_multi_statements()
        self.assertRaises(mysql.exceptions.Parse_Error, self.connection.execute, """INSERT INTO test1 (i) VALUES (1); INSERT INTO test1 (i) VALUES (2)""")

    def test_ssl(self):
        """Test SSL connect."""
        #ssl_set

    def test_container(self):
        """Test container API."""
        self._connect()
        self._make_test_tables()

        class test1:

            def __init__(self, connection):
                self.connection = connection

            def load(self, id):
                self.id = id
                self.connection.exec_fetch_container(self, 'SELECT vc, i FROM test1 WHERE id=$id')

            def store(self):
                self.connection.exec_container(self, 'INSERT INTO test1 (vc, i) VALUES ($vc, $i)')

        a = test1(self.connection)
        a.vc = 'hi there'
        a.i = 1234
        a.store()
        a.vc = 'rain'
        a.i = 5678
        a.store()

        a.load(1)
        self.assertEqual(a.i, 1234)
        self.assertEqual(a.vc, 'hi there')
        a.load(2)
        self.assertEqual(a.i, 5678)
        self.assertEqual(a.vc, 'rain')


if __name__ == '__main__':
    unittest.main()
