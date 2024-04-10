"""
File: pyproxyhelper/main.py
Author: @wyattowalsh
Tests: tests/test_proxyhelper.py
Description: cli entry point for the proxy helper
"""
import rich
from typer import Typer

from pyproxyhelper.proxyhelper import ProxyHelper

app = Typer()


@app.command()
def main( display: bool = False ) -> ProxyHelper:
    helper = ProxyHelper()
    if display:
        rich.print( helper.proxies )
    return helper


if __name__ == "__main__":
    app()
