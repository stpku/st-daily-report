"""Centralised logging configuration for ST-dailyreport.

All modules should use ``from log import logger`` instead of ``print()``.
Log files go to runtime/logs/ and the console receives INFO+ by default.

NOTE: This module must NOT import any other project module to avoid circular
imports (many modules import log at the top level).
"""

import logging
import os
import sys

# Self-contained path resolution — do NOT import path_utils
_LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runtime", "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

logger = logging.getLogger("st-dailyreport")
logger.setLevel(logging.DEBUG)

# Prevent duplicate handlers when the module is imported multiple times
if not logger.handlers:
    # Console handler — INFO and above
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console)

    # File handler — DEBUG and above, single log file
    file_handler = logging.FileHandler(
        os.path.join(_LOG_DIR, "st-dailyreport.log"),
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-5s %(name)s: %(message)s",
                          datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(file_handler)
