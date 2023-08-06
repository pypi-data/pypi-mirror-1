# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: utils.py 913 2009-01-02 12:47:38Z mac $

import zope.app.container.interfaces
import zope.event
import zope.lifecycleevent


def set_site(func):
    "Decorator which does the set-site-dance."
    def decorated(site, *args, **kw):
        old_site = zope.app.component.hooks.getSite()
        try:
            zope.app.component.hooks.setSite(site)
            return func(*args, **kw)
        finally:
            zope.app.component.hooks.setSite(old_site)
    return decorated


def create_obj(class_, *args, **kw):
    """Create an object of class and fire created event."""
    obj = class_(*args)
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
    for attrib, value in kw.items():
        setattr(obj, attrib, value)
    return obj


create_obj_with_set_site = set_site(create_obj)


def add(parent, obj):
    nc = zope.app.container.interfaces.INameChooser(parent)
    name = nc.chooseName('', obj)
    parent[name] = obj
    return name


def create_and_add(parent, class_, *args, **kw):
    obj = create_obj(class_, *args, **kw)
    return add(parent, obj)


create_and_add_with_set_site = set_site(create_and_add)


def iter_by_interface(container, interface):
    "Iterate a container and return only objects providing the specified iface."
    for obj in container.values():
        if interface.providedBy(obj):
            yield obj

