#!/usr/bin/env python
"""pyrg - colorized Python's UnitTest Result Tool"""
from ConfigParser import ConfigParser
from subprocess import Popen, PIPE
from select import poll, POLLIN
import sys
import re
import os

__version__ = '0.2.2'
__author__ = 'Hideo Hattroi <hhatto.jp@gmail.com>'
__license__ = 'NewBSDLicense'

__all__ = ['get_color', 'parse_result_line', 'parse_lineone',
           'coloring_method', 'parse_unittest_result',
           'get_configfile_path', 'set_configration']

PRINT_COLOR_SET = {
        'ok': 'green',
        'fail': 'red',
        'error': 'yellow',
        'function': 'cyan',
}
COLOR_MAP = {
        'black': '[30m%s[0m',
        'gray': '[1;30m%s[0m',
        #'black ': '[2;30m%s[0m',   ## TODO:not worked?
        'red': '[31m%s[0m',
        'pink': '[1;31m%s[0m',
        'darkred': '[2;31m%s[0m',
        'green': '[32m%s[0m',
        'yellowgreen': '[1;32m%s[0m',
        'darkgreen': '[2;32m%s[0m',
        'brown': '[33m%s[0m',
        'yellow': '[1;33m%s[0m',
        'gold': '[2;33m%s[0m',
        'blue': '[34m%s[0m',
        'lightblue': '[1;34m%s[0m',
        'darkblue': '[2;34m%s[0m',
        'magenta': '[35m%s[0m',
        'lightmagenta': '[1;35m%s[0m',
        'darkmagenta': '[2;35m%s[0m',
        'cyan': '[36m%s[0m',
        'lightcyan': '[1;36m%s[0m',
        'darkcyan': '[2;36m%s[0m',
        'silver': '[37m%s[0m',
        'white': '[1;37m%s[0m',
        'darksilver': '[2;37m%s[0m',
        }


def get_color(key):
    """color name get from COLOR_MAP dict."""
    return COLOR_MAP[PRINT_COLOR_SET[key]]


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
        result = "(%s=%s. " % (get_color('fail') % "failures",
                               get_color('fail') % f)
        result += "%s=%s)" % (get_color('error') % "errors",
                              get_color('error') % e)
    elif fail and not err:
        l = line.split('=')[1].split(')')[0]
        result = "(%s=%s)" % (get_color('fail') % "failures",
                              get_color('fail') % l)
    elif err and not fail:
        l = line.split('=')[1].split(')')[0]
        result = "(%s=%s)" % (get_color('error') % "errors",
                              get_color('error') % l)
    return get_color('fail') % "FAILED" + " %s" % result


def parse_lineone(line):
    """parse to test result line1"""
    results = []
    line = line.strip()
    for char in line:
        if '.' == char:
            results.append(get_color('ok') % ".")
        elif 'E' == char:
            results.append(get_color('error') % "E")
        elif 'F' == char:
            results.append(get_color('fail') % "F")
        else:
            results.append(char)
    return "".join(results)


def coloring_method(line):
    """colorized method line"""
    return get_color('function') % line


def parse_unittest_result(lines):
    """parse test result"""
    results = []
    err = re.compile("ERROR:")
    fail = re.compile("FAIL:")
    ok = re.compile("OK")
    failed = re.compile("FAILED")
    results.append(parse_lineone(lines[0]) + '\n')
    for line in lines[1:]:
        if ok.match(line):
            result = get_color('ok') % "OK"
        elif failed.match(line):
            result = parse_result_line(line)
        elif fail.match(line):
            result = "%s:%s" % (get_color('fail') % "FAIL",
                                coloring_method(line[5:]))
        elif err.match(line):
            result = "%s:%s" % (get_color('error') % "ERROR",
                                coloring_method(line[6:]))
        else:
            result = line
        results.append(result)
    return "".join(results)


def get_configfile_path():
    """get $HOME/.pyrgrc path"""
    return "/home/%s/.pyrgrc" % (os.getlogin())


def set_configration():
    """setting to printing color map"""
    filename = get_configfile_path()
    if not os.path.exists(filename):
        print "default configration"
        return
    configure = ConfigParser()
    configure.read(filename)
    for item in configure.items('color'):
        PRINT_COLOR_SET[item[0]] = COLOR_MAP[item[1]]
    return


def main():
    """execute command line tool"""
    set_configration()
    if sys.argv[1:]:
        proc = Popen(['python', sys.argv[1]], stdout=PIPE, stderr=PIPE)
        result = proc.communicate()[1]
        print parse_unittest_result(result.splitlines(1))
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
