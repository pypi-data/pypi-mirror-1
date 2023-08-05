#!/usr/bin/env python

### XXX: this code needs to be refactored into a more streamlined system

__version__ = "$Revision: 1.5 $"

import exceptions
import os
import random
import stat
import sys
import tempfile
import unittest
import warnings

import poly

os.environ["POLY_LOCALFILE_CMDS"] = "scp"

def clear_environ():
    for key in ["LSB_JOBID", "LSB_JOBINDEX",
                "LSB_JOBINDEX_END", "LSB_JOBNAME",
                "LSFUSER", "LSF_HEADNODE", "POLY_STORAGE_HOST"]:
        try:
            del os.environ[key]
        except KeyError:
            pass

def cleanup():
    os.system("for X in /tmp/poly-polytester*; do rm -r $X; done")

class TestPolyStandAlone(unittest.TestCase):
    def setUp(self):
        clear_environ()
        reload(poly)

    def test_jobid(self):
        self.assertEqual(poly.jobid, None)

    def test_jobindex(self):
        self.assertEqual(poly.jobindex, None)

    def test_jobindex_end(self):
        self.assertEqual(poly.jobindex_end, None)

    def test_jobname(self):
        self.assertEqual(poly.jobname, None)

    def test_chunk(self):
        ra = range(random.randrange(1, 9999))
        self.assertEqual(poly.chunk(ra), ra)

    def test_localfilename(self):
        fn = "/etc/hosts"
        self.assertEqual(fn, poly.localfilename(fn))

    def test_NamedTemporaryFile(self):
        tmpf = poly.NamedTemporaryFile()

    def test_TemporaryFile(self):
        tmpf = poly.TemporaryFile()

    def test_firstjob(self):
        self.assert_(poly.firstjob)

    def test_lastjob(self):
        self.assert_(poly.lastjob)

    def test_localfile(self):
        fh = poly.localfile("/etc/hosts")
        a = 0
        for line in fh:
            a += 1
        self.assert_(a >= 1)

class TestPolyHeadNode(unittest.TestCase):
    def testNoSetting(self):
        clear_environ()
        self.assertEqual(poly.headnode, "localhost")

    def testSetting(self):
        os.environ["POLY_STORAGE_HOST"] = "barbecueworld"

        reload(poly)
        self.assertEqual(poly.headnode, "barbecueworld")

class TestPolyJobArray(unittest.TestCase):
    def setUp(self):
        clear_environ()

        os.environ["LSB_JOBID"] = "78942384"
        os.environ["LSB_JOBINDEX"] = "5"
        os.environ["LSB_JOBINDEX_END"] = "6"
        os.environ["LSB_JOBNAME"] = "testjob"
        os.environ["LSFUSER"] = "polytester"

        reload(poly)

    def test_makedirs(self):
        poly.makedirs("/tmp/poly-polytester.78942384.99")
        poly.makedirs("/tmp/poly-polytester.78942384.99/44")
        poly.makedirs("/tmp/poly-polytester.78942384.99")
        poly.makedirs("/tmp/poly-polytester.78942384.99/44")
        past_dir = os.getcwd()
        os.chdir("/tmp/poly-polytester.78942384.99/44")
        os.chdir(past_dir)

    def test_jobid(self):
        self.assertEqual(poly.jobid, 78942384)

    def test_jobindex(self):
        self.assertEqual(poly.jobindex, 5)

    def test_jobindex_end(self):
        self.assertEqual(poly.jobindex_end, 6)

    def test_jobname(self):
        self.assertEqual(poly.jobname, "testjob")

    def test_localfilename(self):
        fn = "/etc/hosts"
        try:
            self.assertEqual("/tmp/poly-polytester.78942384.5/r/etc/hosts", poly.localfilename(fn, host=poly.headnode))
        except IOError, err:
            try:
                traceback = sys.exc_info()[2]
                if err.args[0] == "lsrcp not found":
                    warnings.warn("lsrcp not found", RuntimeWarning)
                    return
                else:
                    raise
            except:
                raise err, None, traceback
        self.assertEqual(os.system("scp %s:/etc/hosts /tmp/poly-polytester.78942384.5/r/etc/hosts2" % poly.headnode), 0)
        self.assertEqual(os.system("diff /tmp/poly-polytester.78942384.5/r/etc/hosts /tmp/poly-polytester.78942384.5/r/etc/hosts2"), 0)

        st1 = os.stat(poly.localfilename(fn, host=poly.headnode))
        st2 = os.stat(poly.localfilename(fn, host=poly.headnode))
        self.assertEqual(st1[stat.ST_MTIME], st2[stat.ST_MTIME])

        st3 = os.stat(poly.localfilename(fn, host=poly.headnode, force=True))
        self.assertEqual(st1[stat.ST_SIZE], st3[stat.ST_SIZE])

        past_dir = os.getcwd()
        os.chdir("/usr/bin")
        self.assertEqual("/tmp/poly-polytester.78942384.5/r/usr/bin/env", poly.localfilename("env", host=poly.headnode))
        os.chdir(past_dir)

    def test_NamedTemporaryFile(self):
        tmpf = poly.NamedTemporaryFile()
        self.assert_(tmpf.name.startswith("/tmp/poly-polytester.78942384.5/tmp/tmp"))

    def test_TemporaryFile(self):
        tmpf = poly.TemporaryFile()

    def test_firstjob(self):
        self.failIf(poly.firstjob)

    def test_lastjob(self):
        self.failIf(poly.lastjob)

    def test_localfile(self):
        fh = poly.localfile("/etc/hosts")
        a = 0
        for line in fh:
            a += 1
        self.assert_(a >= 1)

class TestPolyJobArrayWithSlashesLastJob(unittest.TestCase):
    def setUp(self):
        clear_environ()

        os.environ["LSB_JOBID"] = "42"
        os.environ["LSB_JOBINDEX"] = "7"
        os.environ["LSB_JOBINDEX_END"] = "7"
        os.environ["LSB_JOBNAME"] = "testjobs/testjob/bigtest"
        os.environ["LSFUSER"] = "polytester"

        reload(poly)

    def test_jobid(self):
        self.assertEqual(poly.jobid, 42)

    def test_jobindex(self):
        self.assertEqual(poly.jobindex, 7)

    def test_jobindex_end(self):
        self.assertEqual(poly.jobindex_end, 7)

    def test_jobname(self):
        self.assertEqual(poly.jobname, "testjobs/testjob/bigtest")

    def test_localfilename(self):
        fn = "/etc/hosts"
        try:
            self.assertEqual("/tmp/poly-polytester.42.7/r/etc/hosts", poly.localfilename(fn, host=poly.headnode))
        except IOError, err:
            try:
                traceback = sys.exc_info()[2]
                if err.args[0] == "lsrcp not found":
                    warnings.warn("lsrcp not found", RuntimeWarning)
                    return
                else:
                    raise
            except:
                raise err, None, traceback
        self.assertEqual(os.system("scp %s:/etc/hosts /tmp/poly-polytester.42.7/r/etc/hosts2" % poly.headnode), 0)
        self.assertEqual(os.system("diff /tmp/poly-polytester.42.7/r/etc/hosts /tmp/poly-polytester.42.7/r/etc/hosts2"), 0)

        st1 = os.stat(poly.localfilename(fn, host=poly.headnode))
        st2 = os.stat(poly.localfilename(fn, host=poly.headnode))
        self.assertEqual(st1[stat.ST_MTIME], st2[stat.ST_MTIME])

        st3 = os.stat(poly.localfilename(fn, host=poly.headnode, force=True))
        self.assertEqual(st1[stat.ST_SIZE], st3[stat.ST_SIZE])

        past_dir = os.getcwd()
        os.chdir("/usr/bin")
        self.assertEqual("/tmp/poly-polytester.42.7/r/usr/bin/env", poly.localfilename("env", host=poly.headnode))
        os.chdir(past_dir)

    def test_NamedTemporaryFile(self):
        tmpf = poly.NamedTemporaryFile()
        self.assert_(tmpf.name.startswith("/tmp/poly-polytester.42.7/tmp/tmp"))

    def test_TemporaryFile(self):
        tmpf = poly.TemporaryFile()

    def test_firstjob(self):
        self.failIf(poly.firstjob)

    def test_lastjob(self):
        self.assert_(poly.lastjob)

    def test_localfile(self):
        fh = poly.localfile("/etc/hosts")
        a = 0
        for line in fh:
            a += 1
        self.assert_(a >= 1)

class TestPolyChunker(unittest.TestCase):
    def test_chunk(self):
        clear_environ()

        os.environ["LSB_JOBID"] = "78942384"
        os.environ["LSB_JOBNAME"] = "78942384"
        os.environ["LSFUSER"] = "polytester"

        ji_end = random.randrange(2, 99)
        test_range = range(random.randrange(1, 99))
        os.environ["LSB_JOBINDEX_END"] = str(ji_end)

        cmp_range = []
        for ji in range(1, ji_end+1):
            os.environ["LSB_JOBINDEX"] = str(ji)
            reload(poly)

            cmp_range.extend(poly.chunk(test_range))

        self.assertEquals(test_range, cmp_range)

class TestZZZZZZZZZ(unittest.TestCase):
    """
    make sure cleanup is done last
    """
    def test_zzzzzz(self):
        cleanup()

def main():
    try:
        unittest.main(testRunner=unittest.TextTestRunner(verbosity=2))
    finally:
        cleanup()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
