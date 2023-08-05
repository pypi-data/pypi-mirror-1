"""Process watching service."""

import subprocess

class ProcessWatcher(object):
    refresh_rate = 20

    def __init__(self, name, pgrep_opts):
        self.name = name
        self.args = ("pgrep",) + tuple(pgrep_opts)

    def ok(self):
        return subprocess.Popen(self.args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait() == 0

    def timer(self):
        return True
