"""
File: pyproxyhelper/providers/speedx.py
Author: @wyattowalsh
Description: Provider class for the SpeedX GitHub Repo source.
"""
import asyncio

from aiohttp import ClientSession
from loguru import logger

from .provider import Provider


class SpeedX(Provider):
    def __init__(self, name: str = "SpeedX"):
        super().__init__(name=name)
        self.url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"

    async def get_proxies(self) -> list:
        logger.info(f"Getting proxies from {self.name}")
        proxies = []
        try:
            async with ClientSession() as session:
                async with session.get(self.url) as response:
                    if response.status != 200:
                        logger.error(
                            f"Failed to get proxies from {self.name}, status code: {response.status}")
                        return []
                    proxies = await response.text()
                    proxies = proxies.split("\n")
                    tasks = [self.check_proxy(session, proxy)
                             for proxy in proxies]
                    proxies = await asyncio.gather(*tasks)
                    proxies = [proxy for proxy in proxies if proxy]
        except Exception as e:
            logger.error(
                f"An error occurred while getting proxies from {self.name}: {e}")
        else:
            logger.info(f"Retrieved {len(proxies)} proxies from {self.name}")
        return proxies
