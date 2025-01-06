# -*- coding: utf-8 -*-
"""
Example of downloading and processing files in parallel using multiprocess
"""
import logging
import os
import sys
import time
from pathlib import Path
from random import randint
from tempfile import TemporaryDirectory
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

sys.path.append(str(Path(__file__).parent.parent))
from pfprocess.parallel_processor import PFileProcessor

logger = logging.getLogger(__name__)

def _scrape_urls(base_url):
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.lstrip().endswith(".tar.gz"):
                full_url = urljoin(base_url, href)
                links.append(full_url)
        return links
    except requests.RequestException as e:
        print(f"Failed to fetch links: {e}")
        return []


def example_process(fps: List[Path]):
    if all([fp.is_file() for fp in fps]):
        time.sleep(randint(3, 8))  # simulate work
        logger.info(
            f"Process {os.getpid()}: {[fp.name for fp in fps]} processed "
            f"successfully"
        )
    else:
        logger.info(f"Process {os.getpid()}: Not all files exist, skipping.")


if __name__ == "__main__":
    base_url = "https://www.ncei.noaa.gov/data/nsrdb-solar/access/solar-only/"
    urls = _scrape_urls(base_url)
    urls = [
        urls[i : i + 2] for i in range(0, 10, 2)
    ]  # process collections of urls together

    with TemporaryDirectory() as td:
        pfp = PFileProcessor(example_process, td, n_processors=3)
        pfp.run(urls)

    print("Done")
