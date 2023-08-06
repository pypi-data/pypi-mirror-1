"""Utility functions used by uvc."""

import os
from subprocess import PIPE, STDOUT

from uvc.killableprocess import Popen

def run_in_directory(working_dir, command_line, timeout=-1):
    current_dir = os.getcwd()
    os.chdir(working_dir)
    try:
        p = Popen(command_line, 
                    stdout=PIPE, stderr=STDOUT)
        p.wait(timeout=timeout)
    finally:
        os.chdir(current_dir)
    
    return [p.returncode, p.stdout]
    