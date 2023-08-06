#!/usr/bin/env python
# coding: utf-8
# vim: ai ts=4 sts=4 et sw=4

class WebViewJsMixIn(object):
"""
usage example
class MyWebView(webkit.WebView, WebViewJsMixIn):
    def get_selection(self, callback, *args):
        self.eval("document.getSelection()", self.got_selection_cb)

    def got_selection_cb(self, selection):
        print selection
"""

    def _got_response_cb(self, view, msg, n, something, callback, *args):
        self.disconnect(self._got_response)
        callback(msg.strip(), *args)
        view.stop_emission('console-message')

    def eval(self, js, callback, *args):
        self._got_response = self.connect("console-message", self._got_response_cb, callback, *args)
        self.execute_script('console.log(%s);' % js)



