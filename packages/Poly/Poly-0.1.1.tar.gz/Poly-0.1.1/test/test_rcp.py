#!/usr/bin/env python

__version__ = "$Revision: 1.1 $"

import tempfile
import unittest

from poly import rcp

class TestRcp(unittest.TestCase):
    def test_remote_file(self):
        local_tempfile = tempfile.NamedTemporaryFile()
        local_tempfile.close()

        rcp.main(["/nfs/acari/mh5/.bashrc", local_tempfile.name])

if __name__ == "__main__":
    unittest.main()
