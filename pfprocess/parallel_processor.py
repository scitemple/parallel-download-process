# -*- coding: utf-8 -*-
"""
Download process
"""

import logging
import os
import sys
from multiprocessing import Queue, Process
from pathlib import Path
from typing import Optional, Union, Callable, List

import platformdirs

sys.path.append(str(Path(__file__).parent))
from pfprocess.logging_utils import default_configurer
from pfprocess.remote_utils import download_url
from pfprocess.parallel_logging import log_listener, worker_logger_configurer


def _target(func, file_queue, logger_queue):
    if file_queue is None:
        raise ValueError("file_queue is None")

    # we're in the spawned process now, so configure logging to go to queue
    if logger_queue is not None:
        worker_logger_configurer(logger_queue)
    logger = logging.getLogger()
    while True:
        logger.info(f"Processor {os.getpid()}: waiting on queue")
        fps = file_queue.get()

        if fps is None:  # end condition
            # put it back so that other consumers see it
            file_queue.put(None)
            logger.info(f"Ending processor {os.getpid()} on end flag from producer")
            break

        logger.info(f"Processor {os.getpid()} starting task for {len(fps)} files")
        try:
            func(fps)
        except Exception as e:
            logger.error(f"Failed to process {fps} with error {e}")


class PFileProcessor:
    """
    Use multiprocessing to download and process a collection of files in parallel. Main
    process to download and queue files, N spawned processes to process the files.
    """

    def __init__(
        self,
        func: Callable,
        save_dp: Optional[Union[str, Path]] = None,
        n_processors: Optional[int] = None,
        queue_length: Optional[int] = None,
        log_configurer: Optional[Callable] = None,
    ):
        """
        :param func: Callable to process files. It should take a single argument which
            is a list of Path objects. Logging from within function will be handed back
            to main process for logging via a multiprocess Queue
        :param save_dp: Directory to save the downloaded files to (default is user
            downloads directory)
        :param n_processors: Number of spawned worker processes to use
        :queue_length: Number of batches to queue up for the workers
        :log_configurer: Function for configuring the root logger
        """

        self.func = func
        save_dp = platformdirs.user_downloads_dir() if save_dp is None else save_dp
        self.save_dp: Path = Path(save_dp)

        self.n_processors: int = (
            n_processors if n_processors is not None else os.cpu_count()
        )
        self.queue_length: int = 10 if queue_length is None else queue_length

        self.logger_queue = Queue(-1)
        self.file_queue = Queue(self.queue_length)

        self.log_listener = None
        self.log_configurer = (
            log_configurer if log_configurer is not None else default_configurer
        )
        self.logger = logging.getLogger(__name__)

    def download_urls(self, urls, save_fn: Optional[str] = None):
        """
        Download urls with error handling

        :param urls: list of urls to download
        :param save_fn: Save filename. Default filename is derived from url

        :return: URLs as keys and the filepath or "error" as values.
        """

        os.makedirs(self.save_dp, exist_ok=True)

        success = {}
        error = {}
        for url in urls:
            try:
                save_fp = download_url(url, self.save_dp, save_fn=save_fn)
                self.logger.info(f"Downloaded: {url} -> {save_fp}")
                success[url] = save_fp

            except Exception as e:
                self.logger.error(f"Failed to download {url}: {e}")
                error[url] = str(e)

        return success, error

    def _run(self, urls):
        for i, batch in enumerate(urls):

            # TODO even the main process should really log to the queue to avoid danger
            #  of race conditions if logging with FileHandler
            self.logger.info(f"Starting download of url batch {i + 1}/{len(urls)}")
            list(batch) if isinstance(batch, (tuple, list)) else [batch]
            success, error = self.download_urls(batch)

            if len(error) > 0:
                self.logger.error(
                    f"{len(error)} urls failed to download, skipping batch"
                )
                continue

            # add filepaths to processing queue
            self.file_queue.put(list(success.values()))

        self.file_queue.put(None)  # end condition
        self.logger.info("All slots successfully downloaded. Producer ending.")

    def run(self, urls: Union[List[str], List[List[str]]]):
        """
        Download and process a list of urls or a list of url batches
        """

        self.log_listener = Process(
            target=log_listener, args=(self.logger_queue, self.log_configurer)
        )
        self.log_listener.start()
        workers = [
            Process(
                target=_target, args=[self.func, self.file_queue, self.logger_queue]
            )
            for _ in range(self.n_processors)
        ]
        [w.start() for w in workers]

        self._run(urls)

        [w.join() for w in workers]
        self.logger_queue.put_nowait(None)
        self.log_listener.join()
