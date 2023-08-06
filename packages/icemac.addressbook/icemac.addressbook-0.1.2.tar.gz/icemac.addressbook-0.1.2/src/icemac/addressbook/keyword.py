# -*- coding: latin-1 -*-
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: keyword.py 777 2008-11-02 20:33:19Z mac $

import persistent
import zope.app.container.btree
import zope.app.container.contained
import zope.interface
import zope.schema.fieldproperty

import icemac.addressbook.interfaces

from icemac.addressbook.i18n import MessageFactory as _


class KeywordContainer(zope.app.container.btree.BTreeContainer):
    "A container for keywords."
    zope.interface.implements(icemac.addressbook.interfaces.IKeywords)
    
    def get_keywords(self):
        return sorted(self.values(), key=lambda x: x.title)

    def get_titles(self):
        return [x.title for x in self.get_keywords()]


class Keyword(persistent.Persistent, zope.app.container.contained.Contained):
    "A keyword."
    zope.interface.implements(icemac.addressbook.interfaces.IKeyword)

    title = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IKeyword['title'])
    notes = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IKeyword['notes'])


@zope.component.adapter(icemac.addressbook.interfaces.IKeyword)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def title(keyword):
    return keyword.title


def uniqueTitles(obj, event):
    if getattr(obj, '__parent__', None) is None:
        return
    container = obj.__parent__
    titles = [x.title for x in container.values()]
    if len(titles) != len(set(titles)):
        raise zope.interface.Invalid(_(u'This keyword already exists.'))
