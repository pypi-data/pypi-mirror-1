#!/usr/bin/env python
from __future__ import division

__version__ = "$Revision: 1.1 $"

import new
import os
import sys

from path import path as Path

STDOUT_GLOB="stdout/*"
STDERR_GLOB="stderr/*"
HOSTINFO_DIRPATH=Path("hostinfo")

class DynamicInit(object):
    """
    mix-in class, instantiates on first attribute access

    MUST BE FIRST BASE CLASS USED
    i.e. must appear before the class you want getattribute to use in mro
    """
    def __init__(self, *args, **keywds):
        self.__args = args
        self.__keywds = keywds

    def __getattribute__(self, name):
        _super = super(DynamicInit, self)

        try:
            _super.__init__(*object.__getattribute__(self,
                                                     "_DynamicInit__args"),
                            **object.__getattribute__(self,
                                                      "_DynamicInit__keywds"))
            del self.__args
            del self.__keywds
        except AttributeError:
            pass

        return _super.__getattribute__(name)

def dynamic_init(cls):
    new_cls = new.classobj("dynamic_init(%s.%s)" % (cls.__module__,
                                                    cls.__name__),
                           (DynamicInit, cls), {})
    new_cls.__module__ = __name__
    return new_cls

def filepath_number(filepath):
    return int(filepath.name)

def glob_sorted_numeric(pattern):
    return sorted(Path().glob(pattern), key=filepath_number)

def cat_stdout(stdout):
    for stdout_filepath in glob_sorted_numeric(STDOUT_GLOB):
        stdout.write(file(stdout_filepath).read())

def cat_stderr(stderr):
    for stderr_filepath in glob_sorted_numeric(STDERR_GLOB):
        # XXX workaround python bug:
        # print >>filesubclass does not use filesubclass.write()

        for line in file(stderr_filepath):
            if not line.startswith("DEBUG") and not line.startswith("INFO"):
                break
        else:
            continue

        jobindex = stderr_filepath.name
        hostinfo_filepath = HOSTINFO_DIRPATH / jobindex

        stderr.write("### %s\n" % jobindex)

        try:
            hostinfo_text = file(hostinfo_filepath).read()
        except IOError:
            hostinfo_text = "### no hostinfo available\n"

        stderr.write(hostinfo_text)
        stderr.write(file(stderr_filepath).read())

def arg2output_file(arg):
    if arg == "-":
        return sys.stdout
    else:
        return dynamic_init(file)(Path(arg).expanduser().abspath(), "w")

def parse_options(args):
    from optparse import OptionParser

    global options

    usage = "%prog [POLY-DESTINATION] [STDOUT] [STDERR]"
    version = "%%prog %s" % __version__
    parser = OptionParser(usage=usage, version=version)

    options, args = parser.parse_args(args)

    return args

def main(args):
    args = parse_options(args)

    last_dirpath = Path.getcwd()

    try:
        try:
            stdout = arg2output_file(args[1])
        except IndexError:
            stdout = sys.stdout
        try:
            stderr = arg2output_file(args[2])
        except IndexError:
            stderr = sys.stderr

        try:
            # chdir AFTER using abspath on output files
            Path(args[0]).expanduser().chdir()
        except IndexError:
            pass

        cat_stdout(stdout)
        cat_stderr(stderr)
    finally:
        last_dirpath.chdir()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
