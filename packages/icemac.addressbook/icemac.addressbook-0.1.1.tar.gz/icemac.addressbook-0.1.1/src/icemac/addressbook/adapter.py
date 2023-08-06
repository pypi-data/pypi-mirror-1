# -*- coding: latin-1 -*-
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: adapter.py 719 2008-10-14 19:15:06Z mac $

import zope.interface

import icemac.addressbook.interfaces


@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def gocept_country_title(obj):
    """Title for objects from gocept.country."""
    return obj.name
