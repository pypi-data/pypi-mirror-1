# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: add.py 235 2009-01-02 12:47:38Z mac $

import icemac.addressbook.interfaces
import icemac.addressbook.browser.base
import icemac.addressbook.addressbook
from icemac.addressbook.i18n import MessageFactory as _


class AddForm(icemac.addressbook.browser.base.BaseAddForm):
    
    label = _(u'Add new address book')
    interface = icemac.addressbook.interfaces.IAddressBook
    class_ = icemac.addressbook.addressbook.AddressBook
    next_url = 'object'
