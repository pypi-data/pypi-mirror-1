"""Lighttpd access log parser"""

import re
from time import sleep, strptime, strftime
from collections import defaultdict
from pysysmon.utils import readable_size
from pysysmon.loggers.tail import Tail
from pysysmon.ui import attr_escape

line_re = re.compile(r'^([^ ]+) ([^ ]+) ([^ ]+) \[([^\]]+)\] "([A-Z]+) ([^ ]+) ([^"]+)" (\d+) (\d+|\-) "(\-|[^"]+)" "([^"]+)"')
time_re = re.compile(r"^(..)/(...)/(....):(........)")

class LighttpdLog(Tail):
    default_colors = defaultdict(lambda: 9, {"green": 2, "yellow": 3, "red": 1,})
    max_omissions = 5

    user_agents = ("Firefox", "BonEcho", "Opera", "MSIE 5", "MSIE 6",
        "MSIE 7", "MSIE", "Safari", "wget", "Camino")
    os_names = ("Linux", "Windows", "FreeBSD", "Macintosh", "Googlebot")

    def __init__(self, filename, colors={}):
        super(LighttpdLog, self).__init__(filename)
        self.colors = self.default_colors.copy()
        self.colors.update(colors)
        self.last_ip = None
        self.prints_omitted = 0

    def handle(self, line):
        mo = line_re.search(line)
        if mo:
            line = self.get_formatted(*mo.groups())
        self.log(line)

    def get_formatted(self, ip, http_host, user, timestamp, verb, path,
            httpver, statuscode, length, referrer, useragent):
        # Get status color of line.
        color = "default"
        if statuscode.startswith("2"):
            color = "green"  # 200 OK, e.g.
        elif statuscode.startswith("3"):
            color = "yellow"
        elif statuscode.startswith("4") or statuscode.startswith("5"):
            color = "red"
        # Get printed IP address.
        print_ip = ip
        if ip == self.last_ip:
            print_ip = " " * len(print_ip)
            self.prints_omitted += 1
            if self.prints_omitted > self.max_omissions:
                self.prints_omitted = 0
                print_ip = ip
        self.last_ip = ip
        # Format HTTP host
        if http_host == "-":
            http_host = ""
        else:
            http_host = " %s" % (http_host,)
        # Length
        print_length = length
        if length != "-":
            if length == "0":
                print_length = "0 B"
            else:
                print_length = readable_size(length)
        print_length = " %s " % print_length
        # Get timestamp.
        ts_mo = time_re.match(timestamp)
        print_ts = timestamp
        if ts_mo:
            day, month, year, time = ts_mo.groups()
            day = "%2d" % int(day)
            print_ts = " ".join((month, day, time))
        # Get additional info.
        addit = []
        if user != "-":
            addit.append("user: %s" % attr_escape(user))
        if referrer != "-":
            addit.append("ref: %s" % attr_escape(referrer))
        # Like rudimentary heuristics for UA name and OS name.
        if useragent != "-":
            matched_uas = []
            for ua in self.user_agents:
                if ua in useragent:
                    matched_uas.append(ua)
            matched_os = []
            for os in self.os_names:
                if os in useragent:
                    matched_os.append(os)
            if matched_uas:
                addit.append("agent: " + attr_escape(", ".join(matched_uas)))
            else:
                addit.append("agent?: " + attr_escape(useragent))
            if matched_os:
                addit.append("os: " + attr_escape(", ".join(matched_os)))
        # Nicely format addit.
        print_addit = ""
        if addit:
            print_addit = "(%s)" % (", ".join(addit),)
        # Then return the whole line
        return "%s lighty %s%s %s %%%d%s%%0%s%s" % (print_ts,
            print_ip, attr_escape(http_host), attr_escape(verb),
            self.colors[color], attr_escape(path), print_length, print_addit)
