# -*- coding: utf-8 -*-
"""
Multiprocess logging

Inspiration from
https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes

Example use

import multiprocessing
import sys
import time
from logging import getLogger
from pathlib import Path
from random import randint

from logging_utils import default_configurer
from multithread_logging import worker_logger_configurer, log_listener


def worker_process(logger_queue, n):
    worker_logger_configurer(logger_queue)
    time.sleep(randint(1, 4))
    getLogger(__name__).info(f"Worker process {n} done")
    getLogger(__name__).debug(f"Debug level not shown")


if __name__ == "__main__":

    logger_queue = multiprocessing.Queue(-1)
    listener = multiprocessing.Process(target=log_listener,
                                       args=(logger_queue, default_configurer))
    listener.start()
    workers = []
    for i in range(10):
        worker = multiprocessing.Process(target=worker_process,
                                         args=[logger_queue, i])
        workers.append(worker)
        worker.start()
    for w in workers:
        w.join()
    logger_queue.put_nowait(None)
    listener.join()
"""

import logging
import logging.handlers
from multiprocessing import Queue
from typing import Callable


def worker_logger_configurer(queue: Queue):
    """
    Configure logger for spawned process
    """
    h = logging.handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.DEBUG)


def log_listener(queue: Queue, configurer: Callable, *args, **kwargs):
    """
    Listener handler for logging events

    :param queue: multiprocessing queue for logging events
    :param configurer: a function to configure the root logger
    :param args: further args passed to configurer
    :param kwargs: further kwargs passed to configurer
    """
    configurer(*args, **kwargs)
    while True:
        try:
            record = queue.get()
            if record is None:  # Signal for listener to exit
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)
        except Exception:
            import sys, traceback

            print("Exception in parallel log listener:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
