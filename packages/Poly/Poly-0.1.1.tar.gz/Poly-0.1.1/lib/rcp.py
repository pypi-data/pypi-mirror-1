#!/usr/bin/env python
# -*- python -*-
from __future__ import division

__version__ = "$Revision: 1.2 $"

import commands
import itertools
import os
import sys
import time

from path import path as Path

from autolog import autolog
from optbuild import OptionBuilder_ShortOptWithSpace

# XXX: make this less hardcoded for ecs4/ecs2

_log = autolog()

lsf_bin_dirpath = Path(os.environ["LSF_BINDIR"])

LSLOAD_CMDLINE = str(lsf_bin_dirpath / r"""lsload -E -I r1m:r15s:r15m:ut %s | awk '/ok|busy/ { print $0 }' | sed -e "s/*/ /g" | tr -s " " " " | sort -k 3n,6n -k 3,6 | head -n 1""")

LSRCP_PROGRAM = OptionBuilder_ShortOptWithSpace(lsf_bin_dirpath / "lsrcp")

COL_HOST = 0
COL_R1M = 2
COL_R15S = 3

RQUEUE_SOFTMAX = 1.0
RQUEUE_SOFTMAX_STEP = 0.2
RQUEUE_HARDMAX = 2.0

SLEEP_TIMES = dict(soft=5, hard=60)

def sleep(try_index, r1m_str, r15s_str, max_type, rqueue_max):
    sleep_time = SLEEP_TIMES[max_type]

    _log.info("try #%d; r1m=%s; r15s=%s; %s max=%s; retrying in %d s",
              try_index, r1m_str, r15s_str, max_type, rqueue_max, sleep_time)
    time.sleep(sleep_time)

def get_node(nodes_str):
    rqueue_softmax = RQUEUE_SOFTMAX

    for try_index in itertools.count(1):
        # XXX: commands -> optbuild
        line = commands.getoutput(LSLOAD_CMDLINE % nodes_str)
        cols = line.split(" ")

        r1m_str = cols[COL_R1M]
        r15s_str = cols[COL_R15S]

        r1m = float(r1m_str)
        r15s = float(r15s_str)

        if r1m < rqueue_softmax and r15s < rqueue_softmax:
            return cols[COL_HOST]
        elif r1m >= RQUEUE_HARDMAX or r15s >= RQUEUE_HARDMAX:
            sleep(try_index, r1m_str, r15s_str, "hard", RQUEUE_HARDMAX)
        else:
            rqueue_softmax = min(rqueue_softmax+RQUEUE_SOFTMAX_STEP,
                                 RQUEUE_HARDMAX)
            sleep(try_index, r1m_str, r15s_str, "soft", rqueue_softmax)

def node_spec(filename, hostname, envname):
    if filename.startswith(hostname + ":"):
        return get_node(os.environ[envname]) + filename[len(hostname):]
    else:
        return filename

def replace_host(filename):
    filename = node_spec(filename, "ecs2", "ECS2_NODES")
    filename = node_spec(filename, "ecs4", "ECS4_NODES")
    return filename

# enforce right number of args by not using *args
def copy(filename0, filename1):
    filenames = map(replace_host, (filename0, filename1))

    oldpath = os.environ["PATH"]
    try:
        os.environ["PATH"] = "" # no rcp!
        LSRCP_PROGRAM.run(*filenames)
    finally:
        os.environ["PATH"] = oldpath

def main(args):
    copy(*args)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
