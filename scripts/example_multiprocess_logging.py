# -*- coding: utf-8 -*-
"""
Created By: Rowan Temple
Created Date: 03/12/2024

Example use of queued multiprocess logging
"""

import multiprocessing
import sys
import time
from logging import getLogger
from pathlib import Path
from random import randint

sys.path.append(str(Path(__file__).parent.parent))
from pfprocess.logging_utils import default_configurer
from pfprocess.parallel_logging import worker_logger_configurer, log_listener


def worker_process(logger_queue, n):
    worker_logger_configurer(logger_queue)
    time.sleep(randint(1, 4))
    getLogger(__name__).info(f"Worker process {n} done")
    getLogger(__name__).debug(f"Debug level not shown")


if __name__ == "__main__":

    logger_queue = multiprocessing.Queue(-1)
    listener = multiprocessing.Process(
        target=log_listener, args=(logger_queue, default_configurer)
    )
    listener.start()
    workers = []
    for i in range(10):
        worker = multiprocessing.Process(target=worker_process, args=[logger_queue, i])
        workers.append(worker)
        worker.start()
    for w in workers:
        w.join()
    logger_queue.put_nowait(None)
    listener.join()

    print("Done")
