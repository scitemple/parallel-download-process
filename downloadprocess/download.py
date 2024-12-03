# -*- coding: utf-8 -*-
"""
Download
"""
import os
from logging import getLogger
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse

import requests


def _download_url(
    url: str, save_dp: Optional[Union[str, Path]] = None, save_fn: Optional[str] = None
):
    """
    Download a url and save content to the specified directory

    :param url: URL string to download.
    :param save_dp: Directory to save the downloaded files to (default is user
        downloads directory)
    :param save_fn: Save filename. Default filename is derived from url

    :return save_fp: file path of created file
    """

    os.makedirs(save_dp, exist_ok=True)
    if save_fn is None:
        parsed_url = urlparse(url)
        save_fn = os.path.basename(parsed_url.path) or "index.html"
    save_fp = os.path.join(save_dp, save_fn)

    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(save_fp, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return save_fp


def download_url(
    url: str, save_dp: Optional[Union[str, Path]] = None, save_fn: Optional[str] = None
):
    """
    Download a url with error handling

    :param url: URL string to download.
    :param save_dp: Directory to save the downloaded files to (default is user
        downloads directory)

    :return: URLs as keys and the status ("success" or "error: ...") as values.
    """
    logger = getLogger(__name__)
    try:
        save_fp = _download_url(url, save_dp, save_fn)
        logger.info(f"Downloaded: {url} -> {save_fp}")
        return save_fp

    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
