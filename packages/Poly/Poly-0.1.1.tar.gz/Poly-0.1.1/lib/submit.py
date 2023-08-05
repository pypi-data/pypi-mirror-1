#!/usr/bin/env python
from __future__ import division

__version__ = "$Revision: 1.8 $"

"""
This is intimately bound up with Platform LSF/bsub.
"""

import errno
import os
import subprocess
import sys

from path import path

from autolog import autolog
import optbuild

import poly
import poly.watch

_log = autolog()

POLYJOB_CMD = "polyjob"

POLYCAT_JOBNAME = "polycat_%s"
DEFAULT_DIRNAME = "polydata"

SUPERGLOBAL_FILENAME = "superglobals.pickle"

OUT_EXT = "out"
ERR_EXT = "err"

JOB_SLOT_LIMIT_INIT = 1

class BsubOptionBuilder(optbuild.OptionBuilder_ShortOptWithSpace):
    def getoutput(self, *args, **kwargs):
        try:
            stdout, stderr = self.getoutput_error(*args, **kwargs)

            if stderr:
                print >>sys.stderr, stderr

            return stdout

        except optbuild.ReturncodeError, err:
            print err.output
            print >>sys.stderr, err.error

            _log.die("bsub failed with status %d", err.returncode)

BSUB_PROGRAM = BsubOptionBuilder("bsub")

def bsub_polycat(jobid, jobname, job_dirpath):
    return BSUB_PROGRAM.getoutput("polycat",
                                  job_dirpath,
                                  options.stdout_filename,
                                  options.stderr_filename,
                                  q="small",
                                  w="ended(%s)" % jobid,
                                  J=make_polycat_jobname(jobname))

def make_polycat_jobname(jobname):
    return jobname.replace("[", "_").replace("]", "_") + "polycat"

def get_current_host():
    import socket

    return socket.gethostname()

def get_destination_host():
    return poly._try_each(KeyError,
                          poly._environgetter("POLY_STORAGE_HOST"),
                          poly._environgetter("HOSTNAME"),
                          get_current_host)

def get_destination_dirpath():
    try:
        destination = os.environ["POLY_DESTINATION"]
        destination_split = destination.split(":")
        if len(destination_split) != 2:
            _log.die("Environment variable POLY_DESTINATION "
                     "must contain only one colon")

        # assumes destination_dirname is available from submitting host,
        # but its parents will be created if it is not
        res = path(destination_split[1])
    except KeyError:
        home_dirpath = path(os.environ["HOME"])
        res = home_dirpath / DEFAULT_DIRNAME
        destination = "%s:%s" % (get_destination_host(), res)
        os.environ["POLY_DESTINATION"] = destination

    return res

def process_bsub_args(bsub_args):
    try:
        program_cmdline = bsub_args[bsub_args.index("--")+1:]
        bsub_args[bsub_args.index("--")] = POLYJOB_CMD
        return bsub_args, program_cmdline
    except ValueError:
        _log.die("job specification did not include --")

def set_bash_env():
    # if you don't want it, set it to " " or /dev/null
    if not os.environ.has_key("BASH_ENV"):
        os.environ["BASH_ENV"] = "~/.bashrc"

def normalize_stdout_filename(job_dirpath):
    if options.stdout_filename is None:
        options.stdout_filename = os.extsep.join([job_dirpath, OUT_EXT])
    elif options.stdout_filename == "":
        options.stdout_filename = "/dev/null"

def normalize_stderr_filename():
    if options.stderr_filename is None:
        if options.stdout_filename.endswith(os.extsep + OUT_EXT):
            stdout_basename = options.stdout_filename[:-len(OUT_EXT)-1]
        else:
            stdout_basename = options.stdout_filename
        options.stderr_filename = os.extsep.join([stdout_basename, ERR_EXT])
    elif options.stderr_filename == "":
        options.stderr_filename = "/dev/null"

def remove_job_files(job_dirpath):
    try:
        job_dirpath.rmtree()
    except OSError:
        pass

    for filename in options.stdout_filename, options.stderr_filename:
        try:
            os.remove(filename)
        except OSError:
            pass

def make_job_dirs(job_dirpath):
    for dirname in ["hostinfo", "stdout", "stderr", "tar"]:
        dirpath = job_dirpath / dirname
        try:
            dirpath.makedirs()
        except OSError, err:
            if err.errno == errno.EEXIST:
                _log.die("destination store %s already exists; "
                         "use %s --remove to remove it", dirpath, sys.argv[0])
            else:
                _log.die("can't create destination store %s: %s",
                         dirpath, err.strerror)

def make_superglobals(program_cmdline, job_dirpath):
    _log[".make_superglobals"].debug("start")
    superglobal_filename = job_dirpath / SUPERGLOBAL_FILENAME

    os.environ["POLY_SUPERGLOBAL_SAVE"] = superglobal_filename
    returncode = subprocess.call(program_cmdline, env=os.environ)

    if returncode:
        _log.die("%s failed with return code %s",
                 program_cmdline[0], returncode)

    del os.environ["POLY_SUPERGLOBAL_SAVE"]
    os.environ["POLY_SUPERGLOBAL_LOAD"] = superglobal_filename
    _log[".make_suberglobals"].debug("end")

def polysub(bsub_args):
    _log[".polysub"].debug("start")
    destination_dirpath = get_destination_dirpath()

    bsub_args, program_cmdline = process_bsub_args(bsub_args)

    use_polywatch = os.environ.has_key("POLYWATCH_HOSTS")

    # set job slot limit, don't use polywatch if it's already set
    try:
        args_index_jobname = bsub_args.index("-J")+1
        jobname = bsub_args[args_index_jobname]

        if use_polywatch:
            try: # job slot specified; fix jobname
                jobname = jobname[:jobname.index("%")]
                use_polywatch = False
            except ValueError: # job slot limit not specified; fix bsub arg
                bsub_jobname = jobname + "%%%d" % JOB_SLOT_LIMIT_INIT
                bsub_args[args_index_jobname] = bsub_jobname

    except ValueError:
        _log.die("job specification did not include -J jobname")

    set_bash_env()

    job_dirpath = destination_dirpath / jobname

    normalize_stdout_filename(job_dirpath)
    normalize_stderr_filename()

    if options.remove:
        remove_job_files(job_dirpath)

    if not options.no_makedirs:
        make_job_dirs(job_dirpath)

    try:
        if options.superglobal:
            make_superglobals(program_cmdline, job_dirpath)

        bsub_output = BSUB_PROGRAM.getoutput(*bsub_args)
    except:
        if not options.no_makedirs:
            remove_job_files(job_dirpath)
        raise

    print "Main", bsub_output,
    jobid = bsub_output[bsub_output.index("<")+1:bsub_output.index(">")]

    print "Summary", bsub_polycat(jobid, jobname, job_dirpath),

    sys.stdout.flush()
    if use_polywatch:
        poly.watch.main([str(jobid)])

def parse_options(args):
    from optparse import OptionParser

    global options

    long_args = []
    bsub_args = []

    for index, arg in enumerate(args):
        if not arg.startswith("--") or arg == "--":
            long_args = args[:index]
            bsub_args.extend(args[index:])
            break
    else:
        long_args = args


    usage = "%prog [POLYSUB-OPTION]... " \
            "-J JOBNAME [BSUB-OPTION]... " \
            "-- COMMAND [COMMAND-ARG]..."
    version = "%%prog %s" % __version__
    parser = OptionParser(usage=usage, version=version)
    parser.add_option("", "--output", dest="stdout_filename", default=None,
                      help="write standard output to FILE", metavar="FILE")
    parser.add_option("", "--error", dest="stderr_filename", default=None,
                      help="write standard error to FILE", metavar="FILE")
    parser.add_option("", "--superglobal", action="store_true",
                      help="generate superglobals interactively "
                      "before submitting batch job array")
    parser.add_option("", "--remove", action="store_true",
                      help="remove existing desination files before running")
    parser.add_option("", "--no-makedirs", action="store_true",
                      help="do not make job directories")

    options, long_args = parser.parse_args(long_args)

    assert not long_args
    return bsub_args

def main(args):
    bsub_args = parse_options(args)

    return polysub(bsub_args)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
