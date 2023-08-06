#!/usr/bin/env python
"""pyrg - colorized Python's UnitTest Result Tool"""
from subprocess import Popen, PIPE
from select import poll, POLLIN
import sys
import re

__version__ = '0.2.1'
__author__ = 'Hideo Hattroi <hhatto.jp@gmail.com>'
__license__ = 'NewBSDLicense'

OK_COLOR = "[32m%s[0m"
FAIL_COLOR = "[31m%s[0m"
ERROR_COLOR = "[33m%s[0m"
FUNC_COLOR = "[36m%s[0m"


def parse_result_line(line):
    """parse to test result when fail tests"""
    err = False
    fail = False
    if 'errors' in line:
        err = True
    if 'failures' in line:
        fail = True
    if err and fail:
        f = line.split('=')[1].split(',')[0]
        e = line.split('=')[2].split(')')[0]
        result = "(" + FAIL_COLOR % "failures" + "=" + FAIL_COLOR % f + ", "
        result += ERROR_COLOR % "errors" + "=" + ERROR_COLOR % e + ")"
    elif fail and not err:
        l = line.split('=')[1].split(')')[0]
        result = "(" + FAIL_COLOR % "failures" + "=" + FAIL_COLOR % l + ")"
    elif err and not fail:
        l = line.split('=')[1].split(')')[0]
        result = "(" + ERROR_COLOR % "errors" + "=" + ERROR_COLOR % l + ")"
    return FAIL_COLOR % "FAILED" + " %s" % result


def parse_lineone(line):
    """parse to test result line1"""
    results = []
    line = line.strip()
    for char in line:
        if '.' == char:
            results.append(OK_COLOR % ".")
        elif 'E' == char:
            results.append(ERROR_COLOR % "E")
        elif 'F' == char:
            results.append(FAIL_COLOR % "F")
        else:
            results.append(char)
    return "".join(results)


def coloring_method(line):
    """colorized method line"""
    return FUNC_COLOR % line


def parse_unittest_result(lines):
    """parse test result"""
    results = []
    err = re.compile("ERROR:")
    fail = re.compile("FAIL:")
    ok = re.compile("OK")
    failed = re.compile("FAILED")
    results.append(parse_lineone(lines[0])+'\n')
    for line in lines[1:]:
        if ok.match(line):
            result = OK_COLOR % "OK"
        elif failed.match(line):
            result = parse_result_line(line)
        elif fail.match(line):
            result = FAIL_COLOR % "FAIL" + ":" + coloring_method(line[5:])
        elif err.match(line):
            result = ERROR_COLOR % "ERROR" + ":" + coloring_method(line[6:])
        else:
            result = line
        results.append(result)
    return "".join(results)


def main():
    """execute command line tool"""
    if sys.argv[1:]:
        p = Popen(['python', sys.argv[1]], stdout=PIPE, stderr=PIPE)
        r = p.communicate()[1]
        print parse_unittest_result(r.splitlines(1))
    else:
        poller = poll()
        poller.register(sys.stdin, POLLIN)
        pollret = poller.poll(1)
        if len(pollret) == 1 and pollret[0][1] & POLLIN:
            print parse_unittest_result(sys.stdin.readlines())
        else:
            print __doc__
            print "version:", __version__
            print "usage: pyrg pythontest.py"
            print "       python pythontest.py |& pyrg"
            print ""

if __name__ == '__main__':
    sys.exit(main())
