#!/usr/bin/env python
from distutils.core import setup

setup(name="pycpmc", version="0.1.1", url="http://lericson.se/",
    author="Ludvig Ericson", author_email="ludvig@lericson.se",
    description="A curses-based CPM calculator.", packages=["pycpmc", "pycpmc.utils"],
    scripts=["pycpmc/utils/pycpmc"], package_data={"pycpmc": ["sentences.txt"]})
