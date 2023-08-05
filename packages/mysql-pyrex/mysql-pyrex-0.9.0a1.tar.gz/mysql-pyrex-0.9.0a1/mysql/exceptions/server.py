# $Header: /home/cvs2/mysql/mysql/exceptions/server.py,v 1.5 2006/11/13 02:39:08 ehuss Exp $
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

"""Exceptions from the MySQL server.

These are all errors that the server-side of the MySQL API may generate.

Because older clients may connect to newer versions of the server, the server
may generate new errors that this client is not aware of.  In this case, the
exception `mysql.exceptions.client.Unknown_Error` is raised.
"""

__version__ = '$Revision: 1.5 $'

from mysql.exceptions.base import MySQL_Error

class Hashchk(MySQL_Error):

    """hashchk """

class Nisamchk(MySQL_Error):

    """isamchk"""

class No(MySQL_Error):

    """NO"""

class Yes(MySQL_Error):

    """YES"""

class Cant_Create_File(MySQL_Error):

    """Can't create file '%s' (errno: %d)"""

class Cant_Create_Table(MySQL_Error):

    """Can't create table '%s' (errno: %d)"""

class Cant_Create_DB(MySQL_Error):

    """Can't create database '%s' (errno: %d)"""

class DB_Create_Exists(MySQL_Error):

    """Can't create database '%s'; database exists"""

class DB_Drop_Exists(MySQL_Error):

    """Can't drop database '%s'; database doesn't exist"""

class DB_Drop_Delete(MySQL_Error):

    """Error dropping database (can't delete '%s', errno: %d)"""

class DB_Drop_Rmdir(MySQL_Error):

    """Error dropping database (can't rmdir '%s', errno: %d)"""

class Cant_Delete_File(MySQL_Error):

    """Error on delete of '%s' (errno: %d)"""

class Cant_Find_System_Rec(MySQL_Error):

    """Can't read record in system table"""

class Cant_Get_Stat(MySQL_Error):

    """Can't get status of '%s' (errno: %d)"""

class Cant_Get_Wd(MySQL_Error):

    """Can't get working directory (errno: %d)"""

class Cant_Lock(MySQL_Error):

    """Can't lock file (errno: %d)"""

class Cant_Open_File(MySQL_Error):

    """Can't open file: '%s' (errno: %d)"""

class File_Not_Found(MySQL_Error):

    """Can't find file: '%s' (errno: %d)"""

class Cant_Read_Dir(MySQL_Error):

    """Can't read dir of '%s' (errno: %d)"""

class Cant_Set_Wd(MySQL_Error):

    """Can't change dir to '%s' (errno: %d)"""

class Checkread(MySQL_Error):

    """Record has changed since last read in table '%s'"""

class Disk_Full(MySQL_Error):

    """Disk full (%s); waiting for someone to free some space..."""

class Dup_Key(MySQL_Error):

    """Can't write; duplicate key in table '%s'"""

class Error_On_Close(MySQL_Error):

    """Error on close of '%s' (errno: %d)"""

class Error_On_Read(MySQL_Error):

    """Error reading file '%s' (errno: %d)"""

class Error_On_Rename(MySQL_Error):

    """Error on rename of '%s' to '%s' (errno: %d)"""

class Error_On_Write(MySQL_Error):

    """Error writing file '%s' (errno: %d)"""

class File_Used(MySQL_Error):

    """'%s' is locked against change"""

class Filsort_Abort(MySQL_Error):

    """Sort aborted"""

class Form_Not_Found(MySQL_Error):

    """View '%s' doesn't exist for '%s'"""

class Get_Errno(MySQL_Error):

    """Got error %d from storage engine"""

class Illegal_Ha(MySQL_Error):

    """Table storage engine for '%s' doesn't have this option"""

class Key_Not_Found(MySQL_Error):

    """Can't find record in '%s'"""

class Not_Form_File(MySQL_Error):

    """Incorrect information in file: '%s'"""

class Not_Keyfile(MySQL_Error):

    """Incorrect key file for table '%s'; try to repair it"""

class Old_Keyfile(MySQL_Error):

    """Old key file for table '%s'; repair it!"""

class Open_As_Readonly(MySQL_Error):

    """Table '%s' is read only"""

class Outofmemory(MySQL_Error):

    """Out of memory; restart server and try again (needed %d bytes)"""

class Out_Of_Sortmemory(MySQL_Error):

    """Out of sort memory; increase server sort buffer size"""

class Unexpected_Eof(MySQL_Error):

    """Unexpected EOF found when reading file '%s' (errno: %d)"""

class Con_Count_Error(MySQL_Error):

    """Too many connections"""

class Out_Of_Resources(MySQL_Error):

    """Out of memory; check if mysqld or some other process uses all available
    memory; if not, you may have to use 'ulimit' to allow mysqld to use more
    memory or you can add more swap space
    """

class Bad_Host_Error(MySQL_Error):

    """Can't get hostname for your address"""

class Handshake_Error(MySQL_Error):

    """Bad handshake"""

class DB_Access_Denied_Error(MySQL_Error):

    """Access denied for user '%s'@'%s' to database '%s'"""

class Access_Denied_Error(MySQL_Error):

    """Access denied for user '%s'@'%s' (using password: %s)"""

class No_DB_Error(MySQL_Error):

    """No database selected"""

class Unknown_Com_Error(MySQL_Error):

    """Unknown command"""

class Bad_Null_Error(MySQL_Error):

    """Column '%s' cannot be null"""

class Bad_DB_Error(MySQL_Error):

    """Unknown database '%s'"""

class Table_Exists_Error(MySQL_Error):

    """Table '%s' already exists"""

class Bad_Table_Error(MySQL_Error):

    """Unknown table '%s'"""

class Non_Uniq_Error(MySQL_Error):

    """Column '%s' in %s is ambiguous"""

class Server_Shutdown(MySQL_Error):

    """Server shutdown in progress"""

class Bad_Field_Error(MySQL_Error):

    """Unknown column '%s' in '%s'"""

class Wrong_Field_With_Group(MySQL_Error):

    """'%s' isn't in GROUP BY"""

class Wrong_Group_Field(MySQL_Error):

    """Can't group on '%s'"""

class Wrong_Sum_Select(MySQL_Error):

    """Statement has sum functions and columns in same statement"""

class Wrong_Value_Count(MySQL_Error):

    """Column count doesn't match value count"""

class Too_Long_Ident(MySQL_Error):

    """Identifier name '%s' is too long"""

class Dup_Fieldname(MySQL_Error):

    """Duplicate column name '%s'"""

class Dup_Keyname(MySQL_Error):

    """Duplicate key name '%s'"""

class Dup_Entry(MySQL_Error):

    """Duplicate entry '%s' for key %d"""

class Wrong_Field_Spec(MySQL_Error):

    """Incorrect column specifier for column '%s'"""

class Parse_Error(MySQL_Error):

    """%s near '%s' at line %d"""

class Empty_Query(MySQL_Error):

    """Query was empty"""

class Nonuniq_Table(MySQL_Error):

    """Not unique table/alias: '%s'"""

class Invalid_Default(MySQL_Error):

    """Invalid default value for '%s'"""

class Multiple_Pri_Key(MySQL_Error):

    """Multiple primary key defined"""

class Too_Many_Keys(MySQL_Error):

    """Too many keys specified; max %d keys allowed"""

class Too_Many_Key_Parts(MySQL_Error):

    """Too many key parts specified; max %d parts allowed"""

class Too_Long_Key(MySQL_Error):

    """Specified key was too long; max key length is %d bytes"""

class Key_Column_Does_Not_Exits(MySQL_Error):

    """Key column '%s' doesn't exist in table"""

class Blob_Used_As_Key(MySQL_Error):

    """BLOB column '%s' can't be used in key specification with the used table
    type
    """

class Too_Big_Fieldlength(MySQL_Error):

    """Column length too big for column '%s' (max = %d); use BLOB or TEXT
    instead
    """

class Wrong_Auto_Key(MySQL_Error):

    """Incorrect table definition; there can be only one auto column and it
    must be defined as a key
    """

class Ready(MySQL_Error):

    """%s: ready for connections. Version: '%s' socket: '%s' port: %d"""

class Normal_Shutdown(MySQL_Error):

    """%s: Normal shutdown"""

class Got_Signal(MySQL_Error):

    """%s: Got signal %d. Aborting!"""

class Shutdown_Complete(MySQL_Error):

    """%s: Shutdown complete"""

class Forcing_Close(MySQL_Error):

    """%s: Forcing close of thread %ld user: '%s'"""

class Ipsock_Error(MySQL_Error):

    """Can't create IP socket"""

class No_Such_Index(MySQL_Error):

    """Table '%s' has no index like the one used in CREATE INDEX; recreate the
    table
    """

class Wrong_Field_Terminators(MySQL_Error):

    """Field separator argument is not what is expected; check the manual"""

class Blobs_And_No_Terminated(MySQL_Error):

    """You can't use fixed rowlength with BLOBs; please use 'fields terminated
    by'
    """

class Textfile_Not_Readable(MySQL_Error):

    """The file '%s' must be in the database directory or be readable by all"""

class File_Exists_Error(MySQL_Error):

    """File '%s' already exists"""

class Load_Info(MySQL_Error):

    """Records: %ld Deleted: %ld Skipped: %ld Warnings: %ld"""

class Alter_Info(MySQL_Error):

    """Records: %ld Duplicates: %ld"""

class Wrong_Sub_Key(MySQL_Error):

    """Incorrect sub part key; the used key part isn't a string, the used
    length is longer than the key part, or the storage engine doesn't support
    unique sub keys
    """

class Cant_Remove_All_Fields(MySQL_Error):

    """You can't delete all columns with ALTER TABLE; use DROP TABLE instead"""

class Cant_Drop_Field_Or_Key(MySQL_Error):

    """Can't DROP '%s'; check that column/key exists"""

class Insert_Info(MySQL_Error):

    """Records: %ld Duplicates: %ld Warnings: %ld"""

class Update_Table_Used(MySQL_Error):

    """You can't specify target table '%s' for update in FROM clause"""

class No_Such_Thread(MySQL_Error):

    """Unknown thread id: %lu"""

class Kill_Denied_Error(MySQL_Error):

    """You are not owner of thread %lu"""

class No_Tables_Used(MySQL_Error):

    """No tables used"""

class Too_Big_Set(MySQL_Error):

    """Too many strings for column %s and SET"""

class No_Unique_Logfile(MySQL_Error):

    """Can't generate a unique log-filename %s.(1-999)"""

class Table_Not_Locked_For_Write(MySQL_Error):

    """Table '%s' was locked with a READ lock and can't be updated"""

class Table_Not_Locked(MySQL_Error):

    """Table '%s' was not locked with LOCK TABLES"""

class Blob_Cant_Have_Default(MySQL_Error):

    """BLOB/TEXT column '%s' can't have a default value"""

class Wrong_DB_Name(MySQL_Error):

    """Incorrect database name '%s'"""

class Wrong_Table_Name(MySQL_Error):

    """Incorrect table name '%s'"""

class Too_Big_Select(MySQL_Error):

    """The SELECT would examine more than MAX_JOIN_SIZE rows; check your WHERE
    and use SET SQL_BIG_SELECTS=1 or SET SQL_MAX_JOIN_SIZE=# if the SELECT is
    okay
    """

class Unknown_Error(MySQL_Error):

    """Unknown error"""

class Unknown_Procedure(MySQL_Error):

    """Unknown procedure '%s'"""

class Wrong_Paramcount_To_Procedure(MySQL_Error):

    """Incorrect parameter count to procedure '%s'"""

class Wrong_Parameters_To_Procedure(MySQL_Error):

    """Incorrect parameters to procedure '%s'"""

class Unknown_Table(MySQL_Error):

    """Unknown table '%s' in %s"""

class Field_Specified_Twice(MySQL_Error):

    """Column '%s' specified twice"""

class Invalid_Group_Func_Use(MySQL_Error):

    """Invalid use of group function"""

class Unsupported_Extension(MySQL_Error):

    """Table '%s' uses an extension that doesn't exist in this MySQL version"""

class Table_Must_Have_Columns(MySQL_Error):

    """A table must have at least 1 column"""

class Record_File_Full(MySQL_Error):

    """The table '%s' is full"""

class Unknown_Character_Set(MySQL_Error):

    """Unknown character set: '%s'"""

class Too_Many_Tables(MySQL_Error):

    """Too many tables; MySQL can only use %d tables in a join"""

class Too_Many_Fields(MySQL_Error):

    """Too many columns"""

class Too_Big_Rowsize(MySQL_Error):

    """Row size too large. The maximum row size for the used table type, not
    counting BLOBs, is %ld. You have to change some columns to TEXT or BLOBs
    """

class Stack_Overrun(MySQL_Error):

    """Thread stack overrun: Used: %ld of a %ld stack. Use 'mysqld -O
    thread_stack=#' to specify a bigger stack if needed
    """

class Wrong_Outer_Join(MySQL_Error):

    """Cross dependency found in OUTER JOIN; examine your ON conditions"""

class Null_Column_In_Index(MySQL_Error):

    """Column '%s' is used with UNIQUE or INDEX but is not defined as NOT
    NULL
    """

class Cant_Find_Udf(MySQL_Error):

    """Can't load function '%s'"""

class Cant_Initialize_Udf(MySQL_Error):

    """Can't initialize function '%s'; %s"""

class Udf_No_Paths(MySQL_Error):

    """No paths allowed for shared library"""

class Udf_Exists(MySQL_Error):

    """Function '%s' already exists"""

class Cant_Open_Library(MySQL_Error):

    """Can't open shared library '%s' (errno: %d %s)"""

class Cant_Find_Dl_Entry(MySQL_Error):

    """Can't find function '%s' in library'"""

class Function_Not_Defined(MySQL_Error):

    """Function '%s' is not defined"""

class Host_Is_Blocked(MySQL_Error):

    """Host '%s' is blocked because of many connection errors; unblock with
    'mysqladmin flush-hosts'
    """

class Host_Not_Privileged(MySQL_Error):

    """Host '%s' is not allowed to connect to this MySQL server"""

class Password_Anonymous_User(MySQL_Error):

    """You are using MySQL as an anonymous user and anonymous users are not
    allowed to change passwords
    """

class Password_Not_Allowed(MySQL_Error):

    """You must have privileges to update tables in the mysql database to be
    able to change passwords for others
    """

class Password_No_Match(MySQL_Error):

    """Can't find any matching row in the user table"""

class Update_Info(MySQL_Error):

    """Rows matched: %ld Changed: %ld Warnings: %ld"""

class Cant_Create_Thread(MySQL_Error):

    """Can't create a new thread (errno %d); if you are not out of available
    memory, you can consult the manual for a possible OS-dependent bug
    """

class Wrong_Value_Count_On_Row(MySQL_Error):

    """Column count doesn't match value count at row %ld"""

class Cant_Reopen_Table(MySQL_Error):

    """Can't reopen table: '%s'"""

class Invalid_Use_Of_Null(MySQL_Error):

    """Invalid use of NULL value"""

class Regexp_Error(MySQL_Error):

    """Got error '%s' from regexp"""

class Mix_Of_Group_Func_And_Fields(MySQL_Error):

    """Mixing of GROUP columns (MIN(),MAX(),COUNT(),...) with no GROUP columns
    is illegal if there is no GROUP BY clause
    """

class Nonexisting_Grant(MySQL_Error):

    """There is no such grant defined for user '%s' on host '%s'"""

class Tableaccess_Denied_Error(MySQL_Error):

    """%s command denied to user '%s'@'%s' for table '%s'"""

class Columnaccess_Denied_Error(MySQL_Error):

    """%s command denied to user '%s'@'%s' for column '%s' in table '%s'"""

class Illegal_Grant_For_Table(MySQL_Error):

    """Illegal GRANT/REVOKE command; please consult the manual to see which
    privileges can be used
    """

class Grant_Wrong_Host_Or_User(MySQL_Error):

    """The host or user argument to GRANT is too long"""

class No_Such_Table(MySQL_Error):

    """Table '%s.%s' doesn't exist"""

class Nonexisting_Table_Grant(MySQL_Error):

    """There is no such grant defined for user '%s' on host '%s' on table '%s'"""

class Not_Allowed_Command(MySQL_Error):

    """The used command is not allowed with this MySQL version"""

class Syntax_Error(MySQL_Error):

    """You have an error in your SQL syntax; check the manual that corresponds
    to your MySQL server version for the right syntax to use
    """

class Delayed_Cant_Change_Lock(MySQL_Error):

    """Delayed insert thread couldn't get requested lock for table %s"""

class Too_Many_Delayed_Threads(MySQL_Error):

    """Too many delayed threads in use"""

class Aborting_Connection(MySQL_Error):

    """Aborted connection %ld to db: '%s' user: '%s' (%s)"""

class Net_Packet_Too_Large(MySQL_Error):

    """Got a packet bigger than 'max_allowed_packet' bytes"""

class Net_Read_Error_From_Pipe(MySQL_Error):

    """Got a read error from the connection pipe"""

class Net_Fcntl_Error(MySQL_Error):

    """Got an error from fcntl()"""

class Net_Packets_Out_Of_Order(MySQL_Error):

    """Got packets out of order"""

class Net_Uncompress_Error(MySQL_Error):

    """Couldn't uncompress communication packet"""

class Net_Read_Error(MySQL_Error):

    """Got an error reading communication packets"""

class Net_Read_Interrupted(MySQL_Error):

    """Got timeout reading communication packets"""

class Net_Error_On_Write(MySQL_Error):

    """Got an error writing communication packets"""

class Net_Write_Interrupted(MySQL_Error):

    """Got timeout writing communication packets"""

class Too_Long_String(MySQL_Error):

    """Result string is longer than 'max_allowed_packet' bytes"""

class Table_Cant_Handle_Blob(MySQL_Error):

    """The used table type doesn't support BLOB/TEXT columns"""

class Table_Cant_Handle_Auto_Increment(MySQL_Error):

    """The used table type doesn't support AUTO_INCREMENT columns"""

class Delayed_Insert_Table_Locked(MySQL_Error):

    """INSERT DELAYED can't be used with table '%s' because it is locked with
    LOCK TABLES
    """

class Wrong_Column_Name(MySQL_Error):

    """Incorrect column name '%s'"""

class Wrong_Key_Column(MySQL_Error):

    """The used storage engine can't index column '%s'"""

class Wrong_Mrg_Table(MySQL_Error):

    """All tables in the MERGE table are not identically defined"""

class Dup_Unique(MySQL_Error):

    """Can't write, because of unique constraint, to table '%s'"""

class Blob_Key_Without_Length(MySQL_Error):

    """BLOB/TEXT column '%s' used in key specification without a key length"""

class Primary_Cant_Have_Null(MySQL_Error):

    """All parts of a PRIMARY KEY must be NOT NULL; if you need NULL in a key,
    use UNIQUE instead
    """

class Too_Many_Rows(MySQL_Error):

    """Result consisted of more than one row"""

class Requires_Primary_Key(MySQL_Error):

    """This table type requires a primary key"""

class No_Raid_Compiled(MySQL_Error):

    """This version of MySQL is not compiled with RAID support"""

class Update_Without_Key_In_Safe_Mode(MySQL_Error):

    """You are using safe update mode and you tried to update a table without a
    WHERE that uses a KEY column
    """

class Key_Does_Not_Exits(MySQL_Error):

    """Key '%s' doesn't exist in table '%s'"""

class Check_No_Such_Table(MySQL_Error):

    """Can't open table"""

class Check_Not_Implemented(MySQL_Error):

    """The storage engine for the table doesn't support %s"""

class Cant_Do_This_During_An_Transaction(MySQL_Error):

    """You are not allowed to execute this command in a transaction"""

class Error_During_Commit(MySQL_Error):

    """Got error %d during COMMIT"""

class Error_During_Rollback(MySQL_Error):

    """Got error %d during ROLLBACK"""

class Error_During_Flush_Logs(MySQL_Error):

    """Got error %d during FLUSH_LOGS"""

class Error_During_Checkpoint(MySQL_Error):

    """Got error %d during CHECKPOINT"""

class New_Aborting_Connection(MySQL_Error):

    """Aborted connection %ld to db: '%s' user: '%s' host: '%s' (%s)"""

class Dump_Not_Implemented(MySQL_Error):

    """The storage engine for the table does not support binary table dump"""

class Flush_Master_Binlog_Closed(MySQL_Error):

    """Binlog closed, cannot RESET MASTER"""

class Index_Rebuild(MySQL_Error):

    """Failed rebuilding the index of dumped table '%s'"""

class Master(MySQL_Error):

    """Error from master: '%s'"""

class Master_Net_Read(MySQL_Error):

    """Net error reading from master"""

class Master_Net_Write(MySQL_Error):

    """Net error writing to master"""

class Ft_Matching_Key_Not_Found(MySQL_Error):

    """Can't find FULLTEXT index matching the column list"""

class Lock_Or_Active_Transaction(MySQL_Error):

    """Can't execute the given command because you have active locked tables or
    an active transaction
    """

class Unknown_System_Variable(MySQL_Error):

    """Unknown system variable '%s'"""

class Crashed_On_Usage(MySQL_Error):

    """Table '%s' is marked as crashed and should be repaired"""

class Crashed_On_Repair(MySQL_Error):

    """Table '%s' is marked as crashed and last (automatic?) repair failed"""

class Warning_Not_Complete_Rollback(MySQL_Error):

    """Some non-transactional changed tables couldn't be rolled back"""

class Trans_Cache_Full(MySQL_Error):

    """Multi-statement transaction required more than 'max_binlog_cache_size'
    bytes of storage; increase this mysqld variable and try again
    """

class Slave_Must_Stop(MySQL_Error):

    """This operation cannot be performed with a running slave; run STOP SLAVE
    first
    """

class Slave_Not_Running(MySQL_Error):

    """This operation requires a running slave; configure slave and do START
    SLAVE
    """

class Bad_Slave(MySQL_Error):

    """The server is not configured as slave; fix in config file or with CHANGE
    MASTER TO
    """

class Master_Info(MySQL_Error):

    """Could not initialize master info structure; more error messages can be
    found in the MySQL error log
    """

class Slave_Thread(MySQL_Error):

    """Could not create slave thread; check system resources"""

class Too_Many_User_Connections(MySQL_Error):

    """User %s already has more than 'max_user_connections' active
    connections
    """

class Set_Constants_Only(MySQL_Error):

    """You may only use constant expressions with SET"""

class Lock_Wait_Timeout(MySQL_Error):

    """Lock wait timeout exceeded; try restarting transaction"""

class Lock_Table_Full(MySQL_Error):

    """The total number of locks exceeds the lock table size"""

class Read_Only_Transaction(MySQL_Error):

    """Update locks cannot be acquired during a READ UNCOMMITTED transaction"""

class Drop_DB_With_Read_Lock(MySQL_Error):

    """DROP DATABASE not allowed while thread is holding global read lock"""

class Create_DB_With_Read_Lock(MySQL_Error):

    """CREATE DATABASE not allowed while thread is holding global read lock"""

class Wrong_Arguments(MySQL_Error):

    """Incorrect arguments to %s"""

class No_Permission_To_Create_User(MySQL_Error):

    """'%s'@'%s' is not allowed to create new users"""

class Union_Tables_In_Different_Dir(MySQL_Error):

    """Incorrect table definition; all MERGE tables must be in the same
    database
    """

class Lock_Deadlock(MySQL_Error):

    """Deadlock found when trying to get lock; try restarting transaction"""

class Table_Cant_Handle_Ft(MySQL_Error):

    """The used table type doesn't support FULLTEXT indexes"""

class Cannot_Add_Foreign(MySQL_Error):

    """Cannot add foreign key constraint"""

class No_Referenced_Row(MySQL_Error):

    """Cannot add or update a child row: a foreign key constraint fails"""

class Row_Is_Referenced(MySQL_Error):

    """Cannot delete or update a parent row: a foreign key constraint fails"""

class Connect_To_Master(MySQL_Error):

    """Error connecting to master: %s"""

class Query_On_Master(MySQL_Error):

    """Error running query on master: %s"""

class Error_When_Executing_Command(MySQL_Error):

    """Error when executing command %s: %s"""

class Wrong_Usage(MySQL_Error):

    """Incorrect usage of %s and %s"""

class Wrong_Number_Of_Columns_In_Select(MySQL_Error):

    """The used SELECT statements have a different number of columns"""

class Cant_Update_With_Readlock(MySQL_Error):

    """Can't execute the query because you have a conflicting read lock"""

class Mixing_Not_Allowed(MySQL_Error):

    """Mixing of transactional and non-transactional tables is disabled"""

class Dup_Argument(MySQL_Error):

    """Option '%s' used twice in statement"""

class User_Limit_Reached(MySQL_Error):

    """User '%s' has exceeded the '%s' resource (current value: %ld)"""

class Specific_Access_Denied_Error(MySQL_Error):

    """Access denied; you need the %s privilege for this operation"""

class Local_Variable(MySQL_Error):

    """Variable '%s' is a SESSION variable and can't be used with SET GLOBAL"""

class Global_Variable(MySQL_Error):

    """Variable '%s' is a GLOBAL variable and should be set with SET GLOBAL"""

class No_Default(MySQL_Error):

    """Variable '%s' doesn't have a default value"""

class Wrong_Value_For_Var(MySQL_Error):

    """Variable '%s' can't be set to the value of '%s'"""

class Wrong_Type_For_Var(MySQL_Error):

    """Incorrect argument type to variable '%s'"""

class Var_Cant_Be_Read(MySQL_Error):

    """Variable '%s' can only be set, not read"""

class Cant_Use_Option_Here(MySQL_Error):

    """Incorrect usage/placement of '%s'"""

class Not_Supported_Yet(MySQL_Error):

    """This version of MySQL doesn't yet support '%s'"""

class Master_Fatal_Error_Reading_Binlog(MySQL_Error):

    """Got fatal error %d: '%s' from master when reading data from binary
    log
    """

class Slave_Ignored_Table(MySQL_Error):

    """Slave SQL thread ignored the query because of replicate-\\*-table rules"""

class Incorrect_Global_Local_Var(MySQL_Error):

    """Variable '%s' is a %s variable"""

class Wrong_Fk_Def(MySQL_Error):

    """Incorrect foreign key definition for '%s': %s"""

class Key_Ref_Do_Not_Match_Table_Ref(MySQL_Error):

    """Key reference and table reference don't match"""

class Operand_Columns(MySQL_Error):

    """Operand should contain %d column(s)"""

class Subquery_No_1_Row(MySQL_Error):

    """Subquery returns more than 1 row"""

class Unknown_Stmt_Handler(MySQL_Error):

    """Unknown prepared statement handler (%.*s) given to %s"""

class Corrupt_Help_DB(MySQL_Error):

    """Help database is corrupt or does not exist"""

class Cyclic_Reference(MySQL_Error):

    """Cyclic reference on subqueries"""

class Auto_Convert(MySQL_Error):

    """Converting column '%s' from %s to %s"""

class Illegal_Reference(MySQL_Error):

    """Reference '%s' not supported (%s)"""

class Derived_Must_Have_Alias(MySQL_Error):

    """Every derived table must have its own alias"""

class Select_Reduced(MySQL_Error):

    """Select %u was reduced during optimization"""

class Tablename_Not_Allowed_Here(MySQL_Error):

    """Table '%s' from one of the SELECTs cannot be used in %s"""

class Not_Supported_Auth_Mode(MySQL_Error):

    """Client does not support authentication protocol requested by server;
    consider upgrading MySQL client
    """

class Spatial_Cant_Have_Null(MySQL_Error):

    """All parts of a SPATIAL index must be NOT NULL"""

class Collation_Charset_Mismatch(MySQL_Error):

    """COLLATION '%s' is not valid for CHARACTER SET '%s'"""

class Slave_Was_Running(MySQL_Error):

    """Slave is already running"""

class Slave_Was_Not_Running(MySQL_Error):

    """Slave already has been stopped"""

class Too_Big_For_Uncompress(MySQL_Error):

    """Uncompressed data size too large; the maximum size is %d (probably,
    length of uncompressed data was corrupted)
    """

class Zlib_Z_Mem_Error(MySQL_Error):

    """ZLIB: Not enough memory"""

class Zlib_Z_Buf_Error(MySQL_Error):

    """ZLIB: Not enough room in the output buffer (probably, length of
    uncompressed data was corrupted)
    """

class Zlib_Z_Data_Error(MySQL_Error):

    """ZLIB: Input data corrupted"""

class Cut_Value_Group_Concat(MySQL_Error):

    """%d line(s) were cut by GROUP_CONCAT()"""

class Warn_Too_Few_Records(MySQL_Error):

    """Row %ld doesn't contain data for all columns"""

class Warn_Too_Many_Records(MySQL_Error):

    """Row %ld was truncated; it contained more data than there were input
    columns
    """

class Warn_Null_To_Notnull(MySQL_Error):

    """Column set to default value; NULL supplied to NOT NULL column '%s' at
    row %ld
    """

class Warn_Data_Out_Of_Range(MySQL_Error):

    """Out of range value adjusted for column '%s' at row %ld"""

class Warn_Data_Truncated(MySQL_Error):

    """Data truncated for column '%s' at row %ld"""

class Warn_Using_Other_Handler(MySQL_Error):

    """Using storage engine %s for table '%s'"""

class Cant_Aggregate_2Collations(MySQL_Error):

    """Illegal mix of collations (%s,%s) and (%s,%s) for operation '%s'"""

class Drop_User(MySQL_Error):

    """Cannot drop one or more of the requested users"""

class Revoke_Grants(MySQL_Error):

    """Can't revoke all privileges, grant for one or more of the requested
    users
    """

class Cant_Aggregate_3Collations(MySQL_Error):

    """Illegal mix of collations (%s,%s), (%s,%s), (%s,%s) for operation
    '%s'
    """

class Cant_Aggregate_Ncollations(MySQL_Error):

    """Illegal mix of collations for operation '%s'"""

class Variable_Is_Not_Struct(MySQL_Error):

    """Variable '%s' is not a variable component (can't be used as
    XXXX.variable_name)
    """

class Unknown_Collation(MySQL_Error):

    """Unknown collation: '%s'"""

class Slave_Ignored_Ssl_Params(MySQL_Error):

    """SSL parameters in CHANGE MASTER are ignored because this MySQL slave was
    compiled without SSL support; they can be used later if MySQL slave with
    SSL is started
    """

class Server_Is_In_Secure_Auth_Mode(MySQL_Error):

    """Server is running in --secure-auth mode, but '%s'@'%s' has a password in
    the old format; please change the password to the new format
    """

class Warn_Field_Resolved(MySQL_Error):

    """Field or reference '%s%s%s%s%s' of SELECT #%d was resolved in SELECT #%d"""

class Bad_Slave_Until_Cond(MySQL_Error):

    """Incorrect parameter or combination of parameters for START SLAVE UNTIL"""

class Missing_Skip_Slave(MySQL_Error):

    """It is recommended to use --skip-slave-start when doing step-by-step
    replication with START SLAVE UNTIL; otherwise, you will get problems if you
    get an unexpected slave's mysqld restart
    """

class Until_Cond_Ignored(MySQL_Error):

    """SQL thread is not to be started so UNTIL options are ignored"""

class Wrong_Name_For_Index(MySQL_Error):

    """Incorrect index name '%s'"""

class Wrong_Name_For_Catalog(MySQL_Error):

    """Incorrect catalog name '%s'"""

class Warn_Qc_Resize(MySQL_Error):

    """Query cache failed to set size %lu; new query cache size is %lu"""

class Bad_Ft_Column(MySQL_Error):

    """Column '%s' cannot be part of FULLTEXT index"""

class Unknown_Key_Cache(MySQL_Error):

    """Unknown key cache '%s'"""

class Warn_Hostname_Wont_Work(MySQL_Error):

    """MySQL is started in --skip-name-resolve mode; you must restart it
    without this switch for this grant to work
    """

class Unknown_Storage_Engine(MySQL_Error):

    """Unknown table engine '%s'"""

class Warn_Deprecated_Syntax(MySQL_Error):

    """'%s' is deprecated; use '%s' instead"""

class Non_Updatable_Table(MySQL_Error):

    """The target table %s of the %s is not updatable"""

class Feature_Disabled(MySQL_Error):

    """The '%s' feature is disabled; you need MySQL built with '%s' to have it
    working
    """

class Option_Prevents_Statement(MySQL_Error):

    """The MySQL server is running with the %s option so it cannot execute this
    statement
    """

class Duplicated_Value_In_Type(MySQL_Error):

    """Column '%s' has duplicated value '%s' in %s"""

class Truncated_Wrong_Value(MySQL_Error):

    """Truncated incorrect %s value: '%s'"""

class Too_Much_Auto_Timestamp_Cols(MySQL_Error):

    """Incorrect table definition; there can be only one TIMESTAMP column with
    CURRENT_TIMESTAMP in DEFAULT or ON UPDATE clause
    """

class Invalid_On_Update(MySQL_Error):

    """Invalid ON UPDATE clause for '%s' column"""

class Unsupported_Ps(MySQL_Error):

    """This command is not supported in the prepared statement protocol yet"""

class Get_Errmsg(MySQL_Error):

    """Got error %d '%s' from %s"""

class Get_Temporary_Errmsg(MySQL_Error):

    """Got temporary error %d '%s' from %s"""

class Unknown_Time_Zone(MySQL_Error):

    """Unknown or incorrect time zone: '%s'"""

class Warn_Invalid_Timestamp(MySQL_Error):

    """Invalid TIMESTAMP value in column '%s' at row %ld"""

class Invalid_Character_String(MySQL_Error):

    """Invalid %s character string: '%s'"""

class Warn_Allowed_Packet_Overflowed(MySQL_Error):

    """Result of %s() was larger than max_allowed_packet (%ld) - truncated"""

class Conflicting_Declarations(MySQL_Error):

    """Conflicting declarations: '%s%s' and '%s%s'"""

class Sp_No_Recursive_Create(MySQL_Error):

    """Can't create a %s from within another stored routine"""

class Sp_Already_Exists(MySQL_Error):

    """%s %s already exists"""

class Sp_Does_Not_Exist(MySQL_Error):

    """%s %s does not exist"""

class Sp_Drop_Failed(MySQL_Error):

    """Failed to DROP %s %s"""

class Sp_Store_Failed(MySQL_Error):

    """Failed to CREATE %s %s"""

class Sp_Lilabel_Mismatch(MySQL_Error):

    """%s with no matching label: %s"""

class Sp_Label_Redefine(MySQL_Error):

    """Redefining label %s"""

class Sp_Label_Mismatch(MySQL_Error):

    """End-label %s without match"""

class Sp_Uninit_Var(MySQL_Error):

    """Referring to uninitialized variable %s"""

class Sp_Badselect(MySQL_Error):

    """PROCEDURE %s can't return a result set in the given context"""

class Sp_Badreturn(MySQL_Error):

    """RETURN is only allowed in a FUNCTION"""

class Sp_Badstatement(MySQL_Error):

    """%s is not allowed in stored procedures"""

class Update_Log_Deprecated_Ignored(MySQL_Error):

    """The update log is deprecated and replaced by the binary log; SET
    SQL_LOG_UPDATE has been ignored
    """

class Update_Log_Deprecated_Translated(MySQL_Error):

    """The update log is deprecated and replaced by the binary log; SET
    SQL_LOG_UPDATE has been translated to SET SQL_LOG_BIN
    """

class Query_Interrupted(MySQL_Error):

    """Query execution was interrupted"""

class Sp_Wrong_No_Of_Args(MySQL_Error):

    """Incorrect number of arguments for %s %s; expected %u, got %u"""

class Sp_Cond_Mismatch(MySQL_Error):

    """Undefined CONDITION: %s"""

class Sp_Noreturn(MySQL_Error):

    """No RETURN found in FUNCTION %s"""

class Sp_Noreturnend(MySQL_Error):

    """FUNCTION %s ended without RETURN"""

class Sp_Bad_Cursor_Query(MySQL_Error):

    """Cursor statement must be a SELECT"""

class Sp_Bad_Cursor_Select(MySQL_Error):

    """Cursor SELECT must not have INTO"""

class Sp_Cursor_Mismatch(MySQL_Error):

    """Undefined CURSOR: %s"""

class Sp_Cursor_Already_Open(MySQL_Error):

    """Cursor is already open"""

class Sp_Cursor_Not_Open(MySQL_Error):

    """Cursor is not open"""

class Sp_Undeclared_Var(MySQL_Error):

    """Undeclared variable: %s"""

class Sp_Wrong_No_Of_Fetch_Args(MySQL_Error):

    """Incorrect number of FETCH variables"""

class Sp_Fetch_No_Data(MySQL_Error):

    """No data to FETCH"""

class Sp_Dup_Param(MySQL_Error):

    """Duplicate parameter: %s"""

class Sp_Dup_Var(MySQL_Error):

    """Duplicate variable: %s"""

class Sp_Dup_Cond(MySQL_Error):

    """Duplicate condition: %s"""

class Sp_Dup_Curs(MySQL_Error):

    """Duplicate cursor: %s"""

class Sp_Cant_Alter(MySQL_Error):

    """Failed to ALTER %s %s"""

class Sp_Subselect_Nyi(MySQL_Error):

    """Subselect value not supported"""

class Stmt_Not_Allowed_In_Sf_Or_Trg(MySQL_Error):

    """%s is not allowed in stored function or trigger"""

class Sp_Varcond_After_Curshndlr(MySQL_Error):

    """Variable or condition declaration after cursor or handler declaration"""

class Sp_Cursor_After_Handler(MySQL_Error):

    """Cursor declaration after handler declaration"""

class Sp_Case_Not_Found(MySQL_Error):

    """Case not found for CASE statement"""

class Fparser_Too_Big_File(MySQL_Error):

    """Configuration file '%s' is too big"""

class Fparser_Bad_Header(MySQL_Error):

    """Malformed file type header in file '%s'"""

class Fparser_Eof_In_Comment(MySQL_Error):

    """Unexpected end of file while parsing comment '%s'"""

class Fparser_Error_In_Parameter(MySQL_Error):

    """Error while parsing parameter '%s' (line: '%s')"""

class Fparser_Eof_In_Unknown_Parameter(MySQL_Error):

    """Unexpected end of file while skipping unknown parameter '%s'"""

class View_No_Explain(MySQL_Error):

    """EXPLAIN/SHOW can not be issued; lacking privileges for underlying
    table
    """

class Frm_Unknown_Type(MySQL_Error):

    """File '%s' has unknown type '%s' in its header"""

class Wrong_Object(MySQL_Error):

    """'%s.%s' is not %s"""

class Nonupdateable_Column(MySQL_Error):

    """Column '%s' is not updatable"""

class View_Select_Derived(MySQL_Error):

    """View's SELECT contains a subquery in the FROM clause"""

class View_Select_Clause(MySQL_Error):

    """View's SELECT contains a '%s' clause"""

class View_Select_Variable(MySQL_Error):

    """View's SELECT contains a variable or parameter"""

class View_Select_Tmptable(MySQL_Error):

    """View's SELECT refers to a temporary table '%s'"""

class View_Wrong_List(MySQL_Error):

    """View's SELECT and view's field list have different column counts"""

class Warn_View_Merge(MySQL_Error):

    """View merge algorithm can't be used here for now (assumed undefined
    algorithm)
    """

class Warn_View_Without_Key(MySQL_Error):

    """View being updated does not have complete key of underlying table in
    it
    """

class View_Invalid(MySQL_Error):

    """View '%s.%s' references invalid table(s) or column(s) or function(s) or
    definer/invoker of view lack rights to use them
    """

class Sp_No_Drop_Sp(MySQL_Error):

    """Can't drop or alter a %s from within another stored routine"""

class Sp_Goto_In_Hndlr(MySQL_Error):

    """GOTO is not allowed in a stored procedure handler"""

class Trg_Already_Exists(MySQL_Error):

    """Trigger already exists"""

class Trg_Does_Not_Exist(MySQL_Error):

    """Trigger does not exist"""

class Trg_On_View_Or_Temp_Table(MySQL_Error):

    """Trigger's '%s' is view or temporary table"""

class Trg_Cant_Change_Row(MySQL_Error):

    """Updating of %s row is not allowed in %strigger"""

class Trg_No_Such_Row_In_Trg(MySQL_Error):

    """There is no %s row in %s trigger"""

class No_Default_For_Field(MySQL_Error):

    """Field '%s' doesn't have a default value"""

class Division_By_Zero(MySQL_Error):

    """Division by 0"""

class Truncated_Wrong_Value_For_Field(MySQL_Error):

    """Incorrect %s value: '%s' for column '%s' at row %ld"""

class Illegal_Value_For_Type(MySQL_Error):

    """Illegal %s '%s' value found during parsing"""

class View_Nonupd_Check(MySQL_Error):

    """CHECK OPTION on non-updatable view '%s.%s'"""

class View_Check_Failed(MySQL_Error):

    """CHECK OPTION failed '%s.%s'"""

class Procaccess_Denied_Error(MySQL_Error):

    """%s command denied to user '%s'@'%s' for routine '%s'"""

class Relay_Log_Fail(MySQL_Error):

    """Failed purging old relay logs: %s"""

class Passwd_Length(MySQL_Error):

    """Password hash should be a %d-digit hexadecimal number"""

class Unknown_Target_Binlog(MySQL_Error):

    """Target log not found in binlog index"""

class Io_Err_Log_Index_Read(MySQL_Error):

    """I/O error reading log index file"""

class Binlog_Purge_Prohibited(MySQL_Error):

    """Server configuration does not permit binlog purge"""

class Fseek_Fail(MySQL_Error):

    """Failed on fseek()"""

class Binlog_Purge_Fatal_Err(MySQL_Error):

    """Fatal error during log purge"""

class Log_In_Use(MySQL_Error):

    """A purgeable log is in use, will not purge"""

class Log_Purge_Unknown_Err(MySQL_Error):

    """Unknown error during log purge"""

class Relay_Log_Init(MySQL_Error):

    """Failed initializing relay log position: %s"""

class No_Binary_Logging(MySQL_Error):

    """You are not using binary logging"""

class Reserved_Syntax(MySQL_Error):

    """The '%s' syntax is reserved for purposes internal to the MySQL server"""

class Wsas_Failed(MySQL_Error):

    """WSAStartup Failed"""

class Diff_Groups_Proc(MySQL_Error):

    """Can't handle procedures with differents groups yet"""

class No_Group_For_Proc(MySQL_Error):

    """Select must have a group with this procedure"""

class Order_With_Proc(MySQL_Error):

    """Can't use ORDER clause with this procedure"""

class Logging_Prohibit_Changing_Of(MySQL_Error):

    """Binary logging and replication forbid changing the global server %s"""

class No_File_Mapping(MySQL_Error):

    """Can't map file: %s, errno: %d"""

class Wrong_Magic(MySQL_Error):

    """Wrong magic in %s"""

class Ps_Many_Param(MySQL_Error):

    """Prepared statement contains too many placeholders"""

class Key_Part_0(MySQL_Error):

    """Key part '%s' length cannot be 0"""

class View_Checksum(MySQL_Error):

    """View text checksum failed"""

class View_Multiupdate(MySQL_Error):

    """Can not modify more than one base table through a join view '%s.%s'"""

class View_No_Insert_Field_List(MySQL_Error):

    """Can not insert into join view '%s.%s' without fields list"""

class View_Delete_Merge_View(MySQL_Error):

    """Can not delete from join view '%s.%s'"""

class Cannot_User(MySQL_Error):

    """Operation %s failed for %s"""

class Xaer_Nota(MySQL_Error):

    """XAER_NOTA: Unknown XID"""

class Xaer_Inval(MySQL_Error):

    """XAER_INVAL: Invalid arguments (or unsupported command)"""

class Xaer_Rmfail(MySQL_Error):

    """XAER_RMFAIL: The command cannot be executed when global transaction is
    in the %s state
    """

class Xaer_Outside(MySQL_Error):

    """XAER_OUTSIDE: Some work is done outside global transaction"""

class Xaer_Rmerr(MySQL_Error):

    """XAER_RMERR: Fatal error occurred in the transaction branch - check your
    data for consistency
    """

class Xa_Rbrollback(MySQL_Error):

    """XA_RBROLLBACK: Transaction branch was rolled back"""

class Nonexisting_Proc_Grant(MySQL_Error):

    """There is no such grant defined for user '%s' on host '%s' on routine
    '%s'
    """

class Proc_Auto_Grant_Fail(MySQL_Error):

    """Failed to grant EXECUTE and ALTER ROUTINE privileges"""

class Proc_Auto_Revoke_Fail(MySQL_Error):

    """Failed to revoke all privileges to dropped routine"""

class Data_Too_Long(MySQL_Error):

    """Data too long for column '%s' at row %ld"""

class Sp_Bad_Sqlstate(MySQL_Error):

    """Bad SQLSTATE: '%s'"""

class Startup(MySQL_Error):

    """%s: ready for connections. Version: '%s' socket: '%s' port: %d %s"""

class Load_From_Fixed_Size_Rows_To_Var(MySQL_Error):

    """Can't load value from file with fixed size rows to variable"""

class Cant_Create_User_With_Grant(MySQL_Error):

    """You are not allowed to create a user with GRANT"""

class Wrong_Value_For_Type(MySQL_Error):

    """Incorrect %s value: '%s' for function %s"""

class Table_Def_Changed(MySQL_Error):

    """Table definition has changed, please retry transaction"""

class Sp_Dup_Handler(MySQL_Error):

    """Duplicate handler declared in the same block"""

class Sp_Not_Var_Arg(MySQL_Error):

    """OUT or INOUT argument %d for routine %s is not a variable"""

class Sp_No_Retset(MySQL_Error):

    """Not allowed to return a result set from a %s"""

class Cant_Create_Geometry_Object(MySQL_Error):

    """Cannot get geometry object from data you send to the GEOMETRY field"""

class Failed_Routine_Break_Binlog(MySQL_Error):

    """A routine failed and has neither NO SQL nor READS SQL DATA in its
    declaration and binary logging is enabled; if non-transactional tables were
    updated, the binary log will miss their changes
    """

class Binlog_Unsafe_Routine(MySQL_Error):

    """This function has none of DETERMINISTIC, NO SQL, or READS SQL DATA in
    its declaration and binary logging is enabled (you *might* want to use the
    less safe log_bin_trust_function_creators variable)
    """

class Binlog_Create_Routine_Need_Super(MySQL_Error):

    """You do not have the SUPER privilege and binary logging is enabled (you
    *might* want to use the less safe log_bin_trust_function_creators
    variable)
    """

class Exec_Stmt_With_Open_Cursor(MySQL_Error):

    """You can't execute a prepared statement which has an open cursor
    associated with it. Reset the statement to re-execute it.
    """

class Stmt_Has_No_Open_Cursor(MySQL_Error):

    """The statement (%lu) has no open cursor."""

class Commit_Not_Allowed_In_Sf_Or_Trg(MySQL_Error):

    """Explicit or implicit commit is not allowed in stored function or
    trigger.
    """

class No_Default_For_View_Field(MySQL_Error):

    """Field of view '%s.%s' underlying table doesn't have a default value"""

class Sp_No_Recursion(MySQL_Error):

    """Recursive stored routines are not allowed."""

class Too_Big_Scale(MySQL_Error):

    """Too big scale %d specified for column '%s'. Maximum is %d."""

class Too_Big_Precision(MySQL_Error):

    """Too big precision %d specified for column '%s'. Maximum is %d."""

class M_Bigger_Than_D(MySQL_Error):

    """For float(M,D), double(M,D) or decimal(M,D), M must be >= D (column
    '%s').
    """

class Wrong_Lock_Of_System_Table(MySQL_Error):

    """You can't combine write-locking of system '%s.%s' table with other
    tables
    """

class Connect_To_Foreign_Data_Source(MySQL_Error):

    """Unable to connect to foreign data source - database '%s'!"""

class Query_On_Foreign_Data_Source(MySQL_Error):

    """There was a problem processing the query on the foreign data source.
    Data source error: '%s'
    """

class Foreign_Data_Source_Doesnt_Exist(MySQL_Error):

    """The foreign data source you are trying to reference does not exist. Data
    source error : '%s'
    """

class Foreign_Data_String_Invalid_Cant_Create(MySQL_Error):

    """Can't create federated table. The data source connection string '%s' is
    not in the correct format
    """

class Foreign_Data_String_Invalid(MySQL_Error):

    """The data source connection string '%s' is not in the correct format"""

class Cant_Create_Federated_Table(MySQL_Error):

    """Can't create federated table. Foreign data src error : '%s'"""

class Trg_In_Wrong_Schema(MySQL_Error):

    """Trigger in wrong schema"""

class Stack_Overrun_Need_More(MySQL_Error):

    """Thread stack overrun: %ld bytes used of a %ld byte stack, and %ld bytes
    needed. Use 'mysqld -O thread_stack=#' to specify a bigger stack.
    """

class Too_Long_Body(MySQL_Error):

    """Routine body for '%s' is too long"""

class Warn_Cant_Drop_Default_Keycache(MySQL_Error):

    """Cannot drop default keycache"""

class Too_Big_Displaywidth(MySQL_Error):

    """Display width out of range for column '%s' (max = %d)"""

class Xaer_Dupid(MySQL_Error):

    """XAER_DUPID: The XID already exists"""

class Datetime_Function_Overflow(MySQL_Error):

    """Datetime function: %s field overflow"""

class Cant_Update_Used_Table_In_Sf_Or_Trg(MySQL_Error):

    """Can't update table '%s' in stored function/trigger because it is already
    used by statement which invoked this stored function/trigger.
    """

class View_Prevent_Update(MySQL_Error):

    """The definition of table '%s' prevents operation %s on table '%s'."""

class Ps_No_Recursion(MySQL_Error):

    """The prepared statement contains a stored routine call that refers to
    that same statement. It's not allowed to execute a prepared statement in
    such a recursive manner
    """

class Sp_Cant_Set_Autocommit(MySQL_Error):

    """Not allowed to set autocommit from a stored function or trigger"""

class Malformed_Definer(MySQL_Error):

    """Definer is not fully qualified"""

class No_View_User(MySQL_Error):

    """View definer is not fully qualified

    (No longer available as of 5.0.17.)
    """

class View_Frm_No_User(MySQL_Error):

    """View %s.%s has not definer information (old table format). Current user
    is used as definer. Please recreate view!
    """

class View_Other_User(MySQL_Error):

    """You need the SUPER privilege for creation view with %s@%s definer"""

class No_Such_User(MySQL_Error):

    """There is no '%s'@'%s' registered"""

class Forbid_Schema_Change(MySQL_Error):

    """Changing schema from '%s' to '%s' is not allowed."""

class Row_Is_Referenced_2(MySQL_Error):

    """Cannot delete or update a parent row: a foreign key constraint fails
    (%s)
    """

class No_Referenced_Row_2(MySQL_Error):

    """Cannot add or update a child row: a foreign key constraint fails (%s)"""

class Sp_Bad_Var_Shadow(MySQL_Error):

    """Variable '%s' must be quoted with ``...``, or renamed"""

class Trg_No_Definer(MySQL_Error):

    """No definer attribute for trigger '%s'.'%s'. The trigger will be
    activated under the authorization of the invoker, which may have
    insufficient privileges. Please recreate the trigger.
    """

###############################################################################
# 5.0.17
###############################################################################

class Sp_Recursion_Limit(MySQL_Error):

    """Recursive limit %d (as set by the max_sp_recursion_depth variable) was
    exceeded for routine %.64s

    (New in 5.0.17.)
    """

class Malformed_Definer(MySQL_Error):

    """Definer is not fully qualified

    (New in 5.0.17.)
    """

class Old_File_Format(MySQL_Error):

    """'%-.64s' has an old format, you should re-create the '%s' object(s).
    (New in 5.0.17.)
    """

class Trg_No_Definer(MySQL_Error):

    """No definer attribute for trigger '%-.64s'.'%-.64s'. The trigger will be
    activated under the auth orization of the invoker, which may have
    insufficient privileges. Please recreate the trigger.

    (New in 5.0.17.)
    """
class Sp_Proc_Table_Corrupt(MySQL_Error):

    """Failed to load routine %s. The table mysql.proc is missing, corrupt, or
    contains bad data (internal code %d)

    (New in 5.0.17.)
    """

###############################################################################
# 5.0.19
###############################################################################

class Table_Needs_Upgrade(MySQL_Error):

    """Table upgrade required. Please do "REPAIR TABLE ``%-.32s``" to fix it!

    (New in 5.0.19.)
    """

class Sp_No_Aggregate(MySQL_Error):

    """AGGREGATE is not supported for stored functions

    (New in 5.0.19.)
    """

class Sp_Wrong_Name(MySQL_Error):

    """Incorrect routine name '%-.64s'

    (New in 5.0.19.)
    """

###############################################################################
# 5.0.21
###############################################################################

class Max_Prepared_Stmt_Count_Reached(MySQL_Error):

    """Can't create more than max_prepared_stmt_count statements (current
    value: %lu)

    (New in 5.0.21.)
    """

class View_Recursive(MySQL_Error):

    """``%-.64s``.``%-.64s`` contains view recursion.

    (New in 5.0.21.)
    """

###############################################################################
# 5.0.23
###############################################################################

class Non_Grouping_Field_Used(MySQL_Error):

    """non-grouping field '%-.64s' is used in %-.64s clause

    (New in 5.0.23.)
    """

class Table_Cant_Handle_Spkeys(MySQL_Error):

    """The used table type doesn't support SPATIAL indexes

    (New in 5.0.23.)
    """

class No_Triggers_On_System_Schema(MySQL_Error):

    """Triggers can not be created on system tables

    (New in 5.0.23.)
    """

###############################################################################
# 5.0.24a
###############################################################################

class Username(MySQL_Error):

    """user name?

    (New in 5.0.24a.)
    """

class Hostname(MySQL_Error):

    """host name?

    (New in 5.0.24a.)
    """

class Wrong_String_Length(MySQL_Error):

    """String '%-.70s' is too long for %s (should be no longer than %d)

    (New in 5.0.24a.)
    """

###############################################################################
# 5.0.25
###############################################################################

class Removed_Spaces(MySQL_Error):

    """Leading spaces are removed from name '%s'

    (New in 5.0.25.)
    """

class Autoinc_Read_Failed(MySQL_Error):

    """Failed to read auto-increment value from storage engine

    (New in 5.0.25.)
    """

class Non_Insertable_Table(MySQL_Error):

    """The target table %-.100s of the %s is not insertable-into

    (New in 5.0.25.)
    """
