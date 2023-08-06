# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: interfaces.py 459 2009-05-12 18:39:39Z mac $

import z3c.menu.ready2go


class IMainMenu(z3c.menu.ready2go.ISiteMenu):
    """Main menu."""


class IAddMenu(z3c.menu.ready2go.IAddMenu):
    """Add menu."""
