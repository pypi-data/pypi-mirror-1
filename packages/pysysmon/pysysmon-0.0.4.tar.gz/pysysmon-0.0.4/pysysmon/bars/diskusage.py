"""Bar for disk usage."""

from os import path
import subprocess

class DiskUsage(object):
    refresh_rate = 60 * 5  # 5 minutes

    def __init__(self, device, name=None):
        self.device = device
        self.name = name or path.basename(device)

    max = lambda s: 100
    timer = lambda s: True

    def current(self):
        p = subprocess.Popen(("df", "-Pl", self.device), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.wait():
            #raise ValueError("df returned non-zero")
            return 0
        parts = filter(None, p.stdout.read().split("\n")[1].split(" "))
        return int(parts[-2][:-1])
