"""
File: pyproxyhelper/utils.py
Author: @wyattowalsh
Description: utility functions for the pyproxyhelper package.
"""
from pyproxyhelper.proxyhelper import ProxyHelper


async def initAndGetProxies() -> tuple[list, ProxyHelper]:
    ph = ProxyHelper()
    proxies = await ph.get_proxies()
    return proxies, ph
