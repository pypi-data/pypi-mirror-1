"""Memory bar, shows memory usage."""

from pysysmon.readers.meminfo import get_memory_info

class MemoryBar(object):
    name = "Mem"
    refresh_rate = 5

    def __init__(self, name=name):
        self.name = name

    def max(self):
        if not hasattr(self, "_maxmem"):
            self._maxmem = get_memory_info()["MemTotal"]
        return self._maxmem

    def current(self):
        d = get_memory_info()
        return self.max() - d["MemFree"] - d["Buffers"] - d["Cached"]

    def timer(self):
        return True  # Refresh this bar.
