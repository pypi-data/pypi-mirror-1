# -*- coding: latin-1 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: menu.py 700 2008-10-07 16:20:39Z mac $

import zope.viewlet.manager
import z3c.menu.ready2go
import z3c.menu.ready2go.manager

MainMenu = zope.viewlet.manager.ViewletManager(
    'left', z3c.menu.ready2go.ISiteMenu, 
    bases=(z3c.menu.ready2go.manager.MenuManager,))

AddMenu = zope.viewlet.manager.ViewletManager(
    'left', z3c.menu.ready2go.IAddMenu,
    bases=(z3c.menu.ready2go.manager.MenuManager,))
