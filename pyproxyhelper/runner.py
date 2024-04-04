"""
File: pyproxyhelper/main.py
Author: @wyattowalsh
Description: Main entry point for the pyproxyhelper package.
"""
from pyproxyhelper.proxyhelper import ProxyHelper


async def helper():
    ph = ProxyHelper()
    proxies = await ph.get_proxies()
    print(proxies)
    return proxies, ph

if __name__ == "__main__":
    import asyncio
    asyncio.run(helper())
