# -*- coding: latin-1 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: root.py 655 2008-09-20 19:08:13Z mac $

import z3c.pagelet.browser
import icemac.addressbook.interfaces


class FrontPage(z3c.pagelet.browser.BrowserPagelet):
    """Pagelet for the front page."""

    def getAddressBooks(self):
        for value in self.context.values():
            if icemac.addressbook.interfaces.IAddressBook.providedBy(value):
                yield value
