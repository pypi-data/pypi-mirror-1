# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: table.py 1184 2009-05-12 18:39:39Z mac $

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.interfaces
import icemac.truncatetext
import z3c.table.column
import z3c.table.table


# Columns

class TitleLinkColumn(z3c.table.column.LinkColumn):
    """Column containing the title of an object and a link to the object."""

    header = _(u'Name')
    weight = 2

    def getSortKey(self, item):
        return icemac.addressbook.interfaces.ITitle(item)

    def getLinkContent(self, item):
        return icemac.addressbook.interfaces.ITitle(item)


class TruncatedContentColumn(z3c.table.column.GetAttrColumn):

    length = 20
    attrName = None

    def getValue(self, obj):
        value = super(TruncatedContentColumn, self).getValue(obj)
        return icemac.truncatetext.truncate(value, self.length)


# Tables

class Table(z3c.table.table.Table):
    "Table which supports a no-rows-found message."

    no_rows_message = u'' # Set at subclass.

    def renderTable(self):
        if self.rows:
            return super(Table, self).renderTable()
        return self.no_rows_message
