# -*- coding: utf-8 -*-
"""
Remote utils
"""

import os
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse

import requests


def download_url(
    url: str,
    save_dp: Union[str, Path],
    save_fn: Optional[str] = None,
    chunk_size: int = 8192,
) -> Path:
    """
    Download a url and save content to the specified directory

    :param url: URL string to download.
    :param save_dp: Directory to save the downloaded files to (default is user
        downloads directory)
    :param save_fn: Save filename. Default filename is derived from url
    :param chunk_size: Chunk size in bytes

    :return save_fp: file path of created file
    """
    save_dp = Path(save_dp)
    if save_fn is None:
        parsed_url = urlparse(url)
        save_fn = os.path.basename(parsed_url.path) or "index.html"
    save_fp = save_dp / save_fn

    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(save_fp, "wb") as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            f.write(chunk)
    return save_fp
