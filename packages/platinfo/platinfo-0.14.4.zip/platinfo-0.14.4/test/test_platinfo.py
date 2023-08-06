#!/usr/bin/env python
# Copyright (c) 2009 ActiveState Software Inc.

import sys
import os
import unittest
import difflib
import pprint



#----- test cases

class APITestCase(unittest.TestCase):
    def test_version(self):
        import platinfo
        self.assert_(hasattr(platinfo, "__version__"))
        self.assert_(hasattr(platinfo, "__version_info__"))

    def test_class(self):
        from platinfo import PlatInfo
        pi = PlatInfo()
        self.assert_(hasattr(pi, "os"))
        self.assert_(hasattr(pi, "arch"))
        self.assertEqual(pi.name(), "%s-%s" % (pi.os, pi.arch))

    def test_ctor(self):
        from platinfo import PlatInfo
        pi = PlatInfo(os="win32", arch="x86")
        self.assertEqual(pi.name(), "win32-x86")
        
        pi = PlatInfo(os="larry", arch="curly", also="moe")
        self.assertEqual(pi.name("os", "also", "arch"), "larry-moe-curly")



#---- mainline

if __name__ == "__main__":
    runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
    result = runner.run(suite())

