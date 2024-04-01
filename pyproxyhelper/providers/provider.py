"""
File: pyproxyhelper/providers/provider.py
Author: @wyattowalsh
Description: base class for all proxy providers.
"""
from abc import ABC, abstractmethod

from aiohttp import ClientSession
from loguru import logger


PROXY_CHECK_TIMEOUT = 5
PROXY_CHECK_URL = 'http://example.com'


class Provider(ABC):
    def __init__(self, name: str = None):
        self.proxies = []
        self.name = name

    @abstractmethod
    def get_proxies(self) -> list:
        """
        abstract method to be implemented by all providers.
        """
        pass

    async def check_proxy(self, session: ClientSession, proxy: str) -> str | None:
        """checks if a proxy is valid by making a request to the check url.

        Args:
            session (ClientSession): aiohttp session object.
            proxy (str): proxy to check.

        Returns:
            str | None: returns the proxy if it is valid, otherwise None.
        """
        try:
            async with session.get(PROXY_CHECK_URL, proxy=f'http://{proxy}', timeout=PROXY_CHECK_TIMEOUT) as response:
                if response.status == 200:
                    return proxy
                else:
                    return None
        except Exception:
            return None
