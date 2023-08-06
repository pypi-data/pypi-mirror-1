# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: menu.py 913 2009-01-02 12:47:38Z mac $

import zope.viewlet.manager
import z3c.menu.ready2go
import z3c.menu.ready2go.manager

MainMenu = zope.viewlet.manager.ViewletManager(
    'left', z3c.menu.ready2go.ISiteMenu, 
    bases=(z3c.menu.ready2go.manager.MenuManager,))

AddMenu = zope.viewlet.manager.ViewletManager(
    'left', z3c.menu.ready2go.IAddMenu,
    bases=(z3c.menu.ready2go.manager.MenuManager,))
