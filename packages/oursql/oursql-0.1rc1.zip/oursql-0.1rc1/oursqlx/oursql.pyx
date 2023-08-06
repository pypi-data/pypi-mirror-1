"""oursql python bindings for MySQL.

This module is a new, better set of MySQL bindings for python, supporting novel
features like parameterization!
"""

__author__ = 'Aaron Gallagher <habnabit@gmail.com>'
__version__ = '0.1rc1'

include "oursql.pxi"
include "nogil.pyx"

cdef unsigned int UNSIGNED_NUM_FLAG = UNSIGNED_FLAG | NUM_FLAG

cdef union column_data:
    MYSQL_TIME t
    long long ll
    unsigned long long ull
    unsigned long ul
    Py_ssize_t st
    long l
    float f
    double d
    char c
    char dec[65]
    
    int8_t s8
    int16_t s16
    int32_t s32
    int64_t s64
    
    uint8_t u8
    uint16_t u16
    uint32_t u32
    uint64_t u64

cdef union bitfield:
    char c[8]
    uint64_t u64

cdef struct column_output:
    enum_field_types type
    unsigned int flags
    bint is_binary
    unsigned long length
    my_bool is_null
    my_bool error
    column_data buf

cimport exceptions

cdef public class Warning(exceptions.Warning) [
        object _oursqlx_WarningObject, 
        type _oursqlx_Warning]: pass
cdef public class Note(Warning) [
        object _oursqlx_NoteObject, 
        type _oursqlx_Note]: pass

cdef public class Error(exceptions.StandardError) [
        object _oursqlx_ErrorObject, 
        type _oursqlx_Error]:
    def __init__(self, message, errno=None):
        super(Error, self).__init__(message, errno)
        self.errno = errno

cdef public class InterfaceError(Error) [
        object _oursqlx_InterfaceErrorObject, 
        type _oursqlx_InterfaceError]: pass
cdef public class DatabaseError(Error) [
        object _oursqlx_DatabaseErrorObject, 
        type _oursqlx_DatabaseError]: pass
cdef public class DataError(DatabaseError) [
        object _oursqlx_DataErrorObject, 
        type _oursqlx_DataError]: pass
cdef public class OperationalError(DatabaseError) [
        object _oursqlx_OperationalErrorObject, 
        type _oursqlx_OperationalError]: pass
cdef public class IntegrityError(DatabaseError) [
        object _oursqlx_IntegrityErrorObject, 
        type _oursqlx_IntegrityError]: pass
cdef public class InternalError(DatabaseError) [
        object _oursqlx_InternalErrorObject, 
        type _oursqlx_InternalError]: pass
cdef public class ProgrammingError(DatabaseError) [
        object _oursqlx_ProgrammingErrorObject, 
        type _oursqlx_ProgrammingError]: pass
cdef public class NotSupportedError(DatabaseError) [
        object _oursqlx_NotSupportedErrorObject, 
        type _oursqlx_NotSupportedError]: pass
cdef public class PermissionsError(DatabaseError) [
        object _oursqlx_PermissionsErrorObject, 
        type _oursqlx_PermissionsError]: pass

include "util.pyx"
include "conversions.pyx"
include "connection.pyx"
include "statement.pyx"
include "query.pyx"
include "cursor.pyx"

paramstyle = 'qmark'
threadsafety = 1
apilevel = '2.0'
connect = Connection

cdef class _DBAPITypeObject:
    cdef readonly object values
    
    def __init__(self, *values):
        self.values = frozenset(values)
    
    def __richcmp__(self, other, int op):
        if op == Py_EQ:
            return other in self.values
        elif op == Py_NE:
            return other not in self.values
        else:
            raise TypeError('unorderable types: %r and %r' % (
                type(self), type(other)))
    
    def __repr__(self):
        return '<_DBAPITypeObject representing %r at %#x>' % (
            self.values, id(self))

STRING = _DBAPITypeObject(
    MYSQL_TYPE_ENUM, MYSQL_TYPE_STRING, MYSQL_TYPE_VAR_STRING)
BINARY = _DBAPITypeObject(
    MYSQL_TYPE_BLOB, MYSQL_TYPE_LONG_BLOB, 
    MYSQL_TYPE_MEDIUM_BLOB, MYSQL_TYPE_TINY_BLOB)
NUMBER = _DBAPITypeObject(
    MYSQL_TYPE_DECIMAL, MYSQL_TYPE_DOUBLE, MYSQL_TYPE_FLOAT, MYSQL_TYPE_INT24, 
    MYSQL_TYPE_LONG, MYSQL_TYPE_LONGLONG, MYSQL_TYPE_TINY, MYSQL_TYPE_YEAR)
DATE = _DBAPITypeObject(
    MYSQL_TYPE_DATE, MYSQL_TYPE_NEWDATE)
TIME = _DBAPITypeObject(
    MYSQL_TYPE_TIME)
DATETIME = TIMESTAMP = _DBAPITypeObject(
    MYSQL_TYPE_TIMESTAMP, MYSQL_TYPE_DATETIME)
ROWID = _DBAPITypeObject()
