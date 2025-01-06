# -*- coding: utf-8 -*-
"""
Logging utilities
"""

import logging
import logging.handlers
from logging import INFO
from pathlib import Path
from typing import Optional, Union

from logzero import setup_logger, LogFormatter


def default_configurer(log_fp: Optional[Union[str, Path]] = None):
    """
    Default logger configuration with stream and optionally a rotating file handler
    :param log_fp: logging file path
    :return:
    """
    # add stream and rotating file handlers
    setup_logger(
        "",
        logfile=log_fp,
        level=INFO,
        maxBytes=4 * 1024**2,
        backupCount=1,
        fileLoglevel=INFO,
    )

    # disable colouring in file logging - leads to weird characters
    logger = logging.getLogger("")
    for handler in logger.handlers:
        if isinstance(handler, logging.handlers.RotatingFileHandler):
            handler.setFormatter(LogFormatter(color=False))
