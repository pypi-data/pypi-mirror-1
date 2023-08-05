#!/usr/bin/env python
from os import path

def get_pycpmc_resource(fn):
    return path.join(path.dirname(path.dirname(__file__)), fn)
