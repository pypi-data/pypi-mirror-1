# -*- coding: latin-1 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: interfaces.py 654 2008-09-20 18:50:21Z mac $

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


class IMainMenu(z3c.menu.ready2go.ISiteMenu):
    """Main menu."""


class IAddMenu(z3c.menu.ready2go.IAddMenu):
    """Add menu."""
