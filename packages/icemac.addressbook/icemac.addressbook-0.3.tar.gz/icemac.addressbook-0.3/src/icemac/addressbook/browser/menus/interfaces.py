# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: interfaces.py 1069 2009-03-20 17:23:09Z mac $

import z3c.form.interfaces
import z3c.formui.interfaces
import z3c.layer.pagelet
import z3c.menu.ready2go


class IMainMenu(z3c.menu.ready2go.ISiteMenu):
    """Main menu."""


class IAddMenu(z3c.menu.ready2go.IAddMenu):
    """Add menu."""
