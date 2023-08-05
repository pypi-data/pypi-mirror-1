# $Header: /home/cvs2/mysql/mysql/extern_mysql.pxd,v 1.5 2006/11/13 04:00:00 ehuss Exp $

# Force my_global.h to be included so that ulong is defined
# Recent change in 5.0.24a causes some defines such as CLIENT_MULTI_STATEMENTS
# to depend on this.  Filed bug #22227.  (Fixed in 5.0.26.)
%if MYSQL_VERSION == 5002491:
    cdef extern from "my_global.h":
        pass

cdef extern from "mysql.h":

    ###########################################################################
    # Enum definitions.                                                       #
    ###########################################################################

    cdef enum enum_cursor_type:
        CURSOR_TYPE_NO_CURSOR
        CURSOR_TYPE_READ_ONLY
        CURSOR_TYPE_FOR_UPDATE
        CURSOR_TYPE_SCROLLABLE

    cdef enum enum_field_types:
        MYSQL_TYPE_DECIMAL
        MYSQL_TYPE_TINY
        MYSQL_TYPE_SHORT
        MYSQL_TYPE_LONG
        MYSQL_TYPE_FLOAT
        MYSQL_TYPE_DOUBLE
        MYSQL_TYPE_NULL
        MYSQL_TYPE_TIMESTAMP
        MYSQL_TYPE_LONGLONG
        MYSQL_TYPE_INT24
        MYSQL_TYPE_DATE
        MYSQL_TYPE_TIME
        MYSQL_TYPE_DATETIME
        MYSQL_TYPE_YEAR
        MYSQL_TYPE_NEWDATE
        MYSQL_TYPE_VARCHAR
        MYSQL_TYPE_BIT
        MYSQL_TYPE_NEWDECIMAL
        MYSQL_TYPE_ENUM
        MYSQL_TYPE_SET
        MYSQL_TYPE_TINY_BLOB
        MYSQL_TYPE_MEDIUM_BLOB
        MYSQL_TYPE_LONG_BLOB
        MYSQL_TYPE_BLOB
        MYSQL_TYPE_VAR_STRING
        MYSQL_TYPE_STRING
        MYSQL_TYPE_GEOMETRY

    cdef enum enum_mysql_set_option:
        MYSQL_OPTION_MULTI_STATEMENTS_ON
        MYSQL_OPTION_MULTI_STATEMENTS_OFF

    cdef enum enum_stmt_attr_type:
        STMT_ATTR_UPDATE_MAX_LENGTH
        STMT_ATTR_CURSOR_TYPE
        STMT_ATTR_PREFETCH_ROWS

    # Dummy enum declaration for integers.
    cdef enum mysql_client_flags:
        CLIENT_FOUND_ROWS
        CLIENT_COMPRESS
        CLIENT_IGNORE_SPACE
        CLIENT_INTERACTIVE
        CLIENT_LOCAL_FILES
        CLIENT_MULTI_STATEMENTS
        CLIENT_MULTI_RESULTS
        CLIENT_NO_SCHEMA
        CLIENT_ODBC
        CLIENT_SSL

    cdef enum mysql_enum_shutdown_level:
        SHUTDOWN_DEFAULT

    # Dummy enum declaration for #define.
    cdef enum mysql_flags:
        NOT_NULL_FLAG
        PRI_KEY_FLAG
        UNIQUE_KEY_FLAG
        MULTIPLE_KEY_FLAG
        BLOB_FLAG
        UNSIGNED_FLAG
        ZEROFILL_FLAG
        BINARY_FLAG
        ENUM_FLAG
        AUTO_INCREMENT_FLAG
        TIMESTAMP_FLAG
        SET_FLAG
        NO_DEFAULT_VALUE_FLAG
        NUM_FLAG
        PART_KEY_FLAG
        GROUP_FLAG
        UNIQUE_FLAG
        BINCMP_FLAG

    cdef enum mysql_option:
        MYSQL_OPT_CONNECT_TIMEOUT
        MYSQL_OPT_COMPRESS
        MYSQL_OPT_NAMED_PIPE
        MYSQL_INIT_COMMAND
        MYSQL_READ_DEFAULT_FILE
        MYSQL_READ_DEFAULT_GROUP
        MYSQL_SET_CHARSET_DIR
        MYSQL_SET_CHARSET_NAME
        MYSQL_OPT_LOCAL_INFILE
        MYSQL_OPT_PROTOCOL
        MYSQL_SHARED_MEMORY_BASE_NAME
        MYSQL_OPT_READ_TIMEOUT
        MYSQL_OPT_WRITE_TIMEOUT
        MYSQL_OPT_USE_RESULT
        MYSQL_OPT_USE_REMOTE_CONNECTION
        MYSQL_OPT_USE_EMBEDDED_CONNECTION
        MYSQL_OPT_GUESS_CONNECTION
        MYSQL_SET_CLIENT_IP
        MYSQL_SECURE_AUTH
        MYSQL_REPORT_DATA_TRUNCATION
        MYSQL_OPT_RECONNECT

    cdef enum mysql_protocol_type:
        MYSQL_PROTOCOL_DEFAULT
        MYSQL_PROTOCOL_TCP
        MYSQL_PROTOCOL_SOCKET
        MYSQL_PROTOCOL_PIPE
        MYSQL_PROTOCOL_MEMORY

    # Dummy enum declaration for integers.
    cdef enum mysql_status_return_codes:
        MYSQL_NO_DATA
        MYSQL_DATA_TRUNCATED

    ###########################################################################
    # Structure and type definitions.                                         #
    ###########################################################################

    ctypedef char my_bool

    ctypedef unsigned long long my_ulonglong

    ctypedef struct MYSQL:
        pass

    ctypedef struct MYSQL_BIND:
        unsigned long       *length
        my_bool             *is_null
        void                *buffer
        my_bool             *error
        enum_field_types    buffer_type
        unsigned long       buffer_length
        my_bool             is_unsigned

    ctypedef struct MY_CHARSET_INFO:
        unsigned int number
        unsigned int state
        char * csname
        char * name
        char * comment
        char * dir
        unsigned int mbminlen
        unsigned int mbmaxlen

    ctypedef struct MYSQL_FIELD:
        char * name
        char * org_name
        char * table
        char * org_table
        char * db
        char * catalog
        char * default "def"
        unsigned long length
        unsigned long max_length
        unsigned int name_length
        unsigned int org_name_length
        unsigned int table_length
        unsigned int org_table_length
        unsigned int db_length
        unsigned int catalog_length
        unsigned int def_length
        unsigned int flags
        unsigned int decimals
        unsigned int charsetnr
        enum_field_types type

    ctypedef unsigned int MYSQL_FIELD_OFFSET

    ctypedef struct MYSQL_RES:
        pass

    ctypedef char **MYSQL_ROW

    ctypedef struct MYSQL_ROWS:
        pass

    ctypedef MYSQL_ROWS *MYSQL_ROW_OFFSET

    ctypedef struct MYSQL_STMT:
        pass

    ctypedef struct MYSQL_TIME:
        unsigned int year
        unsigned int month
        unsigned int day
        unsigned int hour
        unsigned int minute
        unsigned int second
        unsigned long second_part
        my_bool neg

    ###########################################################################
    # Function definitions.                                                   #
    ###########################################################################

    int             IS_BLOB(unsigned int flags)
    int             IS_NOT_NULL(unsigned int flags)
    int             IS_NUM(enum_field_types type)
    int             IS_PRI_KEY(unsigned int flags)
    my_ulonglong    mysql_affected_rows(MYSQL *mysql)
    my_bool         mysql_autocommit(MYSQL * mysql, my_bool auto_mode)
    my_bool         mysql_change_user(MYSQL *mysql, char *user, char *passwd, char *db)
    char *          mysql_character_set_name(MYSQL *mysql)
    void            mysql_close(MYSQL *sock)
    my_bool         mysql_commit(MYSQL * mysql)
    void            mysql_data_seek(MYSQL_RES *result, my_ulonglong offset)
    void            mysql_debug(char *debug)
    int             mysql_dump_debug_info(MYSQL *mysql)
    my_bool         mysql_eof(MYSQL_RES *res)
    unsigned int    mysql_errno(MYSQL *mysql)
    char *          mysql_error(MYSQL *mysql)
    unsigned long   mysql_escape_string(char *to,char *, unsigned long from_length)
    MYSQL_FIELD *   mysql_fetch_field(MYSQL_RES *result)
    MYSQL_FIELD *   mysql_fetch_field_direct(MYSQL_RES *res, unsigned int fieldnr)
    MYSQL_FIELD *   mysql_fetch_fields(MYSQL_RES *res)
    unsigned long * mysql_fetch_lengths(MYSQL_RES *result)
    MYSQL_ROW       mysql_fetch_row(MYSQL_RES *result)
    unsigned int    mysql_field_count(MYSQL *mysql)
    MYSQL_FIELD_OFFSET mysql_field_seek(MYSQL_RES *result, MYSQL_FIELD_OFFSET offset)
    MYSQL_FIELD_OFFSET mysql_field_tell(MYSQL_RES *res)
    void            mysql_free_result(MYSQL_RES *result)
    void            mysql_get_character_set_info(MYSQL *mysql, MY_CHARSET_INFO *charset)
    char *          mysql_get_client_info()
    unsigned long   mysql_get_client_version()
    char *          mysql_get_host_info(MYSQL *mysql)
    unsigned int    mysql_get_proto_info(MYSQL *mysql)
    char *          mysql_get_server_info(MYSQL *mysql)
    unsigned long   mysql_get_server_version(MYSQL *mysql)
    unsigned long   mysql_hex_string(char *to,char *, unsigned long from_length)
    char *          mysql_info(MYSQL *mysql)
    MYSQL *         mysql_init(MYSQL *mysql)
    my_ulonglong    mysql_insert_id(MYSQL *mysql)
    int             mysql_kill(MYSQL *mysql,unsigned long pid)
    int             mysql_library_end()
    int             mysql_library_init(int argc, char **argv, char **groups)
    MYSQL_RES *     mysql_list_dbs(MYSQL *mysql,char *wild)
    MYSQL_RES *     mysql_list_fields(MYSQL *mysql, char *table, char *wild)
    MYSQL_RES *     mysql_list_processes(MYSQL *mysql)
    MYSQL_RES *     mysql_list_tables(MYSQL *mysql,char *wild)
    my_bool         mysql_more_results(MYSQL *mysql)
    int             mysql_next_result(MYSQL *mysql)
    unsigned int    mysql_num_fields(MYSQL_RES *res)
    my_ulonglong    mysql_num_rows(MYSQL_RES *res)
    int             mysql_options(MYSQL *mysql,
                                  mysql_option option,
                                  char *arg)
    int             mysql_ping(MYSQL *mysql)
    MYSQL *         mysql_real_connect(MYSQL *mysql,
                                       char *host,
                                       char *user,
                                       char *passwd,
                                       char *db,
                                       unsigned int port,
                                       char *unix_socket,
                                       unsigned long clientflag)
    unsigned long   mysql_real_escape_string(MYSQL *mysql, char *to,char *, unsigned long length)
    int             mysql_real_query(MYSQL *mysql,
                                     char *q,
                                     unsigned long length)
    int             mysql_refresh(MYSQL *mysql, unsigned int refresh_options)
    my_bool         mysql_rollback(MYSQL * mysql)
    MYSQL_ROW_OFFSET mysql_row_seek(MYSQL_RES *result, MYSQL_ROW_OFFSET offset)
    MYSQL_ROW_OFFSET mysql_row_tell(MYSQL_RES *res)
    int             mysql_select_db(MYSQL *mysql, char *db)
    void            mysql_server_end()
    int             mysql_server_init(int argc, char **argv, char **groups)
    int             mysql_set_character_set(MYSQL *mysql, char *csname)
    int             mysql_set_server_option(MYSQL *mysql, enum_mysql_set_option option)
    int             mysql_shutdown(MYSQL *mysql, mysql_enum_shutdown_level shutdown_level)
    char *          mysql_sqlstate(MYSQL *mysql)
    my_bool         mysql_ssl_set(MYSQL *mysql, char *key, char *cert, char *ca, char *capath, char *cipher)
    char *          mysql_stat(MYSQL *mysql)
    my_ulonglong    mysql_stmt_affected_rows(MYSQL_STMT *stmt)
    my_bool         mysql_stmt_attr_get(MYSQL_STMT *stmt,
                                        enum_stmt_attr_type attr_type,
                                        void *attr)
    my_bool         mysql_stmt_attr_set(MYSQL_STMT *stmt,
                                        enum_stmt_attr_type attr_type,
                                        void *attr)
    my_bool         mysql_stmt_bind_param(MYSQL_STMT * stmt, MYSQL_BIND * bnd)
    my_bool         mysql_stmt_bind_result(MYSQL_STMT * stmt, MYSQL_BIND * bnd)
    my_bool         mysql_stmt_close(MYSQL_STMT * stmt)
    void            mysql_stmt_data_seek(MYSQL_STMT *stmt, my_ulonglong offset)
    unsigned int    mysql_stmt_errno(MYSQL_STMT * stmt)
    char *          mysql_stmt_error(MYSQL_STMT * stmt)
    int             mysql_stmt_execute(MYSQL_STMT *stmt)
    int             mysql_stmt_fetch(MYSQL_STMT *stmt)
    int             mysql_stmt_fetch_column(MYSQL_STMT *stmt,
                                            MYSQL_BIND *bind,
                                            unsigned int column,
                                            unsigned long offset)
    unsigned int    mysql_stmt_field_count(MYSQL_STMT *stmt)
    my_bool         mysql_stmt_free_result(MYSQL_STMT *stmt)
    MYSQL_STMT *    mysql_stmt_init(MYSQL *mysql)
    my_ulonglong    mysql_stmt_insert_id(MYSQL_STMT *stmt)
    my_ulonglong    mysql_stmt_num_rows(MYSQL_STMT *stmt)
    unsigned long   mysql_stmt_param_count(MYSQL_STMT * stmt)
    MYSQL_RES *     mysql_stmt_param_metadata(MYSQL_STMT *stmt)
    int             mysql_stmt_prepare(MYSQL_STMT *stmt,
                                       char *query,
                                       unsigned long length)
    my_bool         mysql_stmt_reset(MYSQL_STMT * stmt)
    MYSQL_RES *     mysql_stmt_result_metadata(MYSQL_STMT *stmt)
    MYSQL_ROW_OFFSET mysql_stmt_row_seek(MYSQL_STMT *stmt,
                                         MYSQL_ROW_OFFSET offset)
    MYSQL_ROW_OFFSET mysql_stmt_row_tell(MYSQL_STMT *stmt)
    my_bool         mysql_stmt_send_long_data(MYSQL_STMT *stmt,
                                              unsigned int param_number,
                                              char *data,
                                              unsigned long length)
    char *          mysql_stmt_sqlstate(MYSQL_STMT * stmt)
    int             mysql_stmt_store_result(MYSQL_STMT *stmt)
    MYSQL_RES *     mysql_store_result(MYSQL *mysql)
    void            mysql_thread_end()
    unsigned long   mysql_thread_id(MYSQL *mysql)
    my_bool         mysql_thread_init()
    unsigned int    mysql_thread_safe()
    MYSQL_RES *     mysql_use_result(MYSQL *mysql)
    unsigned int    mysql_warning_count(MYSQL *mysql)
