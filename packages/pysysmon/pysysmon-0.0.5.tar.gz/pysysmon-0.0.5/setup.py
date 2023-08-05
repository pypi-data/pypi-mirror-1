#!/usr/bin/env python
from distutils.core import setup

setup(name="pysysmon", version="0.0.5",
    url="http://lericson.se/",
    author="Ludvig Ericson", author_email="ludvig@lericson.se",
    description="A curses-based system monitor.",
    packages=["pysysmon", "pysysmon.readers", "pysysmon.services",
        "pysysmon.bars", "pysysmon.loggers"], scripts=["pysysmon/pysysmon"],
    package_data={"pysysmon": ["pysysmon_conf.py.example"]})
