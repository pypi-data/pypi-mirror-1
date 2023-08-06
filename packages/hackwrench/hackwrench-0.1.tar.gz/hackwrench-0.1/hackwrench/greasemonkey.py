#!/usr/bin/env python
# coding: utf-8
# vim: ai ts=4 sts=4 et sw=4
from fnmatch import fnmatch
from os import path
from glob import glob
import webkit
from urllib import urlretrieve
import gobject

class MonkeyMixIn(object):
    def __init__(self):
        webkit.WebView.__init__(self)
        self.connect("load-finished", self._apply_monkey)
    def _apply_monkey(self, view, frame=None):
        for f in glob(path.expanduser('~/.hackwrench/userscripts/*user.js')):
            for line in open(f):
                if '@include' in line or '@match' in line:
                    line = line.replace('@match','@include')
                    mask = line.split('@include',1)[1].strip()
                    if fnmatch(frame.get_uri(), mask):
                        print 'userscript %s match(%s,%s)' % (f, frame.get_uri(), mask)
                        self.execute_script(open(f).read())
                        break
                    elif '==/UserScript==' in line:
                        break
                        
    def install_userscript(self, url):
        save_to = path.expanduser('~/.hackwrench/userscripts/%s' % path.basename(url))
        print 'installing user script', url, save_to
        urlretrieve(url, save_to)







