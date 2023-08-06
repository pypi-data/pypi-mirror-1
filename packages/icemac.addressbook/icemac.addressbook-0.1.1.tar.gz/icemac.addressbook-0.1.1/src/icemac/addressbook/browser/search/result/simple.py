# -*- coding: utf-8 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: simple.py 755 2008-10-26 16:24:34Z mac $

import z3c.table.table
import z3c.table.column
import zope.viewlet.viewlet

import icemac.addressbook.interfaces

from icemac.addressbook.i18n import MessageFactory as _


class PersonTable(zope.viewlet.viewlet.ViewletBase, z3c.table.table.Table): 
    "Person table viewlet."

    def update(self):
        self.result = self.__parent__.result
        if self.result is not None:
            # only render table when a search happend
            z3c.table.table.Table.update(self)

    @property
    def values(self):
        return self.result
        

class CheckBoxColumn(z3c.table.column.CheckBoxColumn): 

    header = u''
    weight = 1

    def getItemKey(self, item):
        return 'persons:list'

    def isSelected(self, item):
        if self.request.get(self.getItemKey(item), None) is None:
            # not in request, return default: selected
            return True
        return super(CheckBoxColumn, self).isSelected(item)


class LinkNameColumn(z3c.table.column.LinkColumn): 

    header = _(u'Name')
    weight = 2

    def getLinkContent(self, item):
        return icemac.addressbook.interfaces.ITitle(item)
