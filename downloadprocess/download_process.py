# -*- coding: utf-8 -*-
"""
Download process
"""

import os
import sys
from multiprocessing import Queue, Process
from pathlib import Path

from downloadprocess.logging_utils import default_configurer

sys.path.append(str(Path(__file__).parent))
from downloadprocess.multithread_logging import log_listener


def download_process(
    urls,
    processor,
    n_downloaders=None,
    n_processors=None,
    save_dp=None,
    args=None,
    kwargs=None,
):
    # work in progress
    raise NotImplementedError

    n_downloaders = n_downloaders if n_downloaders is not None else 1
    n_processors = n_processors if n_processors is not None else os.cpu_count()

    logger_queue = Queue(-1)
    listener = Process(target=log_listener, args=(logger_queue, default_configurer))
    listener.start()
    workers = []
    for i in range(n_processors):
        worker = Process(target=processor, args=[logger_queue, file_queue])
        workers.append(worker)
        worker.start()
    for w in workers:
        w.join()
    logger_queue.put_nowait(None)
    listener.join()
