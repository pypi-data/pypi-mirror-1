# -*- coding: UTF-8 -*-
# vim: ts=4 sw=4 et:

"""
Logging module
"""

__author__ = "Andy Shevchenko <andy.shevchenko@gmail.com>"
__revision__ = "$Id$"

__all__ = ['logger']

import logging
import sys

def get():
    """ Setup stream based logger """
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s",
                                  "%b %d %H:%M:%S")

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    log = logging.getLogger("org.teleca.minitestlib")
    log.addHandler(handler)
    log.setLevel(logging.WARNING)
    return log

logger = get()

