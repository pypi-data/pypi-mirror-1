# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: menu.py 1069 2009-03-20 17:23:09Z mac $

import zope.viewlet.manager
import z3c.menu.ready2go
import z3c.menu.ready2go.manager

MainMenu = zope.viewlet.manager.ViewletManager(
    'main', z3c.menu.ready2go.ISiteMenu,
    bases=(z3c.menu.ready2go.manager.MenuManager,))

AddMenu = zope.viewlet.manager.ViewletManager(
    'add', z3c.menu.ready2go.IAddMenu,
    bases=(z3c.menu.ready2go.manager.MenuManager,))
