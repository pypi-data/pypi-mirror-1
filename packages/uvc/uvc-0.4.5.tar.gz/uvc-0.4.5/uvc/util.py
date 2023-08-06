"""Utility functions used by uvc."""

import os
from subprocess import PIPE, STDOUT
from subprocess import Popen as StdPopen

from uvc.killableprocess import Popen

def run_in_directory(working_dir, command_line, timeout=-1, output=None):
    # use the standard Popen so that we don't have
    # threading issues if there is a threaded
    # server in front
    if timeout == -1 or timeout is None:
        p = StdPopen(command_line, stdout=PIPE, stderr=STDOUT, cwd=working_dir)
    else:
        p = Popen(command_line, stdout=PIPE, stderr=STDOUT, cwd=working_dir)
    while True:
        o = p.stdout.readline()
        if o == '' and p.poll() != None:
            break
        output.write(o)

    output.return_code = p.returncode
