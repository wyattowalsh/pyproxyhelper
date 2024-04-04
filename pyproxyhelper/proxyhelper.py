"""
File: pyproxyhelper/proxyhelper.py
Author: @wyattowalsh
Description: Main module for the pyproxyhelper package.
Tests: tests/test_proxyhelper.py
"""
import asyncio
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from sys import stderr

import pandas as pd
from loguru import logger

from pyproxyhelper.providers.provider import Provider
from pyproxyhelper.providers.proxyscrape import ProxyScrape
from pyproxyhelper.providers.scrapingant import ScrapingAnt
from pyproxyhelper.providers.speedx import SpeedX

PROVIDERS = [ProxyScrape, ScrapingAnt, SpeedX]

PROXIES_FILE_NAME = "proxies.csv"

# Configuration for the print formatting
PRINT_CONFIG = {
    "expand_all": True,
    "max_length": 3,
    "max_string": 21,
}

# Separate logger configuration
LOG_CONFIG = {
    "console": {
        "format": "<green>executed at: {time:YYYY-MM-DD at HH:mm:ss}</green> | <k><b>module:</b> {module}</k> <b>⇨</b> <e><b>function:</b> {function}</e> <b>⇨</b> <c><b>line #:</b> {line}</c> |  <yellow><b>elapsed time:</b> <u>{elapsed}</u></yellow> | <level><b>{level}</b></level> ⇨ {message} <red>{exception}</red>",
    },
    "file": {
        "format": "executed at: {time:YYYY-MM-DD at HH:mm:ss} | module: {module} ⇨ function: {function} ⇨ line #: {line} | elapsed time: {elapsed} | {level} ⇨ {message} {exception}",
    },
    "common": {
        "colorize": True,
        "diagnose": True,
        "enqueue": True,
        "backtrace": True,
    },
}


def start_logger(
    console: bool = False,
    file: bool = True,
    log_folder: str = "logs",
    log_name: str = "log",
    rotation: str = "100 MB",
) -> None:
    """
    Initializes a logger with console and/or file handlers with enhanced flexibility and error handling.

    Parameters:
    - console (bool): Enable console logging if True.
    - file (bool): Enable file logging if True.
    - log_folder (str): The directory where log files will be stored.
    - log_name (str): Base name for log files.
    - rotation (str): The rotation condition for log files.

    Raises:
    - ValueError: If neither console nor file logging is enabled.

    This function sets up the logger to output to the console and/or file based on the provided configurations.
    It ensures the log directory exists, and formats the log filenames with timestamps for uniqueness.
    """
    if not console and not file:
        raise ValueError("At least one of console or file must be enabled")

    logger.remove()

    log_folder_path = Path(log_folder)
    log_folder_path.mkdir(exist_ok=True)

    datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_path = log_folder_path / f"{log_name}.log"
    structured_log_file_path = log_folder_path / f"{log_name}_structured.json"

    if console:
        logger.add(stderr, **LOG_CONFIG["console"],
                   **LOG_CONFIG["common"])

    if file:
        logger.add(str(log_file_path), **
                   LOG_CONFIG["file"], **LOG_CONFIG["common"])
        logger.add(
            str(structured_log_file_path),
            **LOG_CONFIG["file"],
            **LOG_CONFIG["common"],
            serialize=True,
        )

    logger.info("Logger initialized")


class ProxyHelper:

    def __init__(self, log_to_console: bool = True, log_to_file: bool = True):
        """
        Args:
            log_to_console (bool, optional): whether or not to log to console. Defaults to True.
            log_to_file (bool, optional): whether or not to log to file. Defaults to True.
        """
        start_logger(console=log_to_console, file=log_to_file)
        self.providers = PROVIDERS
        self.proxies = []

    async def fetch_provider_proxies(self, provider: Provider) -> list:
        """Fetch proxies from a given provider.

        Args:
            provider: An instance of a Provider class that has a get_proxies method.

        Returns:
            A list of proxies fetched from the provider, or an empty list in case of an exception.
        """
        try:
            # Assuming provider is already an instance, so we directly call get_proxies without instantiation.
            return await provider.get_proxies()
        except Exception as e:
            logger.error(f"Error in provider {provider.__name__}: {e}")
            return []

    async def get_proxies_helper(self) -> list:
        tasks = (self.fetch_provider_proxies(
            provider) for provider in self.providers)
        proxies_lists = await asyncio.gather(*tasks, return_exceptions=True)
        self.proxies = set()
        for proxies in proxies_lists:
            if isinstance(proxies, Exception):
                logger.error(f"Error fetching proxies: {proxies}")
            else:
                self.proxies = self.proxies | set(proxies)
        return self.proxies

    def save_proxies(self, filename: str = PROXIES_FILE_NAME) -> pd.DataFrame | None:
        if not self.proxies:
            logger.error("No proxies to save.")
            return
        # add with timestamp as column name
        df = pd.DataFrame(self.proxies, columns=[datetime.now().isoformat()])
        df.to_csv(filename, index=False)
        logger.info(f"{len(self.proxies)} proxies saved to {filename}")
        return df

    async def load_proxies(self, filename: str = PROXIES_FILE_NAME) -> pd.DataFrame:
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            self.proxies = df[df.columns[0]].tolist()
            logger.info(f"Loaded {len(self.proxies)} proxies from {filename}")
            return df
        else:
            logger.error(f"File {filename} does not exist.")
            logger.info("Fetching new proxies...")
            self.proxies = await self.get_proxies_helper()
            df = self.save_proxies()
            return df

    async def get_proxies(self, force: bool = False) -> list:
        df = await self.load_proxies()
        if datetime.now() - timedelta(hours=1) < pd.to_datetime(df.columns[0]):
            self.proxies = df[df.columns[0]].tolist()
            logger.info(f"Retrieved {len(self.proxies)} proxies from file")
            return self.proxies
        else:
            logger.info("Proxies file is outdated, fetching new proxies")
            self.proxies = await self.get_proxies_helper()
            self.save_proxies()
            return self.proxies

    def get_proxy(self):
        # return a random proxy
        try:
            random.choice(self.proxies)
        except IndexError:
            logger.error("No proxies available. Try fetching new proxies.")
            return None
