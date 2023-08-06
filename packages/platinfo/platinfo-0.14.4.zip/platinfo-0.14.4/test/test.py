#!/usr/bin/env python
# Copyright (c) 2009 ActiveState Software Inc.

"""The platinfo test suite entry point."""

import os
from os.path import exists, join, dirname, abspath
import sys
import logging
from pprint import pprint

import testlib


log = logging.getLogger("test")
default_tags = ["-knownfailure"]


def setup():
    # Ensure the *development* platinfo.py is tested.
    lib_dir = join(dirname(dirname(abspath(__file__))), "lib")
    sys.path.insert(0, lib_dir)

if __name__ == "__main__":
    retval = testlib.harness(setup_func=setup, default_tags=default_tags)
    sys.exit(retval)

