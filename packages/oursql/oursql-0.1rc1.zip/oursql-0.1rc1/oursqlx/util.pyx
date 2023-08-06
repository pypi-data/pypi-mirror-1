cdef object conversion_info_from_res(MYSQL_RES *res, int fields):
    cdef int i
    cdef MYSQL_FIELD *field
    ret = PyList_New(fields)
    for 0 <= i < fields:
        field = mysql_fetch_field_direct(res, i)
        data = (
            field.type,
            field.flags,
            field.charsetnr)
        Py_INCREF(data)
        PyList_SET_ITEM(ret, i, data)
    return ret

cdef object description_from_res(MYSQL_RES *res, int fields, bint show_table):
    cdef int i
    cdef MYSQL_FIELD *field
    ret = PyList_New(fields)
    for 0 <= i < fields:
        field = mysql_fetch_field_direct(res, i)
        if show_table and field.table[0] != 0:
            name = PyString_FromFormat("%s.%s", 
                field.table, field.name)
        else:
            name = field.name
        data = (
            name,
            field.type,
            field.max_length,
            field.length,
            field.length,
            field.decimals,
            field.flags & NOT_NULL_FLAG != NOT_NULL_FLAG)
        Py_INCREF(data)
        PyList_SET_ITEM(ret, i, data)
    return ret

cdef class _DictWhateverMixin:
    def fetchone(self):
        row = super(_DictWhateverMixin, self).fetchone()
        if row is None:
            return None
        ret = {}
        for name, value in zip(self.column_names, row):
            if name in ret:
                if ret[name] != value:
                    raise ProgrammingError('column "%s" appears more than once'
                        ' in output' % name)
            else:
                ret[name] = value
        return ret

def _exception_from_errno(int err):
    return _oursqlx_exc_from_errno(err)

def _exceptions_from_warnings_query(results):
    ret = []
    for kind, err, message in results:
        if kind == 'Note':
            kind = Note
        elif kind == 'Warning':
            kind = Warning
        elif kind == 'Error':
            kind = _exception_from_errno(err)
        else:
            raise InterfaceError('unknown kind of warning: %r' % kind)
        ret.append((kind, (message, err)))
    return ret
