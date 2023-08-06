# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: root.py 688 2009-11-21 15:07:47Z icemac $

import icemac.addressbook.interfaces
import z3c.pagelet.browser
import zope.size.interfaces


class FrontPage(z3c.pagelet.browser.BrowserPagelet):
    """Pagelet for the front page."""

    def getAddressBooks(self):
        return [value
                for value in self.context.values()
                if icemac.addressbook.interfaces.IAddressBook.providedBy(value)
                ]

    def countEntries(self, address_book):
        return zope.size.interfaces.ISized(address_book).sizeForDisplay()
