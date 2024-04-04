"""
File: pyproxyhelper/utils.py
Author: @wyattowalsh
Description: utility functions for the pyproxyhelper package.
"""
from pyproxyhelper.proxyhelper import ProxyHelper


async def getProxyHelper() -> ProxyHelper:
    return await ProxyHelper()
