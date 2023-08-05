"""Utility functions."""

sizes = "B", "KiB", "MiB", "GiB", "TiB"

def readable_size(bytes):
    try:
        bytes = float(bytes)
    except ValueError:
        return bytes
    lsize = "B"
    for size in sizes:
        lsize = size
        if bytes < 1024:
            break
        bytes /= 1024
    if bytes % 1:
        return "%.2f %s" % (bytes, lsize)
    else:
        return "%d %s" % (bytes, lsize)

if not hasattr(__builtins__, "any"):
    def any(iterable):
        return bool(filter(None, iterable))
