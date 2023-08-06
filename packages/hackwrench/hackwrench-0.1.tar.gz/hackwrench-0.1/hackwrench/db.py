#!/usr/bin/env python
# coding: utf-8
# vim: ai ts=4 sts=4 et sw=4
import os
from os import path
from collections import deque

import gtk


class FileList(list):
    def __init__(self):
        super(FileList, self).__init__()
        self.path = path.expanduser(self.path)
        if not path.exists(path.dirname(self.path)):
            os.makedirs(path.dirname(self.path))
        if path.exists(self.path):
            for line in open(self.path):
                line = line.strip().split(None, len(self.columns)-1)
                if len(line) == len(self.columns):
                    super(FileList, self).append(line)
    def append(self, arg):
        super(FileList, self).append(arg)
        print >>open(self.path, 'a'), '\t'.join(arg)

class FileListStore(gtk.ListStore):
    def __init__(self):
        super(FileListStore, self).__init__(*self.columns)
        if not hasattr(self,'uniq'):
            self.uniq = gtk.ListStore(str)
        self.path = path.expanduser(self.path)
        if not path.exists(path.dirname(self.path)):
            os.makedirs(path.dirname(self.path))
        if path.exists(self.path):
            for line in open(self.path):
                line = line.strip().split(None, len(self.columns)-1)
                if len(line) == len(self.columns):
                    self.append(line, False)
    def append(self, arg, write=True):
        super(FileListStore, self).append(arg)
        if arg[0] not in [row[0] for row in self.uniq]:
            self.uniq.append((arg[0],))
        if write:
            print >>open(self.path, 'a'), '\t'.join(x or 'null' for x in arg)


class History(FileListStore):
    path = '~/.hackwrench/history'
    columns = (str,str,str)

    #def __init__(self):
    #    self.uniq = gtk.ListStore(str,str)
    #    super(History, self).__init__()

    def top(self, num):
        urls = [row[0] for row in self]
        res = []
        for url in sorted(set(urls), key=lambda x: urls.count(x), reverse=True)[:num]:
            for row in self:
                if row[0] == url:
                    res.append({'url': url, 'title': row[2], 'favicon': row[1]})
                    break
        return res

    def last(self, num):
        return map(list, reversed(deque(self,num)))

    #def append(self, arg, write=True):
    #    gtk.ListStore.append(self, arg)
    #    if arg[0] not in [row[0] for row in self.uniq]:
    #        self.uniq.append((arg[0],arg[0]))
    #        self.uniq.append((arg[2],arg[0]))
    #    if write:
    #        print >>open(self.path, 'a'), '\t'.join(x or 'null' for x in arg)





class SearchHistory(FileListStore):
    path = '~/.hackwrench/search_history'
    columns = (str,)

class Bookmarks(FileList):
    path = '~/.hackwrench/bookmarks'
    columns = (str,str)
    
    def remove(self, url):
        for row in self:
            if url == row[0]:
                super(Bookmarks, self).remove(row)
                lines = open(self.path).readlines()
                f = open(self.path, 'w')
                for line in lines:
                    if line.strip():
                        if line.strip().split(None,1)[0] != url:
                            print >>f, line
                f.close()
                break
        else:
            raise KeyError('%r not in %r' % (arg, self))

    def __contains__(self, arg):
        return arg in (url for url, title in self)





