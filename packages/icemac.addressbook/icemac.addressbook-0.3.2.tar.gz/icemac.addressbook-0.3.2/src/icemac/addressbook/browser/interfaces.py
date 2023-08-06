# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: interfaces.py 1069 2009-03-20 17:23:09Z mac $

import z3c.form.interfaces
import z3c.formui.interfaces
import z3c.layer.pagelet
import z3c.menu.ready2go


class IAddressBookLayer(
    z3c.form.interfaces.IFormLayer, z3c.layer.pagelet.IPageletBrowserLayer):
    """Address book browser layer with form support."""


class IAddressBookBrowserSkin(
    z3c.formui.interfaces.IDivFormLayer, IAddressBookLayer):
    """The address book browser skin using the div-based layout."""
