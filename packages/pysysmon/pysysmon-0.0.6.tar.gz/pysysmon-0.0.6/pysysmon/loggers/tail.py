"""Follow a file line-by-line."""

class Tail(object):
    refresh_rate = 1

    def __init__(self, filename):
        self.fp = file(filename, "r")
        self.fp.seek(0, 2)  # Seek to end.
        self.insts = []
        self.buffer = ""

    def __call__(self, inst):
        self.insts.append(inst)
        return self

    def timer(self):
        d = self.fp.read()
        self.buffer += d
        lines = self.buffer.split("\n")
        self.buffer = lines.pop()
        [self.handle(line) for line in lines]

    def log(self, line):
        [inst.log(line) for inst in self.insts]

    handle = log
