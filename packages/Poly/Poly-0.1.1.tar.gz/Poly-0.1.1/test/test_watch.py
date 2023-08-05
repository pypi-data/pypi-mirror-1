#!/usr/bin/env python

__version__ = "$Revision: 1.4 $"

import os
import unittest

from poly import watch

class TestMain(unittest.TestCase):
    def setUp(self):
        os.environ["POLYWATCH_SLEEP_TIME"] = "0"

    def test_help(self):
        self.assertRaises(SystemExit, watch.main, ["--help"])

if __name__ == "__main__":
    unittest.main()
