#!/usr/bin/env python

from pycpmc.words import *
from pycpmc.ui import *
from pycpmc.utils import get_pycpmc_resource

# get_pycpmc_resource just locates in which directory pycpmc is installed and
# joins the given filename with that directory.
source = LinedFileSource(get_pycpmc_resource("sentences.txt"))
ui = TerminalUI  # No call.
