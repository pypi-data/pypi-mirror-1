# Copyright (C) 2007 by INdT
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# @author Gustavo Sverzut Barbieri <gustavo.barbieri@openbossa.org>

cdef extern from "Python.h":
    # ceval.h
    cdef enum:
        Py_BEGIN_ALLOW_THREADS
        Py_END_ALLOW_THREADS

    # object.h
    void Py_INCREF(object)
    void Py_DECREF(object)

    # stringobject.h
    object PyString_FromStringAndSize(char *v, Py_ssize_t len)


cdef extern from "lightmediascanner_plugin.h":
    ctypedef struct lms_plugin_t:
        char *name


cdef extern from "lightmediascanner.h":
    ctypedef struct lms_t

    ctypedef enum lms_progress_status_t:
        LMS_PROGRESS_STATUS_UP_TO_DATE
        LMS_PROGRESS_STATUS_PROCESSED
        LMS_PROGRESS_STATUS_DELETED
        LMS_PROGRESS_STATUS_KILLED
        LMS_PROGRESS_STATUS_ERROR_PARSE
        LMS_PROGRESS_STATUS_ERROR_COMM

    ctypedef void (*lms_free_callback_t)(void *data)
    ctypedef void (*lms_progress_callback_t)(lms_t *lms, char *path, int path_len, lms_progress_status_t status, void *data)

    lms_t *lms_new(char *db_path)
    int lms_free(lms_t *lms)
    int lms_process(lms_t *lms, char *top_path)
    int lms_check(lms_t *lms, char *top_path)
    int lms_process_single_process(lms_t *lms, char *top_path)
    int lms_check_single_process(lms_t *lms, char *top_path)
    void lms_stop_processing(lms_t *lms)
    int lms_is_processing(lms_t *lms)
    int lms_get_slave_timeout(lms_t *lms)
    void lms_set_slave_timeout(lms_t *lms, int ms)
    unsigned int lms_get_commit_interval(lms_t *lms)
    void lms_set_commit_interval(lms_t *lms, unsigned int transactions)
    void lms_set_progress_callback(lms_t *lms, lms_progress_callback_t cb, void *data, lms_free_callback_t free_data)

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

