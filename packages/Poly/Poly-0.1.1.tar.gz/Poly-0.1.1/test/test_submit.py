#!/usr/bin/env python

__version__ = "$Revision: 1.16 $"

import errno
import os
import sys
import unittest

from poly import submit

class TestPolysub(unittest.TestCase):
    def setUp(self):
        os.environ["POLYWATCH_SLEEP_TIME"] = "2"
        self.jobname_root = "test_polysub_%s_" % os.getpid()

    def test_bsub_failure(self):
        jobname = self.jobname_root + "test_bsub_failure"
        self.assertRaises((OSError, SystemExit), submit.main,
                          ["-J", "%s[4]" % jobname, "-R", "bogusreq",
                           "--", "ls", "/"])

        job_dirpath = submit.get_destination_dirpath() / jobname
        self.assertRaises(OSError, job_dirpath.stat)

    def test_success(self):
        if os.environ.has_key("LSF_ENVDIR"):
            jobname = self.jobname_root + "test_success[1-2]"

            self.assertRaises(SystemExit,
                              submit.main,
                              ["--remove", "-J", jobname, "--", "ls", "/"])

            # wait for polycat to finish before deleting things
            dependency_expr = "done(%s)" % submit.make_polycat_jobname(jobname)
            submit.BSUB_PROGRAM("true", I=True, w=dependency_expr)

            job_dirpath = submit.get_destination_dirpath() / jobname
            job_dirpath.rmtree()

            # this should exist
            (job_dirpath + ".out").remove()

            # this shouldn't exist, should raise error
            self.assertRaises(OSError, (job_dirpath + ".err").remove)

if __name__ == "__main__":
    unittest.main()
