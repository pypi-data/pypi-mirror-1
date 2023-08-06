#!/usr/bin/env python
import time
import sys

file_template = """
/* generated on %(when)s */

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
%(code)s
        default:
            if (err >= ER_ERROR_FIRST && err <= ER_ERROR_LAST)
                ret = &_oursqlx_ProgrammingError;
            else if (err > CR_MIN_ERROR && err < CR_MAX_ERROR)
                ret = &_oursqlx_InternalError;
    }
    if (!ret) {
        snprintf(warning, 50, 
            "could not find exception type for errno %%i", err);
        PyErr_WarnEx((PyObject *)&_oursqlx_InterfaceError, warning, 1);
        ret = &_oursqlx_InterfaceError;
    }
    Py_INCREF(ret);
    return ret;
}
"""

case_template = """
#ifdef %(const)s
        case %(const)s:
#endif
"""
return_template = """
            ret = &%(exc)s;
            break;
"""

data = dict(
    _oursqlx_OperationalError="""
        ER_CANT_CREATE_FILE
        ER_CANT_CREATE_TABLE
        ER_CANT_CREATE_DB
        ER_DB_DROP_DELETE
        ER_DB_DROP_RMDIR
        ER_CANT_DELETE_FILE
        ER_CANT_FIND_SYSTEM_REC
        ER_CANT_GET_STAT
        ER_CANT_GET_WD
        ER_CANT_LOCK
        ER_CANT_OPEN_FILE
        ER_FILE_NOT_FOUND
        ER_CANT_READ_DIR
        ER_CANT_SET_WD
        ER_CHECKREAD
        ER_DISK_FULL
        ER_ERROR_ON_CLOSE
        ER_ERROR_ON_READ
        ER_ERROR_ON_RENAME
        ER_ERROR_ON_WRITE
        ER_FILE_USED
        ER_GET_ERRNO
    """,
    _oursqlx_InternalError="""
        ER_DUP_KEY
        ER_FILSORT_ABORT
        ER_KEY_NOT_FOUND
    """,
    _oursqlx_IntegrityError="""
        ER_DUP_UNIQUE
        ER_ROW_IS_REFERENCED
        ER_NO_REFERENCED_ROW
        ER_ROW_IS_REFERENCED_2
        ER_NO_REFERENCED_ROW_2
    """,
    _oursqlx_NotSupportedError="""
        ER_UNSUPPORTED_PS
        CR_NOT_IMPLEMENTED
        ER_ILLEGAL_HA
    """,
)

def main(outfile):
    output = []
    for exc, consts in sorted(data.iteritems()):
        for const in consts.split():
            output.append(case_template % dict(const=const))
        output.append(return_template % dict(exc=exc))
    outfile.write(file_template % dict(
        when=time.asctime(),
        code=''.join(output),
    ))
    

if __name__ == '__main__':
    main(open(sys.argv[1], 'wb'))
