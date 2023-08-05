#!/usr/bin/env python2.3

__version__ = "$Revision: 1.43 $"

import cPickle
import errno
import exceptions
import itertools
import logging
import os
import popen2
import shutil
import sys
import tempfile
import time
import warnings

import optbuild

from poly import lsf, standalone

SANDBOX_ROOT = "/tmp"
SANDBOX_PREFIX = "poly"
SANDBOX_TMP_DIR = "tmp"
SANDBOX_TMP_PREFIX = "tmp"

IS_FILE_LOCAL_PROGRAM = optbuild.OptionBuilder("is_file_local")

REMOTE_COPY_SLEEP_TIME = 180
REMOTE_COPY_TRIES = 4

### public variables and functions:
__all__ = ["jobid", "jobname,"
           "jobindex", "jobindex_end,"
           "firstjob", "lastjob,"
           "headnode,"
           "localfile", "local", "file_hostname,"
           "copy", "makedirs,"
           "gettempdir", "mkdtemp", "NamedTemporaryFile", "TemporaryFile,"
           "superglobal,"
           "chunk", "substitute",
           "RemoteCopyError", "MultiRemoteCopyErrors"]

### exceptions

class MultiRemoteCopyErrors(exceptions.IOError):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return "; ".join(map(str, self.errors))

### misc helper functions

# XXX: replace with python 2.5 built-in
def _fixargs(func, *create_time_args, **create_time_kwds):
    """
    >>> def f(a, b=2, c=3):
    ...     return (a, b, c)
    >>> f(5)
    (5, 2, 3)
    >>> fa6 = _fixargs(f, 6)
    >>> fa6(4)
    (6, 4, 3)
    >>> fa6(c=99)
    (6, 2, 99)
    >>> fc9 = _fixargs(f, c=9)
    >>> fc9(8, 8)
    (8, 8, 9)
    >>> fc9(8, 8, c=2000)
    (8, 8, 2000)
    """
    def fixed_function(*call_time_args, **call_time_kwds):
        args = create_time_args + call_time_args
        kwds = create_time_kwds.copy()
        kwds.update(call_time_kwds)
        return func(*args, **kwds)
    return fixed_function

def _try_each(exception, *functions):
    for function in functions:
        try:
            return function()
        except exception:
            pass

    raise exception

def _environgetter(name):
    def _environgetter_func():
        return os.environ[name]

    return _environgetter_func

def _strip_final_newline(text):
    if text.endswith("\n"):
        return text[:-1]
    else:
        return text

def makedirs(*args, **keywds):
    "like os.makedirs but doesn't throw an error on EEXIST"
    try:
        os.makedirs(*args, **keywds)
    except OSError, error:
        if error.errno != errno.EEXIST:
            raise

### universal functions

def file_hostname(filename):
    # use >> instead of >>> to avoid doctest
    """
    >> file_hostname("/usr/local")
    None
    >> file_hostname("/nfs/remotehost/remotefile")
    'remotehost'
    """

    try:
        IS_FILE_LOCAL_PROGRAM.getoutput(filename)
        return None # success means it is local
    except optbuild.ReturncodeError, err:
        output = err.output.rstrip()
    except OSError, err:
        if err.errno != errno.ENOENT:
            raise
        output = ""

    if output.endswith("is local"):
        return None
    if output.find("is remote on") != -1 or output.find("is CFS on") != -1:
        return output.split(" ")[-1]
    # and if the output doesn't make sense:
    elif headnode == "localhost":
        return None
    else:
        return headnode

def _remote_copy(src, dst):
    retry_number = 0
    errors = []

    for cmd in itertools.cycle(_localfile_cmds):
        # XXX: set up OptionBuilder at init so you can supply options,
        #      like scp -q
        program = optbuild.OptionBuilder(cmd)
        try:
            program(src, dst)
            return # it worked that's all folks
        except optbuild.ReturncodeError, err:
            errors.append(err)

            if len(errors) >= REMOTE_COPY_TRIES:
                for error_index, error in enumerate(errors):

                    # XXX: autolog
                    print >>sys.stderr, "ERROR %d: %s" % (error_index, error)
                raise MultiRemoteCopyErrors(errors)
            else:
                sleep_time = REMOTE_COPY_SLEEP_TIME * (retry_number+1)
                time.sleep(sleep_time)
    else:
        raise exceptions.OSError, "no remote copy program specified"

def _remote_copy_arg(filename):
    host = file_hostname(os.path.dirname(filename))
    if host:
        return "%s:%s" % (host, filename), True
    else:
        return filename, False

def copy(*filenames):
    """
    copy a file using the appropriate command
    """
    remote_copy_args, remote = zip(*map(_remote_copy_arg,
                                        map(os.path.abspath, filenames)))
    if True in remote:
        _remote_copy(*remote_copy_args)
    else:
        shutil.copy(*filenames)

def localfile(filename, mode="r", *args, **keywds):
    return file(local(filename, mode=mode), mode, *args, **keywds)

def superglobal(name, function, *args, **keywds):
    try:
        res = _superglobals[name]
    except KeyError:
        res = function(*args, **keywds)
        _superglobals[name] = res

    return res

def chunk(collection):
    global _already_chunked

    if _already_chunked:
        warnings.warn("poly.chunk() called earlier in this process -- refusing"
                      " to chunk further", RuntimeWarning, stacklevel=2)
        return collection

    _already_chunked = True
    _write_superglobals()
    return _chunk(collection)

def substitute(text):
    if jobid:
        text = text.replace("%J", str(jobid))
    if jobindex:
        text = text.replace("%I", str(jobindex))

    return text

### environment-specific variables and functions

def _init_superglobal_load_true():
    # XXX: remove this debugging info
    # use autolog if you need it
    # import traceback
    #
    # print >>sys.stderr, "poly._init_superglobal_load_true() called"
    # traceback.print_stack(file=sys.stderr)

    picklefile = localfile(os.environ["POLY_SUPERGLOBAL_LOAD"], "rb")

    return cPickle.load(picklefile)

def _init_superglobal_load_false():
    return {}

def _init_superglobal_save_true():
    _superglobal_filename = os.environ["POLY_SUPERGLOBAL_SAVE"]

    firstjob = False
    lastjob = False

    def _write_superglobals():
        # write superglobals, then exit
        temp_file = NamedTemporaryFile(mode="wb")
        cPickle.dump(_superglobals, temp_file, cPickle.HIGHEST_PROTOCOL)
        temp_file.flush() # don't close yet!

        copy(temp_file.name, _superglobal_filename)

        del temp_file
        sys.exit(0)

    return firstjob, lastjob, _write_superglobals

def _init_superglobal_save_false():
    def _write_superglobals():
        pass

    return firstjob, lastjob, _write_superglobals

# XXX: replace with autolog
def _init_logging():
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

def _init_localfile_cmds(default):
    def _get_env_poly_localfile_cmds():
        return os.environ["POLY_LOCALFILE_CMDS"].split(" ")

    def _get_default():
        return default

    return _try_each(KeyError,
                     _get_env_poly_localfile_cmds,
                     _get_default)

def _init_groupindex():
    try:
        groupindex = int(os.environ["POLY_GROUPINDEX"])
    except KeyError:
        groupindex = None

    try:
        groupindex_end = int(os.environ["POLY_GROUPINDEX_END"])
    except KeyError:
        groupindex_end = None

    return groupindex, groupindex_end

### run init functions

_init_logging()

headnode = _try_each(KeyError,
                     _environgetter("POLY_STORAGE_HOST"),
                     lsf._init_headnode,
                     standalone._init_headnode)

groupindex, groupindex_end = _init_groupindex()

(jobindex,
 jobindex_end,
 firstjob,
 lastjob,
 _chunk) = _try_each(KeyError,
                     lsf._init_job_array,
                     standalone._init_job_array)

(jobid,
 jobname,
 local,
 gettempdir,
 NamedTemporaryFile,
 TemporaryFile,
 _localfile_cmds) = _try_each(KeyError,
                              lsf._init_job,
                              standalone._init_job)

_superglobals = _try_each(KeyError,
                          _init_superglobal_load_true,
                          _init_superglobal_load_false)

firstjob, lastjob, _write_superglobals = \
          _try_each(KeyError,
                    _init_superglobal_save_true,
                    _init_superglobal_save_false) # must be last

localfilename = local # deprecated alias

_already_chunked = False

### universal functions relying on init functions

mkdtemp = _fixargs(tempfile.mkdtemp, dir=gettempdir())
