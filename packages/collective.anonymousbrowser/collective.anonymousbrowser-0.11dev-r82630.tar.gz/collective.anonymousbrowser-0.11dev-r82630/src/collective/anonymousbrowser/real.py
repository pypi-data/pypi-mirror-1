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
import os
import subprocess
import socket
import signal
import logging
import threading
import re
import mozrunner
from mozrunner import global_settings
from decorator import decorator

from zc.testbrowser import real as browser
from collective.anonymousbrowser import browser as abrowser
from zc.testbrowser.real import PROMPT, CONTINUATION_PROMPT

def firefox_user_profile():
    homes = [os.path.expanduser('~/.firefox'),
             os.path.expanduser('~/.mozilla-firefox'),
             os.path.expanduser('~/.mozilla/firefox'),
            ]
    for home in homes:
        if os.path.isdir(home):
            for f in os.listdir(home):
                if f.endswith('default'):
                    return os.path.abspath(
                        os.path.join(home, f)
                    )
    return None

MOZ_USER_PROFILE = firefox_user_profile()
if MOZ_USER_PROFILE:
    global_settings.MOZILLA_DEFAULT_PROFILE = MOZ_USER_PROFILE

def exec_on_firefox_dir(*args):
    def go_in_dir(f, *args, **kwargs):
        ret, cwd = None, os.getcwd()
        d = os.path.dirname(global_settings.firefoxBin)
        os.chdir(d)
        try:
            ret = f(*args, **kwargs)
            os.chdir(cwd)
        except:
            os.chdir(cwd)
            raise
        return ret
    return decorator(go_in_dir)

class FirefoxThread():

    def __init__(self, *args, **kwargs):
        #threading.Thread.__init__(self, *args, **kwargs)
        self.set_settings(self, *args, **kwargs)
        self.FIREFOX = None
        self.FIREFOX_THREAD = None

    @exec_on_firefox_dir()
    def set_settings(self, *args, **kwargs):
        # setting no window bugs from ff
        if 'prefs' in kwargs:
            global_settings.MOZILLA_DEFAULT_PREFS.update(kwargs['prefs'])
            del kwargs['prefs']
        for setting in kwargs:
            setattr(global_settings, setting, kwargs[setting])
        global_settings.MOZILLA_ENV['MOZ_NO_REMOTE'] = "1"
        firefox = getattr(global_settings, 'MOZILLA_BINARY', '')
        if firefox:
            global_settings.firefoxBin=firefox
            d = os.path.dirname(global_settings.firefoxBin)
            #paths = os.environ.get('PATH', '').split(':')
            #ldpaths = os.environ.get('LD_LIBRARY_PATH', '').split(':') 
            #if not d in paths:
            #    paths.insert(0, d)
            #    global_settings.MOZILLA_ENV['PATH'] = ':'.join(paths)
            #    global_settings.MOZILLA_ENV['LD_LIBRARY_PATH'] = ':'.join(ldpaths)

    @exec_on_firefox_dir()
    def get_instance(self, *args, **kwargs):
        if not self.FIREFOX:
            self.FIREFOX = mozrunner.get_moz_from_settings()
        return self.FIREFOX

    @exec_on_firefox_dir()
    def start_ff(self, *args, **kwargs):
        if not self.FIREFOX:
            self.FIREFOX = self.get_instance(*args, **kwargs)
            self.FIREFOX.start()
            time.sleep(3)
        return self.FIREFOX

    @exec_on_firefox_dir()
    def stop_ff(self, *args, **kwargs):
        if self.FIREFOX:
            self.FIREFOX.kill(signal.SIGKILL)
            del self.FIREFOX
            self.FIREFOX = None

    def restart_ff(self, *args, **kwargs):
        self.stop_ff(*args, **kwargs)
        return self.start_ff(*args, **kwargs)

    def run(self):
        return self.start_ff()

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
        self.ff_host = self._config._sections.get(
            'collective.anonymousbrowser' , {}).get(
                'host', host).strip()
        self.ff_port = self._config._sections.get(
            'collective.anonymousbrowser' , {}).get(
                'port', port).strip()
        self.ps_entry = self._config._sections.get(
            'collective.anonymousbrowser' , {}).get(
                'ps-entry', 'firefox').strip()
        self.MOZILLA_BINARY = self._config._sections.get(
            'collective.anonymousbrowser' , {}
        ).get(
            'firefox',
            os.environ.get('FIREFOX', '')
        ).strip()
        self.MOZILLA_DEFAULT_PROFILE = self._config._sections.get(
            'collective.anonymousbrowser' , {}
        ).get(
            'firefox-profile',
            os.environ.get('FIREFOX_PROFILE', '')
        ).strip()
        self.mozrunner_args = {}
        for item in 'MOZILLA_BINARY', 'MOZILLA_DEFAULT_PROFILE':
            value = getattr(self, item)
            if value:
                self.mozrunner_args[item] = value
        self.firefox_thread = FirefoxThread(**self.mozrunner_args)
        self.start_ff()
        if url is not None:
            self.open(url)
        self._enable_setattr_errors = False

    def browser_open(self, url, data=None):
        self.firefox_thread.start_ff()
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
        self.telnet.write("\n;\n")
        if not getattr(self, '_prompt', None):
            a, g, c = self.expect()
            self._prompt = re.sub('> .*', '', g.group())
        return getattr(self, '_prompt', 'repl')

    def start_ff(self):
        moz = self.firefox_thread.start_ff()
        #self.init_repl(self.ff_host, self.ff_port)
        retry = 60
        while retry:
            retry -= 1
            time.sleep(1)
            try:
                self.init_repl(self.ff_host, self.ff_port)
                retry = False
            except Exception, e:
                if not retry:
                    raise
        return moz

    def stop_ff(self):
        self.quit_mozrepl()
        self.firefox_thread.stop_ff(**self.mozrunner_args)

    def restart_ff(self):
        self.stop_ff()
        return self.start_ff()

    def home(self):
        self.execute("%s.home()" % self.getPrompt())

    def quit_mozrepl(self):
        self._prompt = None
        try:
            self.telnet.close()
        except Exception, e:
            pass

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

    def load_file(self, file_path):
        # for local addresses, just load directly the file, its really faster
        hosts = socket.gethostbyaddr(
            socket.getaddrinfo(self.telnet.host, 0)[0][4][0]
        )[1]
        if 'localhost' in hosts:
            self.telnet.write('repl.load("file://%s")' % file_path)
        else:
            for line in open(file_path, 'r'):
                self.telnet.write(line)
        self.expect([PROMPT, CONTINUATION_PROMPT])

    def execute(self, js):
        if not js.strip():
            return
        if not js.endswith('\n'):
            js = js + '\n'
        # wipe the line from previous dusts in the channel
        self.telnet.write("\n;\n")
        #print self.telnet.read_until('MARKER', self.timeout)
        self.expect()
        self.telnet.write(js)
        i, match, text = self.expect()
        if '!!!' in text: raise Exception('FAILED: ' + text + ' in ' + js)
        result = text.rsplit('\n', 1)
        if len(result) == 1:
            return None
        if result[0].startswith('"') and result[0].endswith('"'):
            return result[0][1:-1]
        return result[0]

    @property
    def contents(self):
        base, sub = self.execute('content.document.contentType').split('/')
        command = 'tb_get_contents()'
        #if base == 'text' and 'html' not in sub:
        #    command = "content.document.getElementsByTagName('pre')[0].innerHTML"
        return self.execute(command)

# vim:set et sts=4 ts=4 tw=80:
