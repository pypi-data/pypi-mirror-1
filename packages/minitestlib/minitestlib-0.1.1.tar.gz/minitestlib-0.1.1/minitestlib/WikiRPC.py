# -*- coding: UTF-8 -*-
# vim: ts=4 sw=4 et:

"""
Communicate with remote Wiki engine (MoinMoin)
"""

__author__ = "Andy Shevchenko <andy.shevchenko@gmail.com>"
__revision__ = "$Id$"

__all__ = ['WikiRPC']

import xmlrpclib
from MoinMoin.support.multicall import MultiCall
import socket

from minitestlib.Log import logger

class WikiRPC:
    """ Put results to a MoinMoin Wiki """
    def __init__(self, url):
        self.proxy = xmlrpclib.ServerProxy(url)
        self.multi_call = MultiCall(self.proxy)
        self.page_cache = None
        self.auth_token = None

    def auth(self, user, password):
        """ Try to authorize user with given password """
        try:
            auth_token = self.proxy.getAuthToken(user, password)
        except socket.gaierror, err:
            # Actually that is the MoinMoin bug
            logger.error("Socket error: %s" % str(err))
            return False
        if not auth_token:
            return False
        self.auth_token = auth_token
        self.multi_call.applyAuthToken(self.auth_token)
        try:
            result = list(self.multi_call())
            return result[0] == 'SUCCESS'
        except xmlrpclib.Fault:
            return False
        return True

    def deauth(self):
        """ Forgot authorization """
        result = self.proxy.deleteAuthToken(self.auth_token)
        if result == 'SUCCESS':
            self.auth_token = None
            return True
        return False

    def read(self, page, cache=False):
        """ Read page from Wiki server """
        if not self.auth_token:
            return None
        self.multi_call.getPage(page)
        result = list(self.multi_call())
        if result[0] == 'SUCCESS':
            if cache:
                self.page_cache = result[1]
            return result[1]
        return None

    def write(self, page, data=None, cache=False):
        """ Write page to a Wiki server """
        if not self.auth_token:
            return False
        if data is None:
            if cache == False:
                # Clear page. EOL is used like filling because Wiki prevents to
                # put empty pages.
                content = "\n"
            else:
                content = self.page_cache
        else:
            content = data
        self.multi_call.putPage(page, content)
        result = list(self.multi_call())
        if result[0] == 'SUCCESS':
            return True
        return False

    def list(self):
        """ List all Wiki pages which are accessible for current user """
        if not self.auth_token:
            return None
        self.multi_call.getAllPages()
        result = list(self.multi_call())
        if result[0] == 'SUCCESS':
            return result[1]
        return None

    def get(self):
        """ Get data from local cache """
        return self.page_cache

    def put(self, data):
        """ Put data to local cache """
        self.page_cache = data

