# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: evolve4.py 1075 2009-03-21 09:29:00Z mac $

__docformat__ = "reStructuredText"

import zope.app.zopeappgenerations

generation = 4


def evolve(context):
    """Update the root folder to be a ``zope.site.folder.Folder`` instead of
       ``zope.app.folder.folder.Folder``.
    """
    root = zope.app.zopeappgenerations.getRootFolder(context)
    context.connection.root()._p_changed = True
    root._p_changed = True
