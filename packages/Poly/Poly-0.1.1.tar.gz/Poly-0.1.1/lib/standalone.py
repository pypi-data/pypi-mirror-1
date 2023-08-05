#!/usr/bin/env python2.3

__version__ = "$Revision: 1.3 $"

import tempfile

import poly

def _init_job_array():
    jobindex = None
    jobindex_end = None
    firstjob = True
    lastjob = True

    def _chunk(collection):
        return collection

    return jobindex, jobindex_end, firstjob, lastjob, _chunk

def _init_job():
    jobid = None
    jobname = None

    def local(filename, mode="r", host=poly.headnode, force=False):
        # imitate for better error-checking
        return filename

    gettempdir = tempfile.gettempdir
    # XXX: replace with Py2.5 partial
    NamedTemporaryFile = poly._fixargs(tempfile.NamedTemporaryFile,
                                       suffix=".poly")
    TemporaryFile = tempfile.TemporaryFile

    _localfile_cmds = poly._init_localfile_cmds(default=["scp"])

    return (jobid, jobname, local, gettempdir,
            NamedTemporaryFile, TemporaryFile, _localfile_cmds)

def _init_headnode():
    return "localhost"
