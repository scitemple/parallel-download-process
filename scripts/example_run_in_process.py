# -*- coding: utf-8 -*-
"""
Example of using run_in_process to run a target function in a spawned process

This a serial (not parallel) pattern. It may be useful for processing files where it's
important to silo the proccessing well, e.g. for opening files where
it's difficult to close all the references
"""

import sys
import time
from logging import getLogger
from pathlib import Path
from random import randint

sys.path.append(str(Path(__file__).parent.parent))
from pfprocess.run_in_process import run_in_process


def target(n):
    time.sleep(randint(1, 4))

    # Show logger working from within target
    getLogger(__name__).info(f"Target {n} done")


if __name__ == "__main__":
    # note these run in serial, target is awaited before next is run
    run_in_process(target, args=[1])
    run_in_process(target, args=[2])
    print("Done")
