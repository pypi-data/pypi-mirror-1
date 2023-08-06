#!/usr/bin/env python

# Copyright (C) 2008, Mathieu PASQUET <kiorky@cryptelium.net>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


"""
A proxified wrapper around zope.testbrowser
"""

__docformat__ = 'restructuredtext en'

import os
from os.path import join
import sys
import random
import mechanize
import urllib2
import logging

from zc.testbrowser import browser
from ConfigParser import ConfigParser

__CONFIGFILE__ = join(sys.prefix, 'etc', 'collective.aonymousbrowser.cfg')

FF2_USERAGENT =  'Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'
__log__ = logging.getLogger('collective.anonymousbrowser')

class BaseBrowser:
    def __init__(self,
                 url=None,config=None, useragent=None,
                 openproxies=[], proxify=True, proxy_max_use=None,
                 mech_browser = None,
                 *args, **kwargs):
        self._enable_setattr_errors = False
        self._config = ConfigParser()
        if not config:
            config = __CONFIGFILE__
        if not os.path.isfile(config):
            self._initConfig()
        self._config.read(config)
        proxieslist = self._config._sections.get('collective.anonymousbrowser' , {}).get('proxies', '').strip()
        self.proxies = []
        if proxieslist:
            self.proxies = [proxy.strip() for proxy in proxieslist.split('\n')]
        if not useragent:
            useragent = FF2_USERAGENT
        self.useragent = useragent
        self.proxified = False
        if proxieslist:
                self.proxified = bool(proxify)
        self._lastproxy = {'proxy':-1, 'count':0}
        if mech_browser is None:
            mech_browser = mechanize.Browser()
        self.mech_browser = mech_browser 
        self.proxy_max_use = proxy_max_use
        self.cp = self.proxies[:]

    def _initConfig(self):
        self._config.write(__CONFIGFILE__)
        self._config.add_section('collective.anonymousbrowser')
        self._config.set('collective.anonymousbrowser', 'proxies', '')
        directory = os.path.dirname(__CONFIGFILE__)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        self._config.write(open(__CONFIGFILE__, 'w'))

    def chooseProxy(self):
        choice = 0
        if len(self.proxies) < 2:
            # for 0 or 1 proxy, just get it
            choice = random.randint(0, len(self.proxies)-1)
        else:
            # for 2+ proxies in the list, we iterate to get a different proxy
            # for the last one used, if this one was too many used.
            # We also put a coin of the reuse of the proxy, we just dont go too
            # random
            proxy_not_chosen = True
            maxloop = 200
            while proxy_not_chosen:
                # pile or face ! We reuse the proxy or not!
                if not self.proxy_max_use or (1 <= self._lastproxy['count']) and (self._lastproxy['count'] < self.proxy_max_use):
                    if random.randint(0, 1):
                        choice = self._lastproxy['proxy']
                    else:
                        choice = random.randint(0, len(self.proxies)-1)
                if self._lastproxy['proxy'] == choice:
                    if not self.proxy_max_use or (self._lastproxy['count'] <= self.proxy_max_use):
                        self._lastproxy['proxy'] = choice
                        proxy_not_chosen = False
                else:
                    self._lastproxy['proxy'] = choice
                    # reinitialize the proxy count
                    self._lastproxy['count'] = 0
                    proxy_not_chosen = False
                maxloop -= 1
                if not maxloop:
                    print "Ho, seems we got the max wills to choose, something has gone wrong"
                    proxy_not_chosen = False
        self._lastproxy['count'] += 1
        return self.proxies[choice]

    def reset(self):
        """Reset the ubderlying browser"""
        try:
            self.browser_open('about:blank')
        except Exception, e:
            if not ('unknown url type:' in '%s' % e):
                raise e

    def open(self, url, data=None, retrys=4, *args, **kwargs):
        try:
            if self.proxified:
                self.proxify()
            self.browser_open(url, data)
        except urllib2.URLError, e:
            if retrys:
                # go to open blank to reset entirely all post and other stuff
                self.reset()

                
                # removing dead proxies
                if self.proxified:
                    if len(self.proxies) >= 1:
                        del self.proxies[self._lastproxy['proxy']]
                        self._lastproxy['proxy'] = -1
                        self._lastproxy['count'] = 0
                    else:
                        raise Exception("There are no valid proxies left") 
                
                __log__.error('Retrying "%s", (left: %s)' % (url, retrys))
                retrys -= 1
                self.open(url, data, retrys)
            else:
                raise e

    def proxify(self, force=False):
        """Method to choose and set a proxy."""
        raise Exception('not implemented')

    def browser_open(self, url, data=None):
        """Real method to hit the browser."""
        raise Exception('not implemented')
        # implementation example :
        # browser.Browser.open(self, url, data)

class Browser(BaseBrowser, browser.Browser):

    def __init__(self,
                 url=None, mech_browser=None, useragent=None,
                 openproxies=[], config=None, proxify=True,
                 proxy_max_use=None, reset=False,
                 *args, **kwargs):
        BaseBrowser.__init__(self, url=url,config=config, useragent=useragent,
                             openproxies=openproxies,  proxify=proxify, proxy_max_use=proxy_max_use,
                             *args, **kwargs)
        self._enable_setattr_errors = False
        if mech_browser is None:
            mech_browser = mechanize.Browser()
        self.mech_browser = mech_browser
        if url is not None:
            BaseBrowser.open(self, url)

    def browser_open(self, url, data=None):
        self.timer = browser.PystoneTimer()
        self.raiseHttpErrors = True
        self.mech_browser.set_handle_robots(False)
        self.mech_browser.addheaders = [('User-agent' , self.useragent)]
        browser.Browser.open(self, url, data)

    def proxify(self, force=False):
        """"""
        if (self.proxified or force) and self.proxies:
            proxy = self.chooseProxy()
            self.mech_browser.set_proxies({'http': proxy, 'https': proxy})

# vim:set et sts=4 ts=4 tw=80:
