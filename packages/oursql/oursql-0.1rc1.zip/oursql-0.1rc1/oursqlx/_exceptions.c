
/* generated on Fri Oct 30 18:13:22 2009 */

#include "mysqld_error.h"
#include "errmsg.h"
#include <stdio.h>

/* When Cython generates a .h file for export, it's expecting that you'll be
 * importing the library (say, oursql.so) instead of linking with the oursql.o
 * file. So, make DL_IMPORT a no-op to keep compilers from complaining.
 */
#ifdef DL_IMPORT
#  undef DL_IMPORT
#endif
#define DL_IMPORT(x) x
#include "oursql.h"

PyTypeObject *_oursqlx_exc_from_errno(int err) {
    PyTypeObject *ret = NULL;
    char warning[50];
    switch (err) {

#ifdef ER_DUP_UNIQUE
        case ER_DUP_UNIQUE:
#endif

#ifdef ER_ROW_IS_REFERENCED
        case ER_ROW_IS_REFERENCED:
#endif

#ifdef ER_NO_REFERENCED_ROW
        case ER_NO_REFERENCED_ROW:
#endif

#ifdef ER_ROW_IS_REFERENCED_2
        case ER_ROW_IS_REFERENCED_2:
#endif

#ifdef ER_NO_REFERENCED_ROW_2
        case ER_NO_REFERENCED_ROW_2:
#endif

            ret = &_oursqlx_IntegrityError;
            break;

#ifdef ER_DUP_KEY
        case ER_DUP_KEY:
#endif

#ifdef ER_FILSORT_ABORT
        case ER_FILSORT_ABORT:
#endif

#ifdef ER_KEY_NOT_FOUND
        case ER_KEY_NOT_FOUND:
#endif

            ret = &_oursqlx_InternalError;
            break;

#ifdef ER_UNSUPPORTED_PS
        case ER_UNSUPPORTED_PS:
#endif

#ifdef CR_NOT_IMPLEMENTED
        case CR_NOT_IMPLEMENTED:
#endif

#ifdef ER_ILLEGAL_HA
        case ER_ILLEGAL_HA:
#endif

            ret = &_oursqlx_NotSupportedError;
            break;

#ifdef ER_CANT_CREATE_FILE
        case ER_CANT_CREATE_FILE:
#endif

#ifdef ER_CANT_CREATE_TABLE
        case ER_CANT_CREATE_TABLE:
#endif

#ifdef ER_CANT_CREATE_DB
        case ER_CANT_CREATE_DB:
#endif

#ifdef ER_DB_DROP_DELETE
        case ER_DB_DROP_DELETE:
#endif

#ifdef ER_DB_DROP_RMDIR
        case ER_DB_DROP_RMDIR:
#endif

#ifdef ER_CANT_DELETE_FILE
        case ER_CANT_DELETE_FILE:
#endif

#ifdef ER_CANT_FIND_SYSTEM_REC
        case ER_CANT_FIND_SYSTEM_REC:
#endif

#ifdef ER_CANT_GET_STAT
        case ER_CANT_GET_STAT:
#endif

#ifdef ER_CANT_GET_WD
        case ER_CANT_GET_WD:
#endif

#ifdef ER_CANT_LOCK
        case ER_CANT_LOCK:
#endif

#ifdef ER_CANT_OPEN_FILE
        case ER_CANT_OPEN_FILE:
#endif

#ifdef ER_FILE_NOT_FOUND
        case ER_FILE_NOT_FOUND:
#endif

#ifdef ER_CANT_READ_DIR
        case ER_CANT_READ_DIR:
#endif

#ifdef ER_CANT_SET_WD
        case ER_CANT_SET_WD:
#endif

#ifdef ER_CHECKREAD
        case ER_CHECKREAD:
#endif

#ifdef ER_DISK_FULL
        case ER_DISK_FULL:
#endif

#ifdef ER_ERROR_ON_CLOSE
        case ER_ERROR_ON_CLOSE:
#endif

#ifdef ER_ERROR_ON_READ
        case ER_ERROR_ON_READ:
#endif

#ifdef ER_ERROR_ON_RENAME
        case ER_ERROR_ON_RENAME:
#endif

#ifdef ER_ERROR_ON_WRITE
        case ER_ERROR_ON_WRITE:
#endif

#ifdef ER_FILE_USED
        case ER_FILE_USED:
#endif

#ifdef ER_GET_ERRNO
        case ER_GET_ERRNO:
#endif

            ret = &_oursqlx_OperationalError;
            break;

        default:
            if (err >= ER_ERROR_FIRST && err <= ER_ERROR_LAST)
                ret = &_oursqlx_ProgrammingError;
            else if (err > CR_MIN_ERROR && err < CR_MAX_ERROR)
                ret = &_oursqlx_InternalError;
    }
    if (!ret) {
        snprintf(warning, 50, 
            "could not find exception type for errno %i", err);
        PyErr_WarnEx((PyObject *)&_oursqlx_InterfaceError, warning, 1);
        ret = &_oursqlx_InterfaceError;
    }
    Py_INCREF(ret);
    return ret;
}
