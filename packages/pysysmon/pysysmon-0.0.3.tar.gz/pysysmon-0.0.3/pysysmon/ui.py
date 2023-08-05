"""Main UI."""

import math
import curses
from pysysmon.asynccb import AsynchroneousCallback

# Why does math.{ceil,floor} not do this?
ceil = lambda x: int(math.ceil(x))
floor = lambda x: int(math.floor(x))

def strip_ansi_codes(s):
    while True:
        e = s.find("\x1b[")
        if e < 0:
            break
        m = s.find("m", e)
        if m < 0:
            raise ValueError("invalid ANSI codes")
        s = s[:e] + s[m + 1:]
    return s

def attr_escape(s):
    return s.replace("%", "%%")

def _cb(self, cbs=()):
    all = bars = services = False
    for cb in cbs:
        if cb():
            if hasattr(cb, "im_self"):
                if cb.im_self in self.bars:
                    self.refresh_bar(cb.im_self)
                    bars = True
                if cb.im_self in self.services:
                    self.refresh_service(cb.im_self)
                    services = True
            else:
                all = True
    if bars or services:
        curses.doupdate()
    if all:
        self.refresh_services()
        self.refresh_bars()
    return True

def called_list(L, *a, **kw):
    r = []
    for i in L:
        v = i
        if callable(i):
            v = i(*a, **kw)
        r.append(v)
    return r

class UI(object):
    def __init__(self, screen, conf):
        self.conf = conf
        self.screen = self._init_screen(screen)
        c = lambda L: called_list(L, self)
        self.bars = c(conf.bars)
        self.services = c(conf.services)
        self.loggers = c(conf.loggers)
        self.recreate_windows()

    def _init_screen(self, s):
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_BLUE, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.init_pair(6, curses.COLOR_CYAN, -1)
        curses.init_pair(7, curses.COLOR_WHITE, -1)
        s.clear()
        s.refresh()
        return s

    def _deinit_screen(self):
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def get_timers(self):
        timers = []
        for o in self.services + self.bars + self.loggers:
            if hasattr(o, "refresh_rate"):
                timers.append((getattr(o, "timer", lambda: True), o.refresh_rate))
        timer_groups = {}
        dev = self.conf.allowed_refresh_dev
        for cb, rr in timers:
            for comp_cb, comp_rr in timers:
                if abs(rr - comp_rr) <= dev:  # Note: adds (cb, rr).
                    timer_groups[cb] = timer_groups.get(cb, []) + [(comp_cb, comp_rr)]
        while timer_groups:
            for k in timer_groups.keys():
                for ck in timer_groups.keys():
                    if k is not ck and any(k is cb for cb, rr in timer_groups[ck]):
                        del timer_groups[ck]
                        break
                else:
                    average_rr = round(float(sum(rr for cb, rr in timer_groups[k])) / len(timer_groups[k]))
                    cbs = [i[0] for i in timer_groups[k]]
                    yield AsynchroneousCallback(_cb, self, cbs=cbs), int(average_rr)
                    del timer_groups[k]
                break

    get_read_watches = lambda s: iter(())

    def get_services_names(self):
        return (s.name for s in self.services)

    def get_bar_names(self):
        return (b.name for b in self.bars)

    def recreate_windows(self):
        bar_lines = ceil(float(len(self.bars)) / self.conf.bars_per_line) + 1
        self.upper_height = upper_height = curses.LINES - bar_lines
        self.service_win_width = service_win_width = max(map(len, self.get_services_names())) + 3
        self.log_win_width = log_win_width = curses.COLS - service_win_width - 1
        self.service_list = curses.newwin(upper_height, service_win_width, 0, 0)
        self.log_view = curses.newwin(upper_height, log_win_width, 0, service_win_width + 1)
        self.bar_view = curses.newwin(bar_lines, curses.COLS, upper_height, 0)
        self.service_list.clear()
        self.log_view.clear()
        self.bar_view.clear()
        self.refresh_services()
        self.refresh_bars()
        self.service_list.refresh()
        self.bar_view.refresh()

    def refresh_services(self):
        map(self.refresh_service, self.services)
        self.service_list.vline(0, self.service_win_width - 1, curses.ACS_VLINE, self.upper_height)
        curses.doupdate()
    
    def refresh_service(self, service):
        if service not in self.services:
            raise ValueError("%r not in services" % service)
        i = self.services.index(service)
        ok = service.ok()
        self.service_list.addch(i, 0, "* "[ok])
        self.service_list.addstr(i, 1, service.name, curses.color_pair(ok + 1))
        self.service_list.noutrefresh()

    def refresh_bars(self):
        self.bar_view.hline(0, 0, curses.ACS_HLINE, curses.COLS)
        self.bar_view.addch(0, self.service_win_width - 1, curses.ACS_SSBS)
        for bar in self.bars:
            self.refresh_bar(bar)
        curses.doupdate()

    def refresh_bar(self, bar):
        if bar not in self.bars:
            raise ValueError("bar %r not in bars" % bar)
        tot_w = curses.COLS
        i = self.bars.index(bar)
        y = i / self.conf.bars_per_line + 1
        column = i % self.conf.bars_per_line
        max_bar_name = max(len(bar.name) for bar in self.bars)

        m = bar.max()
        part = float(min(bar.current(), m)) / m
        bar_len = (tot_w - (max_bar_name + 10) * self.conf.bars_per_line) / self.conf.bars_per_line
        x = tot_w / self.conf.bars_per_line * column
        x_e = x + max_bar_name + 8 + bar_len
        used = ceil(part * bar_len)
        unused = bar_len - used

        self.bar_view.addstr(y, x + max_bar_name - len(bar.name) + 1, bar.name)
        self.bar_view.addstr(y, x + max_bar_name + 2, "%3d%% [" % (part * 100,))
        self.bar_view.hline(y, x + max_bar_name + 8, "=", used)
        self.bar_view.hline(y, x + max_bar_name + 8 + used, " ", unused)
        self.bar_view.addch(y, x_e, "]")
        self.bar_view.refresh()

    def log_split(self, line):
        line = strip_ansi_codes(line)
        pre = "> "
        while line:
            yield pre
            l = line[:self.log_win_width - len(pre) - 1]
            line = line[len(l):]
            yield l + "\n"
            pre = "  "

    def parse_attr(self, line):
        i = 0
        attr = 0
        while True:
            p = line.find("%", i)
            if p < 0:
                break
            i = p + 1
            if i > len(line):
                break  # No exception by intent.
            elif line[i] == "%":
                line = line[:p] + "%" + line[p + 2:]
            elif line[i].isdigit():
                yield attr, line[:p]
                attr = curses.color_pair(int(line[i]))
                line = line[p + 2:]
                i = 0
        yield attr, line

    def log(self, line):
        attr = 0
        for l in self.log_split(line):
            for cattr, l in self.parse_attr(l):
                y, x = self.log_view.getyx()
                if y + 1 >= self.upper_height:
                    self.log_view.move(0, 0)
                    self.log_view.deleteln()
                    self.log_view.move(y - 1, x)
                self.log_view.addstr(l, cattr)
        self.log_view.refresh()

class C:
    class S1:
        __init__ = lambda s, h: None
        ok = lambda s: True
        name = "fucking long"

    class S2:
        __init__ = lambda s, h: None
        ok = lambda s: False
        name = "test-S2"

    class B1:
        __init__ = lambda s, h: None
        current = lambda s: 33
        max = lambda s: 100
        name = "bar1"
    class B2:
        current = lambda s: 33
        max = lambda s: 35
        __init__ = lambda s, h: None
        name = "b2"

    services = S1, S2
    bars = B1, B2

#z=UI(C)
#z.log("%1HH%2EE%3JJ")
#z.log("Dec 23 20:41:45 %%%1%%%0lighty ::ffff:72.36.115.76 GET /robots.txt (56 B) (info: CazoodleBot/CazoodleBot-0.1 (CazoodleBot Crawler; http://www.cazoodle.com/cazoodlebot; cazoodlebot@cazoodle.com))")
#z.log("Dec 23 20:18:04 odin openvpn[22427]: ossian/80.216.226.83:1347 VERIFY OK: depth=1, /C=SE/ST=Stockholms_l_xC3_xA4n/L=Stockholm/O=Ericson/OU=family/CN=Ericson_CA/emailAddress=ludvig.ericson@gmail.com")
#z.log(attr_escape("Dec 23 19:03:53 lighty ::ffff:203.177.21.66 GET "
#"/news/mozilla-thunderbird-abandoned/%2B%2BGET%2Bhttp%3A/news/mozilla-thunderbird-abandoned/%2B%5B0%2C4670%2C4232%5D%2B-%3E%2B//news/mozilla-thunderbird-abandoned/%2B%2BGET%2Bhttp%3A/www.lericson.se/news/mozilla-thunderbird-abandoned/%2B%5B0%2C4670%2C4232%5D%2B-%3E%2B/ "
#"(0 B) (from: "
#"http://www.lericson.se/news/mozilla-thunderbird-abandoned/%2B%2BGET%2Bhttp%3A/www.lericson.se/news/mozilla-thunderbird-abandoned/%2B%5B0%2C4670%2C4232%5D%2B-%3E%2B/) "
#"(info: MSIE 7, Windows)"))
#z.log("hey \x1b[41m:D")
