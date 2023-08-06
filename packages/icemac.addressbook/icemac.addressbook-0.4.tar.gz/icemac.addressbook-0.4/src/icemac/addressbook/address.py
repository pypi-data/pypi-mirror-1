# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: address.py 997 2009-02-03 16:58:46Z mac $

import persistent
import zope.container.contained
import zope.interface
import zope.schema.fieldproperty

import icemac.addressbook.interfaces

from icemac.addressbook.i18n import MessageFactory as _


class PostalAddress(
    persistent.Persistent, zope.container.contained.Contained):
    "A postal address."

    zope.interface.implements(icemac.addressbook.interfaces.IPostalAddress)

    kind = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPostalAddress['kind'])
    address_prefix = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPostalAddress['address_prefix'])
    street = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPostalAddress['street'])
    city = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPostalAddress['city'])
    zip = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPostalAddress['zip'])
    state = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPostalAddress['state'])
    country = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPostalAddress['country'])
    notes = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPostalAddress['notes'])


def get_kind_title(obj, iface):
    """Get the title for the kind attribute of an object.

    iface: ... interface, used for look up title of kind's value
    """

    if obj.kind is None:
        title = _(u'unknown')
    else:
        title = zope.component.getMultiAdapter(
            (iface['kind'], obj.kind), icemac.addressbook.interfaces.ITitle)
    return title


@zope.component.adapter(icemac.addressbook.interfaces.IPostalAddress)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def postal_address_title(address):
    """Title of a postal address."""
    title = get_kind_title(
        address, icemac.addressbook.interfaces.IPostalAddress)
    values = [icemac.addressbook.interfaces.ITitle(getattr(address, x))
              for x in ('address_prefix', 'street', 'zip', 'city', 'state',
                        'country')
              if getattr(address, x)]
    if values:
        title += ': ' + ', '.join(values)
    return title

class EMailAddress(
    persistent.Persistent, zope.container.contained.Contained):
    """An e-mail address."""

    zope.interface.implements(icemac.addressbook.interfaces.IEMailAddress)

    kind = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IEMailAddress['kind'])
    email = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IEMailAddress['email'])
    notes = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IEMailAddress['notes'])


@zope.component.adapter(icemac.addressbook.interfaces.IEMailAddress)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def email_address_title(email):
    """Title of an e-mail address."""
    title = get_kind_title(email, icemac.addressbook.interfaces.IEMailAddress)
    if email.email:
        title += ': %s' % email.email
    return title


class HomePageAddress(
    persistent.Persistent, zope.container.contained.Contained):
    """A home page address."""

    zope.interface.implements(icemac.addressbook.interfaces.IHomePageAddress)

    kind = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IHomePageAddress['kind'])
    url = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IHomePageAddress['url'])
    notes = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IHomePageAddress['notes'])


@zope.component.adapter(icemac.addressbook.interfaces.IHomePageAddress)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def home_page_address_title(hp):
    """Title of a home page address."""
    title = get_kind_title(hp, icemac.addressbook.interfaces.IHomePageAddress)
    if hp.url:
        title += ': %s' % hp.url
    return title


class PhoneNumber(
    persistent.Persistent, zope.container.contained.Contained):
    """A phone number."""

    zope.interface.implements(icemac.addressbook.interfaces.IPhoneNumber)

    kind = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPhoneNumber['kind'])
    number = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPhoneNumber['number'])
    notes = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPhoneNumber['notes'])


@zope.component.adapter(icemac.addressbook.interfaces.IPhoneNumber)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def phone_number_title(tel):
    """Title of a phone number."""
    title = get_kind_title(tel, icemac.addressbook.interfaces.IPhoneNumber)
    if tel.number:
        title += ': %s' % tel.number
    return title


interface_title_prefix_class_mapping = (
    (icemac.addressbook.interfaces.IPostalAddress, u'postal address',
     'postal_address', PostalAddress),
    (icemac.addressbook.interfaces.IPhoneNumber, u'phone number',
     'phone_number', PhoneNumber),
    (icemac.addressbook.interfaces.IEMailAddress, u'e-mail address',
     'email_address', EMailAddress),
    (icemac.addressbook.interfaces.IHomePageAddress, u'home page address',
     'home_page_address', HomePageAddress),
    )


def object_to_prefix(obj):
    """Convert an object to its prefix."""
    for interface, d, prefix, d in interface_title_prefix_class_mapping:
        if interface.providedBy(obj):
            return prefix
    raise KeyError(obj)


def object_to_title(obj):
    """Convert an object to its title."""
    for interface, title, d, d in interface_title_prefix_class_mapping:
        if interface.providedBy(obj):
            return title
    raise KeyError(obj)


def object_to_class(obj):
    """Convert an object to its class."""
    for interface, d, d, class_ in interface_title_prefix_class_mapping:
        if interface.providedBy(obj):
            return class_
    raise KeyError(obj)
