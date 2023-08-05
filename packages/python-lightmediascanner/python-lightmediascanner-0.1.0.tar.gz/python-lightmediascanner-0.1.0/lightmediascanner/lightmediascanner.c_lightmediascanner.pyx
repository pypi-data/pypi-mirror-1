cdef class LightMediaScanner:
    def __init__(self, char *db_path, parsers=None, charsets=None,
                 slave_timeout=None, commit_interval=None):
        if self.obj == NULL:
            self.parsers = ()
            self.obj = lms_new(db_path)
            self.db_path = db_path
            if self.obj == NULL:
                raise SystemError("Could not create LightMediaScanner.")
            if parsers:
                for p in parsers:
                    self.parser_find_and_add(p)
            if charsets:
                for c in charsets:
                    self.charset_add(c)
            if slave_timeout is not None:
                self.set_slave_timeout(slave_timeout)
            if commit_interval is not None:
                self.set_commit_interval(commit_interval)

    def __dealloc__(self):
        if self.obj != NULL:
            if lms_free(self.obj) != 0:
                raise SystemError("Could not free internal object.")

    def __str__(self):
        parsers = []
        for p in self.parsers:
            parsers.append(str(p))
        parsers = ", ".join(parsers)
        return ("%s(db_path=%r, slave_timeout=%d, commit_interval=%d, "
                "parsers=[%s])") % (self.__class__.__name__, self.db_path,
                                    self.slave_timeout, self.commit_interval,
                                    parsers)

    def __repr__(self):
        parsers = []
        for p in self.parsers:
            parsers.append(repr(p))
        parsers = ", ".join(parsers)
        return ("%s(%#x, lms_t=%#x, db_path=%r, slave_timeout=%d, "
                "commit_interval=%d, parsers=[%s])") % \
                (self.__class__.__name__, <unsigned>self, <unsigned>self.obj,
                 self.db_path, self.slave_timeout, self.commit_interval,
                 parsers)

    def process(self, char *top_path):
        """Process directory recursively.

        This operates on all files in all sub directories of top_path using
        the added parsers.
        """
        if self.obj == NULL:
            raise ValueError("LightMediaScanner is shallow.")
        return lms_process(self.obj, top_path)

    def check(self, char *top_path):
        """Check (and update) files under directory.

        This operates on all files in all sub directories of top_path using
        the added parsers. If files are up to date, nothing is done, otherwise
        they can be marked as deleted or updated if they still exists, but
        with different size or modification time.
        """
        if self.obj == NULL:
            raise ValueError("LightMediaScanner is shallow.")
        return lms_check(self.obj, top_path)

    def parser_find_and_add(self, char *name):
        """Add a new plugin/parser based on it's name.

        @rtype: L{Parser}
        """
        cdef lms_plugin_t *p
        cdef Parser parser
        if self.obj == NULL:
            raise ValueError("LightMediaScanner is shallow.")
        p = lms_parser_find_and_add(self.obj, name)
        if p == NULL:
            raise ValueError("LightMediaScanner cannot add parser %r" % name)
        parser = Parser(self)
        parser._set_obj(p)
        self.parsers = self.parsers + (parser,)

    def parser_add(self, char *so_path):
        """Add a new plugin/parser based on it's whole path to shared object.

        @rtype: L{Parser}
        """
        cdef lms_plugin_t *p
        cdef Parser parser
        if self.obj == NULL:
            raise ValueError("LightMediaScanner is shallow.")
        p = lms_parser_add(self.obj, so_path)
        if p == NULL:
            raise ValueError("LightMediaScanner cannot add parser %r" % so_path)
        parser = Parser(self)
        parser._set_obj(p)
        self.parsers = self.parsers + (parser,)

    def parser_del(self, Parser parser):
        "Delete a plugin/parser."
        if self.obj == NULL:
            raise ValueError("LightMediaScanner is shallow.")
        if lms_parser_del(self.obj, parser.obj) != 0:
            raise SystemError("Could not delete parser %s" % parser)

        parsers = []
        for p in self.parsers:
            if p != parser:
                parsers.append(p)
        self.parsers = tuple(parsers)
        parser._unset_obj()

    def is_processing(self):
        "@rtype: bool"
        if self.obj == NULL:
            raise ValueError("LightMediaScanner is shallow.")
        return bool(lms_is_processing(self.obj))

    def get_slave_timeout(self):
        "@rtype: int"
        if self.obj == NULL:
            raise ValueError("LightMediaScanner is shallow.")
        return lms_get_slave_timeout(self.obj)

    def set_slave_timeout(self, int ms):
        """Set maximum time a parser may use.

        This will be the timeout before killing the slave process running
        some parser. If this happens, another slave process will be
        started to continue from next file.
        """
        if self.obj == NULL:
            raise ValueError("LightMediaScanner is shallow.")
        lms_set_slave_timeout(self.obj, ms)

    property slave_timeout:
        def __get__(self):
            return self.get_slave_timeout()

        def __set__(self, int ms):
            self.set_slave_timeout(ms)

    def get_commit_interval(self):
        "@rtype: int"
        if self.obj == NULL:
            raise ValueError("LightMediaScanner is shallow.")
        return lms_get_commit_interval(self.obj)

    def set_commit_interval(self, unsigned int transactions):
        """Set the number of transactions between commits.

        Sets how many transactions/files to handle in one commit, the more
        the faster, but if one parser takes too long and it's killed due
        slave_timeout being exceeded, then at most this number of transactions
        will be lost.

        Note that transaction here is not a single SQL statement, but it is
        considered to be the processing of a file, which can be more than
        just one.
        """
        if self.obj == NULL:
            raise ValueError("LightMediaScanner is shallow.")
        lms_set_commit_interval(self.obj, transactions)

    property commit_interval:
        def __get__(self):
            return self.get_commit_interval()

        def __set__(self, unsigned int transactions):
            self.set_commit_interval(transactions)

    def charset_add(self, char *charset):
        """Add charset to list of supported input charsets/encoding.

        If some string in analysed/parsed files are not UTF-8, then
        it will try agains a list of charsets registered with this function.
        """
        if self.obj == NULL:
            raise ValueError("LightMediaScanner is shallow.")
        if lms_charset_add(self.obj, charset) != 0:
            raise SystemError("LightMediaScanner cannot add charset %r" %
                              charset)

    def charset_del(self, char *charset):
        "Del charset from list of supported input charsets/encoding."
        if self.obj == NULL:
            raise ValueError("LightMediaScanner is shallow.")
        if lms_charset_del(self.obj, charset) != 0:
            raise SystemError("LightMediaScanner cannot del charset %r" %
                              charset)


cdef class Parser:
    def __init__(self, scanner):
        self.scanner = scanner

    def __str__(self):
        return "%s(name=%r)" % (self.__class__.__name__, self.name)

    def __repr__(self):
        return "%s(%#x, lms_plugin_t=%#x, name=%r)" % \
               (self.__class__.__name__, <unsigned>self, <unsigned>self.obj,
                self.name)

    cdef int _set_obj(self, lms_plugin_t *obj) except 0:
        if self.obj != NULL:
            raise ValueError("Parser already wraps an object.")
        self.obj = obj
        return 1

    cdef int _unset_obj(self) except 0:
        self.obj = NULL
        return 1

    def delete(self):
        "Same as LightMediaScanner.parser_del(self)."
        self.scanner.parser_del(self)

    property name:
        def __get__(self):
            if self.obj == NULL:
                return None
            if self.obj.name == NULL:
                return None
            return self.obj.name
