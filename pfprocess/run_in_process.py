# -*- coding: utf-8 -*-
"""
Run a target function in a spawned dedicated process

This a serial (not parallel) pattern. It may be useful for processing files where it's
important to silo the proccessing well, e.g. for opening files where
it's difficult to close all the references
"""
import multiprocessing
import sys
from pathlib import Path
from typing import Any, Optional, Callable


sys.path.append(str(Path(__file__).parent))
from pfprocess.logging_utils import default_configurer
from pfprocess.parallel_logging import worker_logger_configurer, log_listener


class RunInProcessError(Exception):
    pass


def _target(conn, target, logger_queue, *args, **kwargs):
    if logger_queue is not None:
        worker_logger_configurer(logger_queue)
    ret = target(*args, **kwargs)
    conn.send(ret)


def run_in_process(
    target: Callable, args: Optional[list] = None, kwargs: Optional[dict] = None
) -> Any:
    """
    Spqwn a dedicated process and run target function in it

    Logging is enabled in target function via a logging queue listner

    If the target function raises an exception this will be handled by
    raising a generic RunInProcessError.

    :param target: target function
    :param args: arguments for target
    :param kwargs: keyword arguments for target
    """

    args = [] if args is None else args
    kwargs = {} if kwargs is None else kwargs

    # Create the logger listener
    # TODO create log configuration based on current log configuration
    logger_queue = multiprocessing.Queue(-1)
    listener = multiprocessing.Process(
        target=log_listener, args=(logger_queue, default_configurer)
    )
    listener.start()

    # Create the pipe and the receive and send connections. We choose Pipe
    # over Queue because it is a simple one process offshoot
    connr, conns = multiprocessing.Pipe()

    process = multiprocessing.Process(
        target=_target, args=[conns, target, logger_queue] + list(args), kwargs=kwargs
    )
    process.start()
    process.join()

    # Get the return data. The data should be available immediately (because
    # of .join() above) so we put a timeout of 0. If it's not there then we
    # hit an error in the extract points function and the result will be False.
    success = connr.poll(0)

    if not success:
        # TODO extract traceback information on the error from the running process
        raise RunInProcessError
    else:
        ret = connr.recv()

    return ret
