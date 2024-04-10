"""
File: pyproxyhelper/providers/provider.py
Author: @wyattowalsh
Description: base class for all proxy providers.
"""
import asyncio
from abc import ABC, abstractmethod

from aiohttp import ClientSession

PROXY_CHECK_TIMEOUT = 5
PROXY_CHECK_URL = 'stats.nba.com'


class Provider( ABC ):

    def __init__( self, name: str = None ):
        self.proxies = []
        self.name = name

    async def check_proxy( self, session: ClientSession,
                           proxy: str ) -> str | None:
        """checks if a proxy is valid by making a request to the check url.

        Args:
            session (ClientSession): aiohttp session object.
            proxy (str): proxy to check.

        Returns:
            str | None: returns the proxy if it is valid, otherwise None.
        """
        try:
            async with session.get( PROXY_CHECK_URL,
                                    proxy=f'http://{proxy}',
                                    timeout=PROXY_CHECK_TIMEOUT ) as response:
                if response.status == 200:
                    return proxy
                else:
                    return None
        except Exception:
            return None

    async def check_proxies( self, session: ClientSession,
                             proxies: list ) -> list:
        """checks a list of proxies for validity.

        Args:
            session (ClientSession): aiohttp session object.
            proxies (list): list of proxies to check.

        Returns:
            list: list of valid proxies.
        """
        proxies = [ self.check_proxy( session, proxy ) for proxy in proxies ]
        proxies = await asyncio.gather( *tasks )
        return [ proxy for proxy in proxies if proxy ]

    @abstractmethod
    async def get_proxies( self ) -> list:
        """
        abstract method to be implemented by all providers.
        """
        pass
