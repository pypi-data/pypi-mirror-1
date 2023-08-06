/* I really don't understand the thought process behind most of mysql. */
#ifdef _WIN32
#  include "my_global.h"
#endif
#include "mysql.h"
#include "Python.h"

#if MYSQL_VERSION_ID < 40102
#error "This driver requires at least MySQL 4.1.2."
#endif

my_bool _oursqlx_init_stmt_cursor(MYSQL_STMT *, unsigned long *);
my_bool _oursqlx_stmt_set_prefetch_rows(MYSQL_STMT *, unsigned long *);
int _oursqlx_stmt_cursor_prefetch(MYSQL_STMT *, int *);
int _oursqlx_PyObject_AsReadBuffer(PyObject *, void **, Py_ssize_t *);
PyTypeObject *_oursqlx_exc_from_errno(int);
