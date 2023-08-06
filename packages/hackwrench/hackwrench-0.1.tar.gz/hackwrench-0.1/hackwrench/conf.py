#!/usr/bin/env python
# coding: utf-8
# vim: ai ts=4 sts=4 et sw=4
import os
import gconf

class Conf(object):
    home_url = 'file://%s' % os.path.join(os.path.realpath(os.path.dirname(__file__)),'about.html')
    new_tab_show_home = True
    always_show_tabs = False
    tabs_on_top = True
    search = 'http://google.com/search?q=%s'
    search_name = 'google'
    download_manager = 'uget-gtk %s'
    user_agent = "default"

    def __init__(self):
        if not os.path.exists(os.path.expanduser('~/.hackwrench/favicons')):
            os.makedirs(os.path.expanduser('~/.hackwrench/favicons'))
        if not os.path.exists(os.path.expanduser('~/.hackwrench/userscripts')):
            os.makedirs(os.path.expanduser('~/.hackwrench/userscripts'))
        conf = gconf.Client()
        pref = '/apps/hackwrench'
        types = self.__class__.__dict__
        for e in conf.all_entries(pref):
            if e.value:
                k = e.key.split('/')[-1]
                if type(types.get(k)) == int:
                    setattr(self, k, e.value.get_int())
                elif type(types.get(k)) == bool:
                    setattr(self, k, e.value.get_bool())
                elif isinstance(types.get(k), basestring):
                    setattr(self, k, e.value.get_string())

    def write(self):
        conf = gconf.Client()
        pref = '/apps/hackwrench/'
        types = self.__class__.__dict__
        for k,v in types.items():
            if type(v) == int:
                conf.set_int(pref+k, v)
            elif type(v) == bool:
                conf.set_bool(pref+k, v)
            elif isinstance(v, basestring):
                conf.set_string(pref+k, v)



