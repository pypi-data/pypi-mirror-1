#!/usr/bin/env python
# coding: utf-8
# vim: ai ts=4 sts=4 et sw=4
from gettext import gettext as _
import os
from os import path
from urllib import urlencode
from functools import partial

import gobject
import gtk
from gtk import gdk
import pango
import gio
import webkit
from inspector import Inspector

from browser import BrowserPage
import db
from conf import Conf

def foo(*args):
    print args

def comp_match(completion, key, iter):
    model = completion.get_model()
    text = model.get_value(iter, 0)
    return text and key in text

class TabLabel (gtk.HBox):
    """A class for Tab labels"""

    __gsignals__ = {"close": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,)),}

    def __init__(self, title):
        """initialize the tab label"""
        gtk.HBox.__init__(self, False, 4)
        self.title = title
        self.label = gtk.Label(title)
        self.label.props.max_width_chars = 30
        self.label.set_ellipsize(pango.ELLIPSIZE_MIDDLE)
        self.label.set_alignment(0.0, 0.5)

        self.icon = gtk.image_new_from_stock(gtk.STOCK_ORIENTATION_PORTRAIT, gtk.ICON_SIZE_MENU)
        close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close_button = gtk.Button()
        close_button.set_relief(gtk.RELIEF_NONE)
        close_button.connect("clicked", self.close_tab)
        close_button.add(close_image)
        self.pack_start(self.icon, False, False, 0)
        self.pack_start(self.label, True, True, 0)
        self.pack_start(close_button, False, False, 0)

        self.set_data("icon", self.icon)
        self.set_data("label", self.label)
        self.set_data("close-button", close_button)
        self.connect("style-set", self.style_set_cb)

    def style_set_cb(self, tab_label, style):
        context = tab_label.get_pango_context()
        metrics = context.get_metrics(tab_label.style.font_desc, context.get_language())
        char_width = metrics.get_approximate_digit_width()
        (width, height) = gtk.icon_size_lookup_for_settings(tab_label.get_settings(), gtk.ICON_SIZE_MENU)
        tab_label.set_size_request(20 * pango.PIXELS(char_width) + 2 * width, -1)
        button = tab_label.get_data("close-button")
        button.set_size_request(width + 4, height + 4)

    def set_label_text(self, text):
        """sets the text of this label"""
        self.title = text or ''
        self.label.set_label(self.title)

    def close_tab(self, *args):
        self.emit("close", self.child)

class Tab(gtk.VBox):
    def __init__(self, win, url=None):
        super(Tab, self).__init__()
        self.icon = None
        self.loading = False
        self.win = win
        to_end = False
        # create the tab
        self.label = TabLabel(url or 'about:blank')
        self.label.connect("close", self.close_tab)
        self.label.show_all()
        if isinstance(url, basestring) or url is None:
            if url is None:
                to_end = True
                if win.app.conf.new_tab_show_home:
                    url = win.app.conf.home_url
                else:
                    url = 'about:blank'
            self.browser = BrowserPage(self, win.browser_actions)
            self.browser.home = url == win.app.conf.home_url
            self.browser.open(url)
        else:
            self.label.set_label_text(url.title)
            self.browser = url
            self.browser.tab = self
        self.inspector = Inspector(self.browser.get_web_inspector())

        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        self.scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        self.scrolled_window.add(self.browser)
        self.scrolled_window.show_all()
        self.pack_end(self.scrolled_window)

        self.label.child = self.scrolled_window

        new_tab_number = to_end and -1 or win.notebook.props.page+1
        win.notebook.insert_page(self, self.label, new_tab_number)
        win.notebook.set_tab_reorderable(self, True)
        win.notebook.set_tab_detachable(self, True)
        win.notebook.set_tab_label_packing(self, False, False, gtk.PACK_START)
        win.notebook.set_tab_label(self, self.label)

        # hide the tab if there's only one
        win.notebook.set_show_tabs(win.notebook.get_n_pages() > 1)

        win.notebook.show_all()
        if to_end:
            win.notebook.set_current_page(new_tab_number)

    def close_tab (self, label, child):
        page_num = self.win.notebook.page_num(self)
        if page_num != -1:
            self.browser.destroy()
            self.win.notebook.remove_page(page_num)
        self.win.notebook.set_show_tabs(self.win.notebook.get_n_pages() > 1)

    def update_toolbar(self):
        if self.browser and self.win.active_tab == self:
            self.win.back.set_visible(self.browser.can_go_back())
            if self.browser.can_go_back():
                self.win.toolbar_back.show()
            else:
                self.win.toolbar_back.hide()
            if self.loading:
                self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
                self.browser.set_cursor('wait')
                self.win.toolbar_stop.show()
                self.win.toolbar_reload.hide()
            else:
                self.window.set_cursor(None)
                self.browser.set_cursor(None)
                self.win.location.set_progress_fraction(0.0)
                self.win.toolbar_stop.hide()
                self.win.toolbar_reload.show()
            if self.browser.url in self.win.app.bookmarks:
                self.win.location.set_icon_from_pixbuf(gtk.ENTRY_ICON_PRIMARY,gtk.gdk.pixbuf_new_from_file(path.join(path.dirname(__file__),'favorite1.png')))
            else:
                self.win.location.set_icon_from_pixbuf(gtk.ENTRY_ICON_PRIMARY,gtk.gdk.pixbuf_new_from_file(path.join(path.dirname(__file__),'favorite0.png')))


class BrowserWindow(gtk.Builder):
    def __init__(self, app, web_view=None):
        super(BrowserWindow, self).__init__()
        self.app = app
        self.add_from_file(path.join(path.dirname(__file__),'browser.ui'))
        #self._default_icon = self.location.get_icon_pixbuf(gtk.ENTRY_ICON_PRIMARY)
        self.connect_signals(self)

        self.location_comp.set_model(self.app.history.uniq)
        
        self.location.set_completion(self.location_comp)
        self.location_comp.set_text_column(0)
        self.location_comp.set_match_func(comp_match)

        self.browser_actions = [m.get_action() for m in \
                                self.popup_browser.get_children()]
        self.active_tab = None
        self.view = None
        if web_view:
            self.view = web_view
            self.active_tab = self.new_tab(web_view)
        else:
            self.active_tab = self.new_tab(self.app.conf.home_url)
            self.view = self.active_tab.browser
        self.bookmark_ids = {}
        self.load_bookmarks()
        if self.app.conf.always_show_tabs:
            self.notebook.set_show_tabs(True)

    def add_bookmark(self, url, title):
        id = self.uimanager1.new_merge_id()
        label = '%s%s' % (title[:20], len(title)>20 and '..' or '')
        action = [('bookmark%d' % id, None, label, None, title, lambda act: self.active_tab.browser.open(act.url))]
        self.ag_bookmarks.add_actions(action)
        action = self.ag_bookmarks.get_action('bookmark%d' % id)
        #action.set_tool_item_type(gtk.ImageMenuItem)
        icon = self.app.icon_cache.get(url)
        if icon:
            action.set_gicon(gio.FileIcon(gio.File(icon)))
            action.set_label(' '+label)
        action.set_is_important(True)
        action.id = 4
        action.url = url
        #action.func = partial(self.new_tab, url)
        self.uimanager1.add_ui(id, 'ui/toolbar_bookmarks', 'toolbar_bookmark%d'%id, 'bookmark%d'%id, gtk.UI_MANAGER_TOOLITEM, False)
        self.bookmark_ids[url] = id

    def remove_bookmark(self, url):
        id = self.bookmark_ids.pop(url)
        self.ag_bookmarks.remove_action(self.ag_bookmarks.get_action('bookmark%d' % id))
        self.uimanager1.remove_ui(id)

    def load_bookmarks(self):
        for url, title in self.app.bookmarks:
            self.add_bookmark(url, title)

    def __getattr__(self, attr):
        obj = self.get_object(attr)
        if not obj:
            raise AttributeError('%r has no attribute %r' % (self,attr))
        setattr(self, attr, obj)
        return obj

    def new_tab_cb(self, *args):
        self.new_tab()

    def new_tab(self, url=None):
        return Tab(self, url)

    def go_cb(self, *args):
        url = self.location.get_text().strip()
        if path.exists(path.expanduser(url)):
            self.view.open('file://%s' % path.expanduser(url))
        elif '://' not in url and ' ' in url or not '.' in url:
        #        or len(url.split('/',1)[0].split('.')[-1])>4:
            self.view.search(url)
        else:
            if not '://' in url:
                url = 'http://%s' % url
            self.view.open(url)

    def match_selected_cb(self, completion, model, iter):
        completion.get_entry().set_text(model.get_value(iter,0).strip())
        completion.get_entry().emit('activate')

    def back_cb(self, *args):
        self.view.go_back()

    def bookmark_cb(self, *args):
        if not self.view.url:
            return
        if self.view.url in self.app.bookmarks:
            self.app.bookmarks.remove(self.view.url)
            self.remove_bookmark(self.view.url)
        else:
            self.app.bookmarks.append((self.view.url, self.active_tab.label.title))
            self.add_bookmark(self.view.url, self.active_tab.label.title)
        self.active_tab.update_toolbar()

    def new_window_cb(self, *args):
        self.app.new_window()

    def print_cb(self, *args):
        self.view.print_cb(*args)

    def destroy(self, *args):
        for i in xrange(self.notebook.get_n_pages(),0,-1):
            child = self.notebook.get_nth_page(i)
            if child:
                child.browser.destroy()
        self.app.windows.remove(self)
        self.main.destroy()
        if not self.app.windows:
            self.app.quit()

    @property
    def _view(self):
        page_num = self.notebook.get_current_page()
        if page_num >= 0:
            self.active_tab = self.notebook.get_nth_page(page_num)
            self.view = self.active_tab.browser
        else:
            self.active_tab = self.view = None
        return self.view

    @property
    def tabs(self):
        return self.notebook.get_children()

    def switch_page_cb (self, notebook, page, page_num):
        self.active_tab = self.notebook.get_nth_page(page_num)
        #self.menu.parent.remove(self.menu)
        if self.app.conf.tabs_on_top:
            self.toolbar.parent.remove(self.toolbar)
            self.toolbar_bookmarks.parent.remove(self.toolbar_bookmarks)
            self.active_tab.pack_start(self.toolbar,False,False)
            self.active_tab.pack_start(self.toolbar_bookmarks,False,False)
        self.view = self.active_tab.browser
        self.back.set_visible(self.view.can_go_back())
        if self.view.can_go_back():
            self.toolbar_back.show()
        else:
            self.toolbar_back.hide()
        self.location.set_text(self.view.url or '')
        self.main.set_title(self.view.title or self.view.url or '')
        #if self.view:
        #    self.active_tab.browser._view_load_finished_cb(self.view)
        self.active_tab.update_toolbar()

    def stop_cb(self, *args):
        self.view.stop_loading()

    def reload_cb(self, *args):
        self.view.reload()

    def search_cb(self, *args):
        self.view.search(self.query.get_text())
    
    def zoom_in_cb(self, *args):
        self.view.zoom_in()

    def zoom_out_cb(self, *args):
        self.view.zoom_out()

    def zoom_100_cb(self, *args):
        #if self.view.get_zoom_level() != 1.0:
        self.view.set_zoom_level(1.0)

    def quit_cb(self, *args):
        quit()

    def console_cb(self, *args):
        self.dlg_console.show_all()
        self.command.grab_focus()

    def command_cb(self, command):
        try:
            res = repr(eval(command.get_text()))+'\n'
        except Exception,e:
            res = repr(e)+'\n'
        command.set_text('')
        self.output.get_buffer().insert_at_cursor(res)

    def about_cb(self, *args):
        url = 'file://%s' % path.join(path.realpath(path.dirname(__file__)),'about.html')
        self.new_tab(url)

    def bookmark_menu_cb(self, *args):
        print args

    def focus_in_cb(self, *args):
        self.app.active_window = self

    def focus_out_cb(self, *args):
        self.app.active_window = None


class WebBrowser(object):
    def __init__(self):
        self.conf = Conf()
        self.active_window = None
        #gobject.timeout_add(500,lambda s: (True,foo(s.active_window)),self)
        self.windows = []
        self.history = db.History()
        self.search_history = db.SearchHistory()
        self.icon_cache = {}
        self.bookmarks = db.Bookmarks()
        for row in self.history:
            if row[1] and row[1]!='null':
                self.icon_cache[row[0]] = row[1]

        #if path.exists(path.expanduser('~/.hackwrench/history')):
        #    for line in open(path.expanduser('~/.hackwrench/history')):
        #        line = line.split(None,2)
        #        if len(line) == 3:
        #            self.history.append(line)
        #            if line[1]:
        #                self.icon_cache[line[0]] = line[1]
        #f_history = open(path.expanduser('~/.hackwrench/history'),'a')

        #if path.exists(path.expanduser('~/.hackwrench/search_history')):
        #    for line in open(path.expanduser('~/.hackwrench/search_history')):
        #        self.search_history.append((line,))
        #f_search = open(path.expanduser('~/.hackwrench/search_history'),'a')

    def new_window(self, view=None):
        window = BrowserWindow(self, view)
        self.windows.append(window)
        return window

    def quit(self):
        for window in self.windows:
            window.destroy()
        self.conf.write()
        gtk.main_quit()

    def _write_history(self, model, path, iter, f):
        print >>f, '\t'.join(model.get_value(iter,i) or '' for i in xrange(model.get_n_columns()))
        f.flush()

if __name__ == "__main__":
    gobject.threads_init()
    webbrowser = WebBrowser()
    webbrowser.new_window()
    gtk.main()


