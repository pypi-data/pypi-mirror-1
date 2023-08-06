cdef class Connection:
    """Connection([host, user, passwd,] db=None, port=0, unix_socket=None, 
        compress=False, found_rows=True, use_unicode=True, charset='utf8', 
        autoping=False, default_cursor=None, raise_on_warnings=True)

    Connect to the MySQL database. The first three parameters may be passed by 
    position, but the rest may only be passed by keyword. All options except 
    'use_unicode', 'charset', 'autoping', 'default_cursor', and 
    'raise_on_warnings' correspond with parameters or flags to the 
    mysql_real_connect function. 
    
    If 'use_unicode' is true, oursql will attempt to return unicode wherever 
    feasible. If 'charset' is not None, oursql will set the connection charset 
    to the value provided. 'charset' defaults to using utf-8. If 'autoping' is 
    true, oursql will run the 'ping' method before executing queries or 
    fetching results to attempt to prevent connection timeout errors. 
    'default_cursor', if provided, will be used as the default cursor class 
    when calling the 'cursor' method. If 'raise_on_warnings' is true, oursql
    will raise a CollatedWarningsError exception if there were any warnings
    produced by running a query.
    
    Connections' cursors can also be used as context managers.
    
        with some_connection.cursor() as cursor:
            do_something_with(cursor)
    
    Is equivalent to:
    
        cursor = some_connection.cursor()
        try:
            do_something_with(cursor)
        except:
            some_connection.rollback()
            raise
        else:
            some_connection.commit()
        finally:
            cursor.close()
    
    """
    
    cdef object __weakref__
    cdef MYSQL *conn
    cdef object _charset
    cdef readonly int use_unicode, autoping, raise_on_warnings
    cdef public object default_cursor
    
    def __cinit__(self, char *host=NULL, char *user=NULL, char *passwd=NULL, *,
            char *db=NULL, unsigned int port=0, char *unix_socket=NULL, 
            bint compress=False, bint found_rows=True, bint use_unicode=True, 
            charset='utf8', bint autoping=False, default_cursor=None, 
            bint raise_on_warnings=True,
            bint multi_results=True, bint multi_statements=True):
        cdef unsigned long flags = 0
        self.conn = mysql_init(NULL)
        if not self.conn:
            raise MemoryError('alloc of conn object failed')
        if compress:
            flags |= CLIENT_COMPRESS
        if found_rows:
            flags |= CLIENT_FOUND_ROWS
        # I'll come back to this later. Dealing with multiple result sets is
        # such a pain.
        #if multi_results:
        #    flags |= CLIENT_MULTI_RESULTS
        #if multi_statements:
        #    flags |= CLIENT_MULTI_STATEMENTS
        if not mysql_real_connect(self.conn, host, user, passwd, db, port, 
                unix_socket, flags):
            self._raise_error()
        self.use_unicode = use_unicode
        if charset is not None:
            self.charset = charset
        self.autoping = autoping
        if default_cursor is None:
            default_cursor = Cursor
        self.default_cursor = default_cursor
        self.raise_on_warnings = raise_on_warnings
    
    def close(self):
        """close()
        
        Close the connection. The connection object and all associated cursors
        will become unusable.
        """
        if self.conn:
            self.rollback()
            mysql_close(self.conn)
            self.conn = NULL
    
    def __dealloc__(self):
        if self.conn:
            mysql_close(self.conn)
            self.conn = NULL
    
    cdef int _raise_error(self) except -1:
        # _raise_error can only be called internally, so we shouldn't need to
        # check for if the connection is closed.
        cdef int err = mysql_errno(self.conn)
        raise _exception_from_errno(err)(mysql_error(self.conn), err)
    
    cdef int _check_closed(self) except -1:
        if not self.conn:
            raise ProgrammingError('connection closed')
    
    def ping(self):
        """ping()
        
        Make sure that the database connection is still open. If not, silently
        reconnect.
        """
        self._check_closed()
        if mysql_ping(self.conn):
            self._raise_error()
    
    def commit(self):
        """commit()
        
        Commit the current transaction.
        """
        self._check_closed()
        if mysql_commit(self.conn):
            self._raise_error()
    
    def rollback(self):
        """rollback()
        
        Roll back the current transaction.
        """
        self._check_closed()
        if mysql_rollback(self.conn):
            self._raise_error()
    
    property charset:
        """charset -> str
        
        Get or set the connection's current encoding. If use_unicode is 
        enabled, this is the encoding that will be used to decode incoming
        strings.
        """
        def __get__(self):
            self._charset = PyString_FromString(
                mysql_character_set_name(self.conn))
            return self._charset
        def __set__(self, value):
            cdef char *svalue
            self._check_closed()
            svalue = PyString_AsString(value)
            if mysql_set_character_set(self.conn, svalue):
                self._raise_error()
            self._charset = value
    
    def warning_count(self):
        """warning_count() -> int
        
        Return the number of warnings caused by the most-previously-executed
        query or statement.
        """
        return mysql_warning_count(self.conn)
    
    def cursor(self, cursor_class=None, **kwargs):
        """cursor([cursor_class,] **cursor_options) -> Cursor.
        
        Create a new cursor associated with this connection of the specified 
        type. If no cursor class is specified, the 'default_cursor' attribute
        is used as the cursor class. The cursor_options will be forwarded to 
        the cursor's initializer; see the documentation for the cursor classes 
        for details.
        """
        self._check_closed()
        if cursor_class is None:
            cursor_class = self.default_cursor
        return cursor_class(self, **kwargs)
    
    property server_info:
        def __get__(self):
            self._check_closed()
            return mysql_get_server_info(self.conn)
    
    # FML.
    def _escape_string(self, value):
        """_escape_string(value) -> str.
        
        A wrapper around mysql_real_escape_string. Takes a bytestring in and 
        produces a bytestring out. Please do not every use this unless mysql
        refuses to parameterize a query; oursql has good support for 
        parameterization which also works consistently with unicode.
        """
        return _oursqlx_escape_string(self.conn, value)
    
    def _escape_unicode_string(self, value):
        """_escape_unicode_stirng(value) -> unicode.
        
        _escape_string that takes unicode in and produces unicode out, using
        the connection's charset. As with _escape_string, please do not use 
        this function.
        """
        return self._escape_string(
            value.encode(self.charset)).decode(self.charset)
