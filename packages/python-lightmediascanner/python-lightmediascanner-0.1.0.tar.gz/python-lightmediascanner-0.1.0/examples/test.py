#!/usr/bin/python

import sys
import lightmediascanner

def usage():
    print "Usage:"
    print "\t%s" % sys.argv[0],
    print "<commit-interval> <slave-timeout> <db-path> <parsers>",
    print "<charsets> <scan-path>"

try:
    commit_interval = int(sys.argv[1])
    slave_timeout = int(sys.argv[2])
    db_path = sys.argv[3]
    parsers = sys.argv[4]
    charsets = sys.argv[5]
    scan_path = sys.argv[6]
except IndexError, e:
    usage()
    sys.exit(1)


parsers = parsers.split(',')
charsets = charsets.split(',')
lms = lightmediascanner.LightMediaScanner(db_path, parsers, charsets,
                                          slave_timeout, commit_interval)
print lms

lms.check(scan_path)
lms.process(scan_path)
