"""
File: tests/test_proxyhelper.py
Author: @wyattowalsh
Tests For: pyproxyhelper/proxyhelper.py
"""
import asyncio

import pytest
from loguru import logger

from pyproxyhelper.providers.provider import Provider
from pyproxyhelper.proxyhelper import (LOG_CONFIG, PROVIDERS, ProxyHelper,
                                       start_logger, stderr)

MODULE_PREFIX = "pyproxyhelper.proxyhelper."


class TestLogger:

    @pytest.fixture(autouse=True)
    def setup_method(self, mocker):
        self.mock_logger = mocker.patch(MODULE_PREFIX + 'logger')
        self.mock_path = mocker.patch(MODULE_PREFIX + 'Path')
        self.mock_path.return_value = mocker.MagicMock()

    def teardown_method(self):
        mocks = [self.mock_logger, self.mock_path]
        [mock.reset_mock() for mock in mocks]

    @pytest.mark.parametrize("console,file,add_call_count,path_call_count,mkdir_call_count,remove_call_count", [
        (True, True, 3, 1, 1, 1),
        (True, False, 1, 1, 1, 1),
        (False, True, 2, 1, 1, 1),
        (False, False, 0, 0, 0, 0),
        (True, None, 1, 1, 1, 1),
        (None, True, 2, 1, 1, 1),
        (None, None, 0, 0, 0, 0)
    ])
    def test_start_logger(self, console, file, add_call_count, path_call_count, mkdir_call_count, remove_call_count):
        if console or file:
            start_logger(console=console, file=file)
            assert self.mock_logger.remove.call_count == remove_call_count
            assert self.mock_path.call_count == path_call_count
            assert self.mock_path.return_value.mkdir.call_count == mkdir_call_count
            assert self.mock_logger.add.call_count == add_call_count
            if console:
                self.mock_logger.add.assert_any_call(
                    stderr, **LOG_CONFIG["console"], **LOG_CONFIG["common"])
            if file:
                self.mock_logger.add.assert_any_call(str(
                    self.mock_path.return_value / "log.log"), **LOG_CONFIG["file"], **LOG_CONFIG["common"])
                self.mock_logger.add.assert_any_call(str(
                    self.mock_path.return_value / "log_structured.json"), **LOG_CONFIG["file"], **LOG_CONFIG["common"], serialize=True)
            self.mock_logger.info.assert_called_once_with("Logger initialized")
        else:
            with pytest.raises(ValueError):
                start_logger(console=console, file=file)
            self.mock_logger.remove.assert_not_called()
            self.mock_path.assert_not_called()
            self.mock_logger.add.assert_not_called()
            self.mock_logger.info.assert_not_called()

        self.teardown_method()


class TestProxyHelper:

    @pytest.fixture(autouse=True)
    def setup_method(self, mocker):
        self.proxy_helper = mocker.AsyncMock()
        self.proxy_helper.providers = PROVIDERS

    def teardown_method(self):
        mocks = [self.proxy_helper]
        [mock.reset_mock() for mock in mocks]

    def test___init__(self):
        proxy_helper = ProxyHelper()
        assert proxy_helper.providers == PROVIDERS
        assert proxy_helper.proxies == []

    @pytest.mark.asyncio
    async def test_fetch_provider_proxies(self, mocker):
        mock_proxy_helper = ProxyHelper()

        # Mock the Provider instance
        mock_provider = mocker.MagicMock(
            name='MockProvider', spec=Provider)
        mock_provider.__name__ = 'MockProvider'
        mock_provider.get_proxies = mocker.AsyncMock(
            return_value=['proxy1', 'proxy2'])

        # Test successful proxy fetch
        result = await mock_proxy_helper.fetch_provider_proxies(mock_provider)
        assert result == [
            'proxy1', 'proxy2'], f"Expected ['proxy1', 'proxy2'], but got {result}"
        mock_provider.get_proxies.assert_awaited_once()

        # Simulate an exception in get_proxies
        mock_provider.get_proxies.side_effect = Exception(
            'Error fetching proxies')
        result = await mock_proxy_helper.fetch_provider_proxies(mock_provider)
        assert result == [], "Expected an empty list, but got something else"
