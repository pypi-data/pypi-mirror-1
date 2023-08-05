"""Test bar."""

class TestBar(object):
    name = "test"
    refresh_rate = 1
    max = lambda s: 100
    timer = lambda s: True

    def current(self):
        self.i = (getattr(self, "i", 0) + 1) % 101
        return self.i
