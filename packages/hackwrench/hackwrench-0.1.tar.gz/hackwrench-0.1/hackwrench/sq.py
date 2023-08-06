#!/usr/bin/env python
# coding: utf-8
# vim: ai ts=4 sts=4 et sw=4

from sqlobject import *
from sqlobject.sqlbuilder import *
from formencode import validators

class Bookmark(SQLObject):
    title = StringCol(length=255)
    url = StringCol(alternateID=True, unique=True, validator=validators.URL, length=255)
    tags = RelatedJoin('Tag')

class Tag(SQLObject):
    name = StringCol(alternateID=True, unique=True, length=255)
    bookmarks = RelatedJoin('Bookmark')

def get_tag(name):
    try:
        return Tag(name=name)
    except dberrors.DuplicateEntryError:
        return Tag.byName(name)

class History(SQLObject):
    title = StringCol(length=255, notNone=False, default=None)
    url = StringCol(validator=validators.URL, length=255)
    time = DateTimeCol(default = DateTimeCol.now)

class Site(SQLObject):
    title = StringCol(length=255, notNone=False, default=None)
    url = StringCol(validator=validators.URL, length=255)
    visits = MultipleJoin('History')

class History(SQLObject):
    site = ForeignKey('Site')
    time = DateTimeCol(default = DateTimeCol.now)
#list(c.execute('select count(id) as cnt,site_id from history group by site_id order by cnt desc'))

sqlhub.processConnection = connectionForURI('sqlite:///tmp/hackwench.sqlite')

Bookmark.createTable(ifNotExists=True)
Tag.createTable(ifNotExists=True)
History.createTable(ifNotExists=True)




