"""Main module, run me."""

from os import path
import imp
import curses

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

def main():
    def inner(s):
        conf = get_conf(path.expanduser("~/.pysysmon_conf.py"))
        z = ui.UI(s, conf)
        for cb, timer in z.get_timers():
            timeout_add(timer * 1000, cb)
        for fp, cb in z.get_read_watches():
            io_add_watch(fp, IO_IN, cb)
        MainLoop().run()
    curses.wrapper(inner)

if __name__ == "__main__":
    main()
