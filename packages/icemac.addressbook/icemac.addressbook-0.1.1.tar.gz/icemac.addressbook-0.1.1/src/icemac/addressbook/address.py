# -*- coding: latin-1 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: address.py 649 2008-09-18 19:24:01Z mac $

import persistent
import zope.app.container.contained
import zope.interface
import zope.schema.fieldproperty

import icemac.addressbook.interfaces

class PostalAddress(
    persistent.Persistent, zope.app.container.contained.Contained):
    "A postal address."

    zope.interface.implements(icemac.addressbook.interfaces.IPostalAddress)

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


class EMailAddress(
    persistent.Persistent, zope.app.container.contained.Contained):
    """An e-mail address.

    Let's test the e-mail address regex:
    
    >>> e = EMailAddress()

    Some failing examples first:

    >>> e.email = u'asdfg'
    Traceback (most recent call last):
    ConstraintNotSatisfied: asdfg
    >>> e.email = u'ich@'
    Traceback (most recent call last):
    ConstraintNotSatisfied: ich@
    >>> e.email = u'ich@goo@le.de'
    Traceback (most recent call last):
    ConstraintNotSatisfied: ich@goo@le.de
    >>> e.email = u'ich@local'
    Traceback (most recent call last):
    ConstraintNotSatisfied: ich@local
    >>> e.email = u'ich@local..de'
    Traceback (most recent call last):
    ConstraintNotSatisfied: ich@local..de
    >>> e.email = u'ich@local.de.'
    Traceback (most recent call last):
    ConstraintNotSatisfied: ich@local.de.

    Now some working examples:

    >>> e.email = u'ich@example.org'
    >>> e.email = u'ich+du@example.org'
    >>> e.email = u'ich=du@example.org'
    >>> e.email = u'ich_du@example.org'
    >>> e.email = u'ich+du@a.b.c.d.example.org'
    >>> e.email = u'ich+du@example.museum'

    """

    zope.interface.implements(icemac.addressbook.interfaces.IEMailAddress)

    kind = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IEMailAddress['kind'])
    email = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IEMailAddress['email'])
    notes = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IEMailAddress['notes'])


class HomePageAddress(
    persistent.Persistent, zope.app.container.contained.Contained):
    """A home page address.

    Let's test the URI constraint:
    
    >>> a = HomePageAddress()

    Some failing examples first:

    >>> a.url = 'asdfg'
    Traceback (most recent call last):
    InvalidURI: asdfg
    >>> a.url = 'www.example.com'
    Traceback (most recent call last):
    InvalidURI: www.example.com


    Now some working examples:

    >>> a.url = 'http://www.example.org'
    >>> a.url = 'http://www2.example.org'
    >>> a.url = 'http://a.b.c.d.example.org'
    >>> a.url = 'http://example.museum'

    """

    zope.interface.implements(icemac.addressbook.interfaces.IHomePageAddress)

    kind = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IHomePageAddress['kind'])
    url = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IHomePageAddress['url'])
    notes = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IHomePageAddress['notes'])


class PhoneNumber(
    persistent.Persistent, zope.app.container.contained.Contained):
    """A phone number."""

    zope.interface.implements(icemac.addressbook.interfaces.IPhoneNumber)

    kind = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPhoneNumber['kind'])
    number = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPhoneNumber['number'])
    notes = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPhoneNumber['notes'])
