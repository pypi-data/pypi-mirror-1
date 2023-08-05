#!/usr/bin/env python

__version__ = "$Revision: 1.1 $"

import unittest

from poly import watch

class TestMain(unittest.TestCase):
    def test_help(self):
        self.assertRaises(SystemExit, watch.main, ["--help"])

if __name__ == "__main__":
    unittest.main()
