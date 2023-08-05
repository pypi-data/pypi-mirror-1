"""Main module, run me."""

import sys
from os import path
import imp
import curses
import getopt

from gobject import MainLoop, io_add_watch, timeout_add, IO_IN
from pysysmon import ui

def get_conf(fn):
    fp = file(fn, "U")
    try:
        m = imp.load_module("<pysysmon configuration>", fp, fn,
            ("py", "U", imp.PY_SOURCE))
    finally:
        fp.close()
    return m

def usage():
    print >>sys.stderr, "usage: %s [-c <conf>]" % sys.argv[0]
    sys.exit(1)

def no_conf(m=None):
    print >>sys.stderr, "No usable configuration found."
    print >>sys.stderr
    print >>sys.stderr, "Perhaps you need to set one up?"
    print >>sys.stderr, "See pysysmon/pysysmon_conf.py.example in the"
    print >>sys.stderr, "archive (if you didn't get one because you installed"
    print >>sys.stderr, "with easy_install or so, grab the archive manually"
    print >>sys.stderr, "from PyPI at http://pypi.python.org/pypi/pysysmon/)."
    if m:
        print >>sys.stderr
        print >>sys.stderr, str(m)
    sys.exit(2)

def main():
    conf_path = "~/.pysysmon_conf.py"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:")
    except getopt.GetoptError:
        usage()
    if args:
        usage()

    for opt, val in opts:
        if opt == "-c":
            conf_path = val

    try:
        conf = get_conf(path.expanduser(conf_path))
    except IOError, e:
        no_conf(e)

    def inner(s):
        z = ui.UI(s, conf)
        for cb, timer in z.get_timers():
            timeout_add(timer * 1000, cb)
        for fp, cb in z.get_read_watches():
            io_add_watch(fp, IO_IN, cb)
        MainLoop().run()
    curses.wrapper(inner)

if __name__ == "__main__":
    main()
