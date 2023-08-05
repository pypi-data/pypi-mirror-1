# $Header: /home/cvs2/mysql/test/test_result.py,v 1.3 2006/08/26 20:19:52 ehuss Exp $
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

"""Test normal result objects."""

__version__ = '$Revision: 1.3 $'

import unittest

import base_test
import mysql.constants
import mysql.exceptions
import mysql.result

class Test(base_test.Base_Mysql_Test_Case2):

    def _simple_insert(self):
        self.assertEqual(1, self.connection.execute('INSERT INTO test1 (i, vc) VALUES ($i, $vc)', i=1, vc='hi there'))
        self.assertEqual(1, self.connection.execute('INSERT INTO test1 (i, vc) VALUES ($i, $vc)', i=2, vc='how are you?'))
        self.assertEqual(1, self.connection.execute('INSERT INTO test1 (i, vc) VALUES ($i, $vc)', i=3, vc='not bad'))

    def test_basic(self):
        """Basic result test."""
        self._simple_insert()
        r = self.connection.execute('SELECT i, vc FROM test1 ORDER BY i')
        self.assertEqual(r.fetch_row(), (1, 'hi there'))
        self.assertEqual(r.fetch_row(), (2, 'how are you?'))
        self.assertEqual(r.fetch_row(), (3, 'not bad'))
        self.assertRaises(mysql.exceptions.No_More_Rows, r.fetch_row)
        r = self.connection.execute('SELECT i, vc FROM test1 ORDER BY i')
        rows = r.fetch_all_rows()
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], (1, 'hi there'))
        self.assertEqual(rows[1], (2, 'how are you?'))
        self.assertEqual(rows[2], (3, 'not bad'))

    def test_len(self):
        """Test __len__."""
        self._simple_insert()
        r = self.connection.execute('SELECT i, vc FROM test1 ORDER BY i', store_result=True)
        self.assertEqual(len(r), 3)
        r = self.connection.execute('SELECT i, vc FROM test1 ORDER BY i', store_result=False)
        # Not sure if this is necessarily worth testing, since it's a quirk of
        # the MySQL library.
        self.assertEqual(len(r), 0)
        self.assertEqual(len(r.fetch_all_rows()), 3)
        self.assertEqual(len(r), 3)

    def test_iter(self):
        """Test iteration."""
        self._simple_insert()
        for i in (False, True):
            r = self.connection.execute('SELECT i, vc FROM test1 ORDER BY i', store_result=i)
            rows = []
            for row in r:
                rows.append(row)
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0], (1, 'hi there'))
            self.assertEqual(rows[1], (2, 'how are you?'))
            self.assertEqual(rows[2], (3, 'not bad'))

    def test_empty(self):
        """Test empty result set."""
        for i in (False, True):
            r = self.connection.execute('SELECT i, vc FROM test1 ORDER BY i', store_result=i)
            self.assertRaises(mysql.exceptions.No_More_Rows, r.fetch_row)
            self.assertEqual([], r.fetch_all_rows())
            self.assertEqual(len(r), 0)

    def test_close(self):
        """Test closing the result."""
        self._simple_insert()
        for i in (False, True):
            r = self.connection.execute('SELECT i, vc FROM test1 ORDER BY i', store_result=i)
            self.assertFalse(r.closed())
            r.close()
            self.assertTrue(r.closed())
            self.assertRaises(mysql.exceptions.Result_Closed_Error, len, r)
            def iter_test():
                return [ x for x in r ]
            self.assertRaises(mysql.exceptions.Result_Closed_Error, iter_test)
            # Test close again, shouldn't do anything.
            r.close()
            self.assertRaises(mysql.exceptions.Result_Closed_Error, r.row_tell)
            self.assertRaises(mysql.exceptions.Result_Closed_Error, r.row_seek, 0)
            self.assertRaises(mysql.exceptions.Result_Closed_Error, r.fetch_row)
            self.assertRaises(mysql.exceptions.Result_Closed_Error, r.fetch_all_rows)
            self.assertRaises(mysql.exceptions.Result_Closed_Error, r.num_fields)
            self.assertRaises(mysql.exceptions.Result_Closed_Error, r.fields)

    def test_row_seek(self):
        """Test row seeking."""
        self._simple_insert()
        r = self.connection.execute('SELECT i, vc FROM test1 ORDER BY i', store_result=True)
        o1 = r.row_tell()
        row = r.fetch_row()
        self.assertEqual(row, (1, 'hi there'))
        o2 = r.row_tell()
        row = r.fetch_row()
        self.assertEqual(row, (2, 'how are you?'))
        r.row_seek(o1)
        row = r.fetch_row()
        self.assertEqual(row, (1, 'hi there'))
        r.row_seek(2)
        row = r.fetch_row()
        self.assertEqual(row, (3, 'not bad'))
        r.row_seek(o2)
        row = r.fetch_row()
        self.assertEqual(row, (2, 'how are you?'))

        r = self.connection.execute('SELECT i, vc FROM test1 ORDER BY i', store_result=False)
        self.assertRaises(mysql.exceptions.Result_Unbuffered_Error, r.row_tell)
        self.assertRaises(mysql.exceptions.Result_Unbuffered_Error, r.row_seek, 0)

    def test_fields(self):
        """Test field checking."""
        ff = mysql.constants.field_flags
        ft = mysql.constants.field_types

        def check_field(field, name, default, length, flags, decimals, type):
            self.assertEquals(field.name, name)
            self.assertEquals(field.org_name, name)
            self.assertEquals(field.table, 'test1')
            self.assertEquals(field.org_table, 'test1')
            self.assertEquals(field.db, base_test.test_db)
            self.assertEquals(field.catalog, 'def')
            self.assertEquals(field.default, default)
            self.assertEquals(field.length, length)
            self.assertEquals(field.flags & ff.KNOWN_FLAGS, flags)
            self.assertEquals(field.decimals, decimals)
            self.assertEquals(field.type, type)

        r = self.connection.execute('SELECT * FROM test1', store_result=True)
        self.assertEqual(r.num_fields(), 38)
        fields = r.fields()
        self.assertEqual(len(fields), 38)

        check_field(fields[0],  'id',           None, 10,           (ff.NOT_NULL|ff.PRI_KEY|ff.UNSIGNED|ff.AUTO_INCREMENT), 0, ft.INTEGER)
        check_field(fields[1],  'utiny',        None, 3,            (ff.UNSIGNED),  0, ft.TINYINT)
        check_field(fields[2],  'tiny',         None, 4,            (0),            0, ft.TINYINT)
        check_field(fields[3],  'usmall',       None, 5,            (ff.UNSIGNED),  0, ft.SMALLINT)
        check_field(fields[4],  'small',        None, 6,            (0),            0, ft.SMALLINT)
        check_field(fields[5],  'umedium',      None, 8,            (ff.UNSIGNED),  0, ft.MEDIUMINT)
        check_field(fields[6],  'medium',       None, 9,            (0),            0, ft.MEDIUMINT)
        check_field(fields[7],  'ui',           None, 10,           (ff.UNSIGNED),  0, ft.INTEGER)
        check_field(fields[8],  'i',            None, 11,           (0),            0, ft.INTEGER)
        check_field(fields[9],  'ubigi',        None, 20,           (ff.UNSIGNED),  0, ft.BIGINT)
        check_field(fields[10], 'bigi',         None, 20,           (0),            0, ft.BIGINT)
        if self.connection.get_server_version() < 50021:
            check_field(fields[11], 'bits',         None, 8,            (0),            0, ft.BIT)
        else:
            check_field(fields[11], 'bits',         None, 64,            (0),            0, ft.BIT)
        check_field(fields[12], 'boo',          None, 1,            (0),            0, ft.TINYINT)
        check_field(fields[13], 'uflo',         None, 12,           (ff.UNSIGNED),  31, ft.FLOAT)
        check_field(fields[14], 'flo',          None, 12,           (0),            31, ft.FLOAT)
        check_field(fields[15], 'udoub',        None, 22,           (ff.UNSIGNED),  31, ft.DOUBLE)
        check_field(fields[16], 'doub',         None, 22,           (0),            31, ft.DOUBLE)
        check_field(fields[17], 'udeci',        None, 66,           (ff.UNSIGNED),  30, ft.NEWDECIMAL)
        check_field(fields[18], 'deci',         None, 67,           (0),            30, ft.NEWDECIMAL)
        check_field(fields[19], 'dt_date',      None, 10,           (ff.BINARY),    0, ft.DATE)
        check_field(fields[20], 'dt_datetime',  None, 19,           (ff.BINARY),    0, ft.DATETIME)
        check_field(fields[21], 'dt_timestamp', None, 19,           (ff.NOT_NULL|ff.UNSIGNED|ff.ZEROFILL|ff.BINARY), 0, ft.TIMESTAMP)
        check_field(fields[22], 'dt_time',      None, 8,            (ff.BINARY),    0, ft.TIME)
        check_field(fields[23], 'dt_year',      None, 4,            (ff.UNSIGNED|ff.ZEROFILL), 0, ft.YEAR)
        check_field(fields[24], 'c',            None, 100,          (0),            0, ft.CHAR)
        check_field(fields[25], 'vc',           None, 100,          (0),            0, ft.VARCHAR)
        check_field(fields[26], 'bin',          None, 100,          (ff.BINARY),    0, ft.CHAR)
        check_field(fields[27], 'vbin',         None, 100,          (ff.BINARY),    0, ft.VARCHAR)
        check_field(fields[28], 'e',            None, 5,            (0),            0, ft.CHAR)
        check_field(fields[29], 's',            None, 14,           (0),            0, ft.CHAR)
        check_field(fields[30], 'blob_tiny',    None, 255,          (ff.BINARY),    0, ft.BLOB)
        check_field(fields[31], 'blob_medium',  None, 16777215,     (ff.BINARY),    0, ft.BLOB)
        check_field(fields[32], 'blob_blob',    None, 65535,        (ff.BINARY),    0, ft.BLOB)
        check_field(fields[33], 'blob_long',    None, 4294967295,   (ff.BINARY),    0, ft.BLOB)
        check_field(fields[34], 'text_tiny',    None, 255,          (0),            0, ft.BLOB)
        check_field(fields[35], 'text_medium',  None, 16777215,     (0),            0, ft.BLOB)
        check_field(fields[36], 'text_text',    None, 65535,        (0),            0, ft.BLOB)
        check_field(fields[37], 'text_long',    None, 4294967295,   (0),            0, ft.BLOB)

        # Simple alias test.
        r = self.connection.execute('SELECT id AS foo FROM test1 AS bar', store_result=True)
        self.assertEqual(r.num_fields(), 1)
        fields = r.fields()
        self.assertEqual(len(fields), 1)
        field = fields[0]
        self.assertEqual(field.name, 'foo')
        self.assertEqual(field.org_name, 'id')
        self.assertEqual(field.table, 'bar')
        self.assertEqual(field.org_table, 'test1')

    def test_disconnect(self):
        """Test disconnecting."""
        self._simple_insert()
        r = self.connection.execute('SELECT i, vc FROM test1 ORDER BY i', store_result=False)
        self.connection.disconnect()
        self.connection = None
        self.assertRaises(mysql.exceptions.Result_Closed_Error, r.fetch_row)

    def test_concurrent_results(self):
        """Test having concurrent live result objects."""
        self._simple_insert()
        r1 = self.connection.execute('SELECT i, vc FROM test1 WHERE i=1', store_result=True)
        r2 = self.connection.execute('SELECT i, vc FROM test1 WHERE i>1', store_result=True)
        self.assertEqual(len(r1.fetch_all_rows()), 1)
        self.assertEqual(len(r2.fetch_all_rows()), 2)
        r1.close()
        r2.close()
        r1 = self.connection.execute('SELECT i, vc FROM test1 WHERE i=1', store_result=False)
        r2 = self.connection.execute('SELECT i, vc FROM test1 WHERE i>1', store_result=False)
        self.assertRaises(mysql.exceptions.Result_Closed_Error, r1.fetch_row)
        self.assertEqual(len(r2.fetch_all_rows()), 2)
        # We should probably exhaustively test every method in the Connection
        # object that it will force a close of the result object.

if __name__ == '__main__':
    unittest.main()
