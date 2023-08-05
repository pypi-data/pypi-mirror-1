#!/usr/bin/env python
"""Block device reader for Linux 2.6"""

from os import path, listdir
from itertools import izip

class BlockStat(object):
    _val_keys = ("read_ios", "read_merges", "read_sectors", "read_ticks",
        "write_ios", "write_merges", "write_sectors", "write_ticks",
        "in_flight", "io_ticks", "time_in_queue")

    def __init__(self, devname):
        self.path = path.join("/", "sys", "block", devname, "stat")

    def _get_vals(self):
        f = file(self.path, "r")
        try:
            d = f.read()
        finally:
            f.close()
        return [int(x) for x in d.replace("\n", "").split(" ") if x]

    def stats(self):
        return dict(izip(self._val_keys, self._get_vals()))

def get_statables():
    base = path.join("/", "sys", "block")
    return iter(listdir(base))
    # So far, this hasn't been needed.
    #for devname in listdir(base):
    #    fn = path.join(base, devname)
    #    if path.isdir(fn) and path.exists(path.join(fn, "stat")):
    #        yield devname

def pprint_all():
    from pprint import pprint

    [pprint((dev, BlockStat(dev).stats())) for dev in get_statables()]

if __name__ == "__main__":
    pprint_all()
