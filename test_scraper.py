#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scraping test script"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

# Import and run
from src.scraper import main

if __name__ == "__main__":
    main()
