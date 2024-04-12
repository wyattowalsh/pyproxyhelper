"""
File: pyproxyhelper/providers/proxyscrape.py
Author: @wyattowalsh
Description: Provider class for the ProxyScrape source.
"""
import asyncio

from aiohttp import ClientSession
from loguru import logger

from .provider import Provider


class ProxyScrape( Provider ):

    def __init__( self, name: str = "ProxyScrape" ):
        super().__init__( name=name )
        self.url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies"

    async def get_proxies( self ) -> list:
        logger.info( f"Getting proxies from {self.name}" )
        proxies = []
        try:
            async with ClientSession() as session:
                async with session.get( self.url ) as response:
                    if response.status != 200:
                        logger.error(
                            f"Failed to get proxies from {self.name}, status code: {response.status}"
                        )
                        return []
                    proxies = await response.text()
                    proxies = proxies.split( "\r\n" )
                    proxies = await self.check_proxies( session, proxies )
                    logger.info(
                        f"Retrieved {len(proxies)} proxies from {self.name}" )
                    return proxies
        except Exception as e:
            logger.error(
                f"An error occurred while getting proxies from {self.name}: {e}"
            )
