#!/usr/bin/python

import sys
import lightmediascanner

def usage():
    print "Usage:"
    print "\t%s" % sys.argv[0],
    print "<api-select> <commit-interval> <slave-timeout> <db-path> <parsers>",
    print "<charsets> <scan-path>"
    print "where api-select may be:"
    print "\t0,  for dual process lms (main API)"
    print "\t1,  for single process lms (secondary API)",

if len(sys.argv) != 8:
    usage()
    sys.exit(1)

try:
    api_select = int(sys.argv[1])
    commit_interval = int(sys.argv[2])
    slave_timeout = int(sys.argv[3])
    db_path = sys.argv[4]
    parsers = sys.argv[5]
    charsets = sys.argv[6]
    scan_path = sys.argv[7]
except IndexError, e:
    usage()
    sys.exit(2)

if not api_select in [0, 1]:
    usage()
    sys.exit(3)

parsers = parsers.split(',')
charsets = charsets.split(',')
lms = lightmediascanner.LightMediaScanner(db_path, parsers, charsets,
                                          slave_timeout, commit_interval)

if api_select == 0:
    check = lms.check
    process = lms.process
else:
    check = lms.check_single_process
    process = lms.process_single_process

print lms

s = [
    "UP_TO_DATE",
    "PROCESSED",
    "DELETED",
    "KILLED",
    "ERROR_PARSE",
    "ERROR_COMM",
    ]

def progress(lms, path, status):
    print path, s[status]

lms.set_progress_callback(progress)

print "check:", scan_path
check(scan_path)
print "process:", scan_path
process(scan_path)

lms.set_progress_callback(None)
lms.parsers_clear()
del lms
