import asyncio

from pyproxyhelper.providers.proxyscrape import ProxyScrape


async def main():
    ps = ProxyScrape()
    proxies = await ps.get_proxies()
    print( proxies )
    return proxies


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete( main() )
