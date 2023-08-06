# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: interfaces.py 235 2009-01-02 12:47:38Z mac $

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
