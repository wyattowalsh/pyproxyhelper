"""
File: pyproxyhelper/main.py
Author: @wyattowalsh
Tests: tests/test_proxyhelper.py
Description: cli entry point for the proxy helper
"""
import rich
from typer import Typer

from pyproxyhelper.providers.proxyscrape import ProxyScrape
from pyproxyhelper.proxyhelper import ProxyHelper

app = Typer()


@app.command()
def main( display: bool = False ) -> ProxyHelper:
    helper = ProxyHelper()
    if display:
        rich.print( helper.proxies )
    return helper


@app.command()
def test_proxy_scrape():
    """_summary_

    _extended_summary_
    """

    async def test():
        proxy_scrape = ProxyScrape()
        proxies = await proxy_scrape.get_proxies()
        rich.print( proxies )

    asyncio.run( test() )


if __name__ == "__main__":
    app()
