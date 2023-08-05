"""Memory info reader for Linux."""

from os import path

def get_memory_info():
    f = file(path.join("/", "proc", "meminfo"))
    d = {}
    try:
        for l in f:
            k, rv = l.split(": ", 1)
            rv = rv.lstrip(" ")[:-1]  # Trim off \n too.
            if not rv.endswith(" kB"):
                raise ValueError("line ends not in ' kb'.")
            d[k] = int(rv[:-3]) * 1024  # it's KiB => bytes
    finally:
        f.close()
    return d

def pprint_all():
    from pprint import pprint
    pprint(get_memory_info())

if __name__ == "__main__":
    pprint_all()
