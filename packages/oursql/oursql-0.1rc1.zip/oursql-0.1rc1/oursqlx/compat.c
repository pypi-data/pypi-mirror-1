#include "compat.h"

my_bool _oursqlx_init_stmt_cursor(MYSQL_STMT *stmt, unsigned long *cursor_type) {
#if MYSQL_VERSION_ID >= 50002
    *cursor_type = CURSOR_TYPE_READ_ONLY;
    return mysql_stmt_attr_set(stmt, STMT_ATTR_CURSOR_TYPE, cursor_type);
#else
    return 0;
#endif
}

my_bool _oursqlx_stmt_set_prefetch_rows(MYSQL_STMT *stmt, 
        unsigned long *nrows) {
#if MYSQL_VERSION_ID >= 50006
    return mysql_stmt_attr_set(stmt, STMT_ATTR_PREFETCH_ROWS, nrows);
#else
    return 0;
#endif
}

int _oursqlx_stmt_cursor_prefetch(MYSQL_STMT *stmt, int *buffered) {
#if MYSQL_VERSION_ID < 50002
    int ret = mysql_stmt_store_result(stmt);
    if (!ret)
        *buffered = 1;
    return ret;
#else
    return 0;
#endif
}

int _oursqlx_PyObject_AsReadBuffer(PyObject *o, void **b, Py_ssize_t *s) {
    return PyObject_AsReadBuffer(o, (const void **)b, s);
}

#include "_exceptions.c"
