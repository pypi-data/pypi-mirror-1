# -*- coding: UTF-8 -*-
# vim: ts=4 sw=4 et:

"""
Small driver for DC/AC relay [1]

[1] http://www.eeci.com/ar-2p.htm
"""

__author__ = "Andy Shevchenko <andy.shevchenko@gmail.com>"
__revision__ = "$Id$"

__all__ = ['PWSwitch']

import termios
import fcntl
import struct

from minitestlib.Log import logger

class PWSwitch:
    """ Power switch driver """
    def __init__(self, port):
        try:
            serial = open(port)
        except IOError, err:
            logger.error(str(err))
            serial = None
        self.serial = serial

    def dbg(self, msg):
        """ Internal debbuging """
        logger.debug("%s: %s" % (self.__class__.__name__, msg))

    def set(self, bit):
        """ Set gitven serial bit """
        try:
            fcntl.ioctl(self.serial, termios.TIOCMBIS, bit)
        except TypeError:
            self.dbg("Invalid serial port")

    def clear(self, bit):
        """ Clear gitven serial bit """
        try:
            fcntl.ioctl(self.serial, termios.TIOCMBIC, bit)
        except TypeError:
            self.dbg("Invalid serial port")

    def pin_dtr(self, status):
        """ Change status of DTR line """
        dtr = struct.pack('I', termios.TIOCM_DTR)
        if status:
            self.set(dtr)
        else:
            self.clear(dtr)

    def pin_rts(self, status):
        """ Change status of RTS line """
        rts = struct.pack('I', termios.TIOCM_RTS)
        if status:
            self.set(rts)
        else:
            self.clear(rts)

    def switch(self, status):
        """ Change status of all lines simultaneously """
        for pin in filter(lambda x: x.startswith('pin_'), dir(self)):
            func = getattr(self, pin)
            func(status)

