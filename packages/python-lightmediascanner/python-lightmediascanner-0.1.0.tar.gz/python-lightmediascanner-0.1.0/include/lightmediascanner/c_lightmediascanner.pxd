cdef extern from "lightmediascanner_plugin.h":
    ctypedef struct lms_plugin_t:
        char *name


cdef extern from "lightmediascanner.h":
    ctypedef struct lms_t

    lms_t *lms_new(char *db_path)
    int lms_free(lms_t *lms)
    int lms_process(lms_t *lms, char *top_path)
    int lms_check(lms_t *lms, char *top_path)
    int lms_is_processing(lms_t *lms)
    int lms_get_slave_timeout(lms_t *lms)
    void lms_set_slave_timeout(lms_t *lms, int ms)
    unsigned int lms_get_commit_interval(lms_t *lms)
    void lms_set_commit_interval(lms_t *lms, unsigned int transactions)

    lms_plugin_t *lms_parser_add(lms_t *lms, char *so_path)
    lms_plugin_t *lms_parser_find_and_add(lms_t *lms, char *name)
    int lms_parser_del(lms_t *lms, lms_plugin_t *handle)

    int lms_charset_add(lms_t *lms, char *charset)
    int lms_charset_del(lms_t *lms, char *charset)


cdef class LightMediaScanner:
    cdef lms_t *obj
    cdef readonly object parsers
    cdef readonly object db_path


cdef class Parser:
    cdef lms_plugin_t *obj
    cdef readonly LightMediaScanner scanner

    cdef int _set_obj(self, lms_plugin_t *obj) except 0
    cdef int _unset_obj(self) except 0

