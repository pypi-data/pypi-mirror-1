#ifndef __PYX_HAVE__oursql
#define __PYX_HAVE__oursql
#ifdef __cplusplus
#define __PYX_EXTERN_C extern "C"
#else
#define __PYX_EXTERN_C extern
#endif

/* "C:\Documents and Settings\Owner\oursql-trunk\oursqlx/oursql.pyx":52
 * cimport exceptions
 * 
 * cdef public class Warning(exceptions.Warning) [             # <<<<<<<<<<<<<<
 *         object _oursqlx_WarningObject,
 *         type _oursqlx_Warning]: pass
 */

struct _oursqlx_WarningObject {
  PyBaseExceptionObject __pyx_base;
};

/* "C:\Documents and Settings\Owner\oursql-trunk\oursqlx/oursql.pyx":55
 *         object _oursqlx_WarningObject,
 *         type _oursqlx_Warning]: pass
 * cdef public class Note(Warning) [             # <<<<<<<<<<<<<<
 *         object _oursqlx_NoteObject,
 *         type _oursqlx_Note]: pass
 */

struct _oursqlx_NoteObject {
  struct _oursqlx_WarningObject __pyx_base;
};

/* "C:\Documents and Settings\Owner\oursql-trunk\oursqlx/oursql.pyx":59
 *         type _oursqlx_Note]: pass
 * 
 * cdef public class Error(exceptions.StandardError) [             # <<<<<<<<<<<<<<
 *         object _oursqlx_ErrorObject,
 *         type _oursqlx_Error]:
 */

struct _oursqlx_ErrorObject {
  PyBaseExceptionObject __pyx_base;
};

/* "C:\Documents and Settings\Owner\oursql-trunk\oursqlx/oursql.pyx":66
 *         self.errno = errno
 * 
 * cdef public class InterfaceError(Error) [             # <<<<<<<<<<<<<<
 *         object _oursqlx_InterfaceErrorObject,
 *         type _oursqlx_InterfaceError]: pass
 */

struct _oursqlx_InterfaceErrorObject {
  struct _oursqlx_ErrorObject __pyx_base;
};

/* "C:\Documents and Settings\Owner\oursql-trunk\oursqlx/oursql.pyx":69
 *         object _oursqlx_InterfaceErrorObject,
 *         type _oursqlx_InterfaceError]: pass
 * cdef public class DatabaseError(Error) [             # <<<<<<<<<<<<<<
 *         object _oursqlx_DatabaseErrorObject,
 *         type _oursqlx_DatabaseError]: pass
 */

struct _oursqlx_DatabaseErrorObject {
  struct _oursqlx_ErrorObject __pyx_base;
};

/* "C:\Documents and Settings\Owner\oursql-trunk\oursqlx/oursql.pyx":72
 *         object _oursqlx_DatabaseErrorObject,
 *         type _oursqlx_DatabaseError]: pass
 * cdef public class DataError(DatabaseError) [             # <<<<<<<<<<<<<<
 *         object _oursqlx_DataErrorObject,
 *         type _oursqlx_DataError]: pass
 */

struct _oursqlx_DataErrorObject {
  struct _oursqlx_DatabaseErrorObject __pyx_base;
};

/* "C:\Documents and Settings\Owner\oursql-trunk\oursqlx/oursql.pyx":75
 *         object _oursqlx_DataErrorObject,
 *         type _oursqlx_DataError]: pass
 * cdef public class OperationalError(DatabaseError) [             # <<<<<<<<<<<<<<
 *         object _oursqlx_OperationalErrorObject,
 *         type _oursqlx_OperationalError]: pass
 */

struct _oursqlx_OperationalErrorObject {
  struct _oursqlx_DatabaseErrorObject __pyx_base;
};

/* "C:\Documents and Settings\Owner\oursql-trunk\oursqlx/oursql.pyx":78
 *         object _oursqlx_OperationalErrorObject,
 *         type _oursqlx_OperationalError]: pass
 * cdef public class IntegrityError(DatabaseError) [             # <<<<<<<<<<<<<<
 *         object _oursqlx_IntegrityErrorObject,
 *         type _oursqlx_IntegrityError]: pass
 */

struct _oursqlx_IntegrityErrorObject {
  struct _oursqlx_DatabaseErrorObject __pyx_base;
};

/* "C:\Documents and Settings\Owner\oursql-trunk\oursqlx/oursql.pyx":81
 *         object _oursqlx_IntegrityErrorObject,
 *         type _oursqlx_IntegrityError]: pass
 * cdef public class InternalError(DatabaseError) [             # <<<<<<<<<<<<<<
 *         object _oursqlx_InternalErrorObject,
 *         type _oursqlx_InternalError]: pass
 */

struct _oursqlx_InternalErrorObject {
  struct _oursqlx_DatabaseErrorObject __pyx_base;
};

/* "C:\Documents and Settings\Owner\oursql-trunk\oursqlx/oursql.pyx":84
 *         object _oursqlx_InternalErrorObject,
 *         type _oursqlx_InternalError]: pass
 * cdef public class ProgrammingError(DatabaseError) [             # <<<<<<<<<<<<<<
 *         object _oursqlx_ProgrammingErrorObject,
 *         type _oursqlx_ProgrammingError]: pass
 */

struct _oursqlx_ProgrammingErrorObject {
  struct _oursqlx_DatabaseErrorObject __pyx_base;
};

/* "C:\Documents and Settings\Owner\oursql-trunk\oursqlx/oursql.pyx":87
 *         object _oursqlx_ProgrammingErrorObject,
 *         type _oursqlx_ProgrammingError]: pass
 * cdef public class NotSupportedError(DatabaseError) [             # <<<<<<<<<<<<<<
 *         object _oursqlx_NotSupportedErrorObject,
 *         type _oursqlx_NotSupportedError]: pass
 */

struct _oursqlx_NotSupportedErrorObject {
  struct _oursqlx_DatabaseErrorObject __pyx_base;
};

/* "C:\Documents and Settings\Owner\oursql-trunk\oursqlx/oursql.pyx":90
 *         object _oursqlx_NotSupportedErrorObject,
 *         type _oursqlx_NotSupportedError]: pass
 * cdef public class PermissionsError(DatabaseError) [             # <<<<<<<<<<<<<<
 *         object _oursqlx_PermissionsErrorObject,
 *         type _oursqlx_PermissionsError]: pass
 */

struct _oursqlx_PermissionsErrorObject {
  struct _oursqlx_DatabaseErrorObject __pyx_base;
};

#ifndef __PYX_HAVE_API__oursql

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) _oursqlx_Warning;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) _oursqlx_Note;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) _oursqlx_Error;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) _oursqlx_InterfaceError;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) _oursqlx_DatabaseError;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) _oursqlx_DataError;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) _oursqlx_OperationalError;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) _oursqlx_IntegrityError;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) _oursqlx_InternalError;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) _oursqlx_ProgrammingError;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) _oursqlx_NotSupportedError;
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) _oursqlx_PermissionsError;

#endif

PyMODINIT_FUNC initoursql(void);

#endif
