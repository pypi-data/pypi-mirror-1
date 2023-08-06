
/* generated on Sat Oct 31 03:51:42 2009 */

#include "mysqld_error.h"
#include "errmsg.h"

enum _oursqlx_exception_type _oursqlx_exc_from_errno(int err) {
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

            return _oursqlx_IntegrityError;

#ifdef ER_DUP_KEY
        case ER_DUP_KEY:
#endif

#ifdef ER_FILSORT_ABORT
        case ER_FILSORT_ABORT:
#endif

#ifdef ER_KEY_NOT_FOUND
        case ER_KEY_NOT_FOUND:
#endif

            return _oursqlx_InternalError;

#ifdef ER_UNSUPPORTED_PS
        case ER_UNSUPPORTED_PS:
#endif

#ifdef CR_NOT_IMPLEMENTED
        case CR_NOT_IMPLEMENTED:
#endif

#ifdef ER_ILLEGAL_HA
        case ER_ILLEGAL_HA:
#endif

            return _oursqlx_NotSupportedError;

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

            return _oursqlx_OperationalError;

        default:
            if (err >= ER_ERROR_FIRST && err <= ER_ERROR_LAST)
                return _oursqlx_ProgrammingError;
            else if (err > CR_MIN_ERROR && err < CR_MAX_ERROR)
                return _oursqlx_InternalError;
    }
    return _oursqlx_UnknownError;
}
