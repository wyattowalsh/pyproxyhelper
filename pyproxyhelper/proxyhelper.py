"""
File: pyproxyhelper/proxyhelper.py
Author: @wyattowalsh
Description: Main module for the pyproxyhelper package.
"""
import asyncio
import os
import random
from datetime import datetime, timedelta

import pandas as pd
from loguru import logger

from pyproxyhelper.logging import start_logger
from pyproxyhelper.providers.provider import Provider
from pyproxyhelper.providers.proxyscrape import ProxyScrape
from pyproxyhelper.providers.scrapingant import ScrapingAnt
from pyproxyhelper.providers.speedx import SpeedX

PROVIDERS = [ProxyScrape, ScrapingAnt, SpeedX]

PROXIES_FILE_NAME = "proxies.csv"


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

    async def get_proxies_helper(self) -> list:
        tasks = [self.fetch_provider_proxies(
            provider) for provider in self.providers]
        proxies_lists = await asyncio.gather(*tasks, return_exceptions=True)
        for proxies in proxies_lists:
            if isinstance(proxies, Exception):
                logger.error(f"Error fetching proxies: {proxies}")
            else:
                self.proxies.extend(proxies)
        return self.proxies

    async def fetch_provider_proxies(self, provider: Provider) -> list:
        try:
            provider_instance = provider()
            return await provider_instance.get_proxies()
        except Exception as e:
            logger.error(f"Error in provider {provider.__name__}: {e}")
            return []

    def save_proxies(self, filename: str = PROXIES_FILE_NAME) -> None:
        if not self.proxies:
            logger.error("No proxies to save.")
            return
        # add with timestamp as column name
        df = pd.DataFrame(self.proxies, columns=[datetime.now().isoformat()])
        df.to_csv(filename, index=False)
        logger.info(f"{len(self.proxies)} proxies saved to {filename}")

    async def get_proxies(self, force: bool = False) -> list:
        # load the file if it exists
        if os.path.exists(PROXIES_FILE_NAME):
            df = pd.read_csv(PROXIES_FILE_NAME)
            # if retrieved within the last hour, return the proxies
            if datetime.now() - timedelta(hours=1) < pd.to_datetime(df.columns[0]):
                self.proxies = df[df.columns[0]].tolist()
                logger.info(f"Retrieved {len(self.proxies)} proxies from file")
                return self.proxies
            else:
                logger.info("Proxies file is outdated, fetching new proxies")
                self.proxies = await self.get_proxies_helper()
                self.save_proxies()
                return self.proxies
        else:
            logger.warning(f"File {PROXIES_FILE_NAME} does not exist.")
            logger.info("Fetching new proxies")
            self.proxies = await self.get_proxies_helper()
            self.save_proxies()

    def get_proxy(self):
        # if no proxies, fetch them
        if not self.proxies:
            self.get_proxies()
        # return a random proxy
        return random.choice(self.proxies)
