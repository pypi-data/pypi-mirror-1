# -*- coding: latin-1 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: edit.py 782 2008-11-06 19:29:27Z mac $

import icemac.addressbook.interfaces
import icemac.addressbook.browser.base
from icemac.addressbook.i18n import MessageFactory as _


class EditForm(icemac.addressbook.browser.base.BaseEditFormWithCancel):

    label = _(u'Edit address book data')
    interface = icemac.addressbook.interfaces.IAddressBook
    next_url = 'object'
    next_view = '@@edit.html'
