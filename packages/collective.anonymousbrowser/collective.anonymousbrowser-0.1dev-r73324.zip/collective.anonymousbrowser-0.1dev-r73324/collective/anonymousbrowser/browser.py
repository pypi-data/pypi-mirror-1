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

__docformat__ = 'restructuredtext en'

import os
from os.path import join
import sys
import random
import mechanize

from zope.testbrowser import browser
from ConfigParser import ConfigParser

__CONFIGFILE__ = join(sys.prefix, 'etc', 'collective.aonymousbrowser.cfg')

FF2_USERAGENT =  'Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'

class Browser(browser.Browser):

    def _initConfig(self):
        self._config.write(__CONFIGFILE__)
        self._config.add_section('collective.anonymousbrowser')
        self._config.set('collective.anonymousbrowser', 'proxies', '')
        print 'Writing default configuration file in %s' % __CONFIGFILE__
        self._config.write(open(__CONFIGFILE__, 'w'))

    def __init__(self,
                 url=None, mech_browser=None, useragent=None,
                 openproxies=[], config=None, proxify=True, proxy_max_use=3):
        self._config = ConfigParser()
        if not config:
            config = __CONFIGFILE__
        if not os.path.isfile(config):
            self._initConfig()
        self._config.read(config)
        proxieslist = self._config._sections.get('ccollective.anonymousbrowser' , {}).get('proxies', '').strip()
        self.proxies = []
        if proxieslist:
            self.proxies = [proxy.strip() for proxy in proxieslist.split('\n')]
        if not useragent:
            useragent = FF2_USERAGENT
        self.proxified = bool(proxify)
        self._lastproxy = {'proxy':-1, 'count':0}
        self.proxy_max_use = proxy_max_use
        if mech_browser is None:
            mech_browser = mechanize.Browser()
        self.mech_browser = mech_browser
        self.timer = browser.PystoneTimer()
        self.raiseHttpErrors = True
        self._enable_setattr_errors = True
        self.mech_browser.set_handle_robots(False)
        self.mech_browser.addheaders = [('User-agent' , useragent)] 
        if url is not None:
            self.open(url)

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
                if (1 <= self._lastproxy['count']) and (self._lastproxy['count'] < self.proxy_max_use):
                    if random.randint(0, 1):
                        choice = self._lastproxy['proxy']
                    else:
                        choice = random.randint(0, len(self.proxies)-1)
                if self._lastproxy['proxy'] == choice:
                    if self._lastproxy['count'] <= self.proxy_max_use:
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

    def proxify(self, force=False):
        """"""
        if (self.proxified or force) and self.proxies:
            proxy = self.chooseProxy()
            self.mech_browser.set_proxies({'http': proxy, 'https': proxy})

    def open(self, url, data=None):
        if self.proxified:
            self.proxify()
        browser.Browser.open(self, url, data)

# vim:set et sts=4 ts=4 tw=80:
