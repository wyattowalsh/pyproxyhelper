"""
File: pyproxyhelper/providers/scrapingant.py
Author: @wyattowalsh
Description: Provider class for the ScrapingAnt source.
"""
import asyncio

import pandas as pd
from aiohttp import ClientSession
from loguru import logger

from .provider import Provider


class ScrapingAnt(Provider):
    def __init__(self, name: str = "ScrapingAnt"):
        super().__init__(name=name)
        self.url = "https://scrapingant.com/proxies"

    async def get_proxies(self):
        logger.info(f"Getting proxies from {self.name}")
        proxies = []
        try:
            proxies = pd.read_html(self.url)[0]
            proxies = proxies[proxies["Protocol"] == "HTTP"]["IP"].tolist()
            async with ClientSession() as session:
                tasks = [self.check_proxy(session, proxy) for proxy in proxies]
                proxies = await asyncio.gather(*tasks)
                proxies = [proxy for proxy in proxies if proxy is not None]
        except Exception as e:
            logger.error(
                f"An error occurred while getting proxies from {self.name}: {e}")
        else:
            logger.info(f"Retrieved {len(proxies)} proxies from {self.name}")
        return proxies
