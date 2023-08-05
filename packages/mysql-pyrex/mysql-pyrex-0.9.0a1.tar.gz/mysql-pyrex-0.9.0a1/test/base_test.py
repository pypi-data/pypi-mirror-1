# $Header: /home/cvs2/mysql/test/base_test.py,v 1.3 2006/08/26 20:19:52 ehuss Exp $
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

"""Base classes for unittest code."""

__version__ = '$Revision: 1.3 $'

import unittest

import mysql.connection
import mysql.exceptions

test_user = 'py_mysql_test'
test_password = ''
test_db = 'py_mysql_test'

class Base_Mysql_Test_Case(unittest.TestCase):

    connection = None

    def fake_test(self):
        """Fake test method for experimenting."""
        pass

    def _connect(self):
        if self.connection is not None:
            return
        c = self._make_connection(with_clear=True)
        self.connection = c

    def _make_connection(self, with_clear=False):
        c = mysql.connection.Connection()
        c.connect(user=test_user, password=test_password)
        try:
            c.select_db(test_db)
        except mysql.exceptions.Bad_DB_Error:
            c.execute('CREATE DATABASE %s' % (test_db,))
        else:
            if with_clear:
                c.execute('DROP DATABASE %s' % (test_db,))
                c.execute('CREATE DATABASE %s' % (test_db,))

        c.select_db(test_db)
        return c

    def _clear_tables(self):
        c = self._make_connection()
        try:
            c.execute('DELETE FROM test1')
            c.execute('DELETE FROM test2')
        except mysql.exceptions.No_Such_Table:
            pass
        c.disconnect()

    def _shutdown(self):
        if self.connection:
            self.connection.disconnect()
            self.connection = None
        c = mysql.connection.Connection()
        try:
            c.connect(user=test_user, password=test_password)
        except mysql.exceptions.Error:
            pass
        else:
            try:
                c.execute('DROP DATABASE %s' % (test_db,))
            except mysql.exceptions.Error:
                pass
            c.disconnect()

    def _make_test_tables(self):
        self.connection.execute("""
CREATE TABLE test1 (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    utiny TINYINT UNSIGNED,
    tiny TINYINT,
    usmall SMALLINT UNSIGNED,
    small SMALLINT,
    umedium MEDIUMINT UNSIGNED,
    medium MEDIUMINT,
    ui INT UNSIGNED,
    i INT,
    ubigi BIGINT UNSIGNED,
    bigi BIGINT,
    bits BIT(64),
    boo BOOL,
    uflo FLOAT UNSIGNED,
    flo FLOAT,
    udoub DOUBLE UNSIGNED,
    doub DOUBLE,
    udeci DECIMAL (65,30) UNSIGNED,
    deci DECIMAL (65,30),
    dt_date DATE,
    dt_datetime DATETIME,
    dt_timestamp TIMESTAMP,
    dt_time TIME,
    dt_year YEAR,
    c CHAR(100),
    vc VARCHAR(100),
    bin BINARY(100),
    vbin VARBINARY(100),
    e ENUM('one', 'two', 'three', 'four'),
    s SET('red', 'green', 'blue'),
    blob_tiny TINYBLOB,
    blob_medium MEDIUMBLOB,
    blob_blob BLOB,
    blob_long LONGBLOB,
    text_tiny TINYTEXT,
    text_medium MEDIUMTEXT,
    text_text TEXT,
    text_long LONGTEXT,
    PRIMARY KEY (id)
)
""")
        self.connection.execute("""
CREATE TABLE test2 (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    c CHAR(100),
    bin BINARY(100),
    PRIMARY KEY (id)
) ENGINE=InnoDB
""")

class Base_Mysql_Test_Case2(Base_Mysql_Test_Case):

    def setUp(self):
        self._connect()
        self._make_test_tables()

    def tearDown(self):
        self._shutdown()
