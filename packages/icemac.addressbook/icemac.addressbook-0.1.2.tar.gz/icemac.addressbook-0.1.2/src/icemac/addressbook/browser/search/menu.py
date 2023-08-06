# -*- coding: latin-1 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: menu.py 707 2008-10-11 11:18:19Z mac $

import zope.viewlet.manager
import z3c.menu.ready2go
import z3c.menu.ready2go.manager


SearchMenu = zope.viewlet.manager.ViewletManager(
    'left', z3c.menu.ready2go.IContextMenu, 
    bases=(z3c.menu.ready2go.manager.MenuManager,))
