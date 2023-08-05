#!/usr/bin/env python2.3

__version__ = "$Revision: 1.12 $"

import exceptions
import tempfile
import os
import warnings

import poly

# XXX: os.path -> path.path as Path

LOCALFILE_CMDS = ["polyrcp", "lsrcp", "scp", "rcp"]

def _init_job_array():
    from poly import groupindex, groupindex_end

    jobindex = int(os.environ["LSB_JOBINDEX"])
    jobindex_end = int(os.environ["LSB_JOBINDEX_END"])

    firstjob = (jobindex == 1)
    lastjob = (jobindex == jobindex_end)

    # XXX: there is too much copying going on here
    def _chunk_start(index, index_end, collection):
        return ((index-1)*len(collection))/index_end

    def _chunk(collection):
        if groupindex and groupindex_end:
            group_start = _chunk_start(groupindex, groupindex_end, collection)
            group_end = _chunk_start(groupindex+1, groupindex_end, collection)
            collection = collection[group_start:group_end]

        array_start = _chunk_start(jobindex, jobindex_end, collection)
        array_end = _chunk_start(jobindex+1, jobindex_end, collection)
        return collection[array_start:array_end]

    return jobindex, jobindex_end, firstjob, lastjob, _chunk

def _init_job():
    jobid = int(os.environ["LSB_JOBID"])
    jobname = os.environ["LSB_JOBNAME"]

    try:
        _sandbox = os.path.join(poly.SANDBOX_ROOT,
                                "%s-%s.%s.%d" % (poly.SANDBOX_PREFIX,
                                                 os.environ["LSFUSER"],
                                                 jobid,
                                                 poly.jobindex))
    except TypeError:
        _sandbox = os.path.join(poly.SANDBOX_ROOT,
                                "%s-%s.%s" % (poly.SANDBOX_PREFIX,
                                                 os.environ["LSFUSER"],
                                                 jobid))

    _sandbox_tempdir = os.path.join(_sandbox, poly.SANDBOX_TMP_DIR)
    _sandbox_tmp_prefix = os.path.join(_sandbox_tempdir, poly.SANDBOX_TMP_PREFIX)

    poly.makedirs(os.path.join(_sandbox_tempdir))

    def _local_force(localname, filename, host):
        localdir = os.path.dirname(localname)
        poly.makedirs(localdir)
        poly._remote_copy("%s:%s" % (host, filename), localname)

    def local(filename, mode="r", host=None, force=False):
        """
        force: forces the file to be retrieved again, missing the cache
        """
        if filename is None:
            raise exceptions.TypeError, "filename is None"

        if "w" in mode or "+" in mode or "a" in mode:
            raise exceptions.NotImplementedError
        mode_dir = "r"
        filename = os.path.abspath(filename)

        if filename.startswith(_sandbox):
            message = ("filename %s starts with local sandbox directory %s"
                       "-- not retrieving remote copy") % (filename, _sandbox)
            warnings.warn(message, RuntimeWarning, stacklevel=2)
            return filename

        if not host:
            host = poly.file_hostname(filename)
        if not host: # still
            return filename

        localname = os.path.join(_sandbox, mode_dir, filename[1:])

        if force or not os.path.exists(localname):
            _local_force(localname, filename, host)

        return localname

    def gettempdir():
        return _sandbox_tempdir

    NamedTemporaryFile = poly._fixargs(tempfile.NamedTemporaryFile,
                                       prefix=_sandbox_tmp_prefix,
                                       suffix=".poly")

    TemporaryFile = poly._fixargs(tempfile.TemporaryFile,
                                  prefix=_sandbox_tmp_prefix)

    _localfile_cmds = poly._init_localfile_cmds(LOCALFILE_CMDS)

    # XXX: this is ridiculous, should be a dict
    return (jobid, jobname, local, gettempdir,
            NamedTemporaryFile, TemporaryFile, _localfile_cmds)

def _init_headnode():
    return os.environ["LSB_SUB_HOST"]
