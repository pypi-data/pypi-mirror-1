# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: adapter.py 918 2009-01-02 19:35:06Z mac $

import zope.interface
import zope.schema.interfaces

import icemac.addressbook.interfaces


@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def gocept_country_title(obj):
    """Title for objects from gocept.country."""
    return obj.name


@zope.component.adapter(zope.schema.interfaces.IChoice,
                        zope.interface.Interface)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def title_for_choice_value(field, value):
    "Get the title for a value of a field which is a Choice."
    factory = field.source.factory
    return factory.getTitle(value)


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def default_title(obj):
    "Default title adapter which returns str represantation of obj."
    if isinstance(obj, basestring):
        return obj
    return str(obj)
