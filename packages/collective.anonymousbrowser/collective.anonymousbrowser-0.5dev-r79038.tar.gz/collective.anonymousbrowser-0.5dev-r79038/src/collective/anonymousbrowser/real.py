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

import time
import re

from zc.testbrowser import real as browser
from collective.anonymousbrowser import browser as abrowser

class Browser(abrowser.BaseBrowser, browser.Browser):

    def __init__(self,
                 url=None, config=None, useragent=None,
                 openproxies=[],  proxify=True, proxy_max_use=3,
                 host = '127.0.0.1', port = '4242',
                 *args, **kwargs):
        abrowser.BaseBrowser.__init__(self,
                                  url=url, config=config, useragent=useragent,
                                  openproxies=openproxies,proxify=proxify, proxy_max_use=3,
                                  *args, **kwargs)
        self._enable_setattr_errors = False
        self.js = browser.JSProxy(self.execute)
        host = self._config._sections.get('collective.anonymousbrowser' , {}).get('host', host).strip()
        port = self._config._sections.get('collective.anonymousbrowser' , {}).get('port', port).strip()
        self.init_repl(host, port)
        if url is not None:
            self.open(url)
        self._enable_setattr_errors = False

    def browser_open(self, url, data=None):
        browser.Browser.open(self, url, data)

    def open(self, *args, **kwargs):
        """open.
        If there is errors, try to reconnect 10 times, one per second.
        """
        if kwargs.get('restart_ff', False):
            self.restart_ff()
        wills = 10
        while wills:
            wills -= 1
            try:
                abrowser.BaseBrowser.open(self, *args, **kwargs)
                break
            except Exception, e:
                if wills:
                    time.sleep(1)
                    continue
                # try to relaunch firefox
                if not 'restart_ff' in  kwargs:
                    kwargs.update({'restart_ff': True})
                    self.open(*args, **kwargs)
                raise

    def proxify(self, force=False):
        """"""
        pass

    def getPrompt(self):
        self.telnet.write('MARKER\n')
        _, g, _ = self.expect()
        return re.sub('> .*', '', g.group())

    def restart_ff(self):
        pass

    def home(self):
        self.execute("%s.home()" % self.getPrompt())

    def exec_contentjs(self, cmd):
        d = {'s': self.getPrompt(), 'cmd': cmd}
        try:
            self.home()
            ret = self.execute("this.content.%(cmd)s; " % d)
        except Exception, e:
            raise
        finally:
            self.home()
        return ret

# vim:set et sts=4 ts=4 tw=80:
