# -*- coding: latin-1 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: interfaces.py 775 2008-11-01 14:41:29Z mac $

import z3c.menu.ready2go
import zope.interface
import zope.viewlet.interfaces


class ISearchMenu(z3c.menu.ready2go.ISiteMenu):
    """Search menu."""


class ISearchForm(zope.viewlet.interfaces.IViewletManager):
    """Search form manager."""


class ISearchResult(zope.viewlet.interfaces.IViewletManager):
    """Search form manager."""


class ISearch(zope.interface.Interface):
    """A search."""
    
    def search(**kw):
        """Search for given keyword arguments and return iterable of results."""
