"""
File: pyproxyhelper/proxyhelper.py
Author: @wyattowalsh
Tests: tests/test_proxyhelper.py
Description: Main module for the pyproxyhelper package. Manages proxy retrieval, storage, and loading.
"""

import asyncio
import os
import random
from datetime import datetime, timedelta
from multiprocessing import Pool
from typing import List, Optional

import pandas as pd
from aiohttp import ClientSession
from loguru import logger

from .config import PROVIDERS, PROXIES_FILE_NAME
from .mylogger import start_logger
from .providers.provider import Provider


def fetch_proxies( provider ) -> List[ str ]:
    """
        Fetch proxies from all providers and consolidate into a unique list.

        Returns:
            List[str]: A deduplicated list of all fetched proxies.
        """
    try:
        results = asyncio.run( provider.get_proxies() )
        valid_proxies = {
            proxy
            for result in results if not isinstance( result, Exception )
            for proxy in result
        }
        return list( set( valid_proxies ) )
    except Exception as e:
        logger.error( f"An error occurred while fetching proxies: {e}" )
        return []


class ProxyHelper:

    def __init__( self,
                  log_to_console: bool = True,
                  log_to_file: bool = True ):
        """
        Initializes ProxyHelper with logging and prepares proxy provider instances.

        Args:
            log_to_console (bool): Enable logging to the console.
            log_to_file (bool): Enable logging to a file.
        """
        start_logger( console=log_to_console, file=log_to_file )
        self.providers = [ provider() for provider in PROVIDERS ]
        self.get_proxies()

    def get_proxies_helper( self ) -> List[ str ]:
        """
        Fetch proxies from all providers and consolidate into a unique list.

        Returns:
            List[str]: A deduplicated list of all fetched proxies.
        """
        logger.info( "Fetching proxies..." )
        with Pool( len( self.providers ) ) as p:
            proxies = p.map( fetch_proxies, self.providers )
        self.proxies = list(
            set( [ proxy for sublist in proxies for proxy in sublist ] ) )
        logger.info( f"Retrieved {len(self.proxies)} unique proxies." )
        return self.proxies

    def save_proxies(
            self,
            filename: str = PROXIES_FILE_NAME ) -> Optional[ pd.DataFrame ]:
        """
        Saves the current list of proxies to a CSV file.

        Args:
            filename (str): The file name to save the proxies to.

        Returns:
            Optional[pd.DataFrame]: The DataFrame of proxies if saved successfully, else None.
        """
        if not self.proxies:
            logger.error( "No proxies to save." )
            return None
        df = pd.DataFrame( self.proxies,
                           columns=[ datetime.now().isoformat() ] )
        df.to_csv( filename, index=False )
        logger.info( f"{len(self.proxies)} proxies saved to {filename}" )
        return df

    def load_proxies( self,
                      filename: str = PROXIES_FILE_NAME ) -> pd.DataFrame:
        """
        Loads proxies from a CSV file, or fetches new ones if file is outdated or missing.

        Args:
            filename (str): The file name from which to load proxies.

        Returns:
            pd.DataFrame: The DataFrame containing the loaded or newly fetched proxies.
        """
        if os.path.exists( filename ):
            df = pd.read_csv( filename )
            self.proxies = df[ df.columns[ 0 ] ].tolist()
            logger.info(
                f"Loaded {len(self.proxies)} proxies from {filename}" )
            return df
        else:
            logger.error( f"File {filename} does not exist." )
            logger.info( "Fetching new proxies..." )
            self.get_proxies_helper()
            return pd.DataFrame( self.proxies, columns=[ datetime.now() ] )

    def get_proxies( self, force: bool = False ) -> List[ str ]:
        """
        Retrieve proxies either from file or refresh if forced or file is outdated.

        Args:
            force (bool): Force the refresh of proxies even if they are considered current.

        Returns:
            List[str]: A list of proxies ready to use.
        """
        if force or not os.path.exists( PROXIES_FILE_NAME ):
            logger.info(
                "Forcing refresh or file not found. Fetching new proxies." )
            self.get_proxies_helper()
        else:
            df = self.load_proxies()
            if datetime.now() - timedelta( hours=1 ) > pd.to_datetime(
                    df.columns[ 0 ] ):
                logger.info(
                    "Proxies file is outdated, fetching new proxies." )
                self.get_proxies_helper()
        return self.proxies

    def get_proxy( self ) -> str:
        """
        Retrieves a single proxy randomly from the list of available proxies.

        Returns:
            str: A randomly chosen proxy.
        """
        if not self.proxies:
            self.get_proxies()
        return random.choice( self.proxies )
