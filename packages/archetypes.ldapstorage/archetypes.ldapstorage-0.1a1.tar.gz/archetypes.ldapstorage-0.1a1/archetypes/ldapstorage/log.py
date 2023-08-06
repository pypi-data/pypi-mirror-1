"""
This module contains logging utilities for LDAPStorage. It only logs
messages of severity equal or lower than 'INFO' when in debug mode.
"""

import logging
import config

logger = logging.getLogger('LDAPStorage')

# generic log method
def log(message, summary='', severity=logging.INFO):
    if severity > logging.INFO:
        logger.log(severity, '%s \n%s', summary, message)
    elif config.DEBUG_MODE:
        logger.log(severity, '%s \n%s', summary, message)
