# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Logging."""

import logging
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Print logs to console.
stream_handler = logging.StreamHandler(sys.stdout)

# Format logs.
log_formatter = logging.Formatter(
    "%(asctime)s [%(processName)s: %(process)d] "
    "[%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
)
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)
