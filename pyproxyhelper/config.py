"""
File: pyproxyhelper/config.py
Author: @wyattowalsh
Description: Configuration settings for the pyproxyhelper package.
"""

# Importing proxy providers
from .providers.proxyscrape import ProxyScrape
from .providers.scrapingant import ScrapingAnt
from .providers.speedx import SpeedX

# List of provider classes
PROVIDERS = [ ProxyScrape, ScrapingAnt, SpeedX ]

# Default filename for saving proxies
PROXIES_FILE_NAME = "proxies.csv"
