# -*- coding: latin-1 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: interfaces.py 714 2008-10-12 18:41:05Z mac $

import gocept.country
import gocept.country.db
import re
import zope.interface
import zope.schema

import icemac.addressbook.sources
from icemac.addressbook.i18n import MessageFactory as _


class StateWithoutCountryError(zope.schema.ValidationError):
    __doc__ = _("""You can't select a state without selecting a country.""")

class StateCountryMismatchError(zope.schema.ValidationError):
    __doc__ = _(
        "You selected a state which does not belong to the selected country.")


class ITitle(zope.interface.Interface):
    """Title of an entity."""

    def __str__():
        """Return the title of the entity."""


class IAddressBook(zope.interface.Interface):
    """An address book."""

    keywords = zope.interface.Attribute(u'keywords collection (IKeywords).')

    title = zope.schema.TextLine(title=_(u'title'))
    notes = zope.schema.Text(title=_(u'notes'), required=False)


class IPerson(zope.interface.Interface):
    """A person."""

    first_name = zope.schema.TextLine(title=_(u'first name'), required=False)
    last_name = zope.schema.TextLine(title=_(u'last name'))
    birth_date = zope.schema.Date(title=_(u'birth date'), required=False)
    sex = zope.schema.Choice(
        title=_(u'sex'), source=icemac.addressbook.sources.SexSource(),
        required=False)
    keywords = zope.schema.Set(
        title=_('keywords'), required=False, 
        value_type=zope.schema.Choice(
            title=_('keywords'), 
            source=icemac.addressbook.sources.keyword_source))
    notes = zope.schema.Text(title=_(u'notes'), required=False)


class IPostalAddress(zope.interface.Interface):
    """A postal address."""

    street = zope.schema.Text(title=_(u'street'), required=False)
    city = zope.schema.TextLine(title=_(u'city'), required=False)
    zip = zope.schema.TextLine(title=_(u'zip'), required=False)
    country = zope.schema.Choice(
        title=_(u'country'), source=gocept.country.countries,
        required=False, default=gocept.country.db.Country('DE'))
    state = zope.schema.Choice(
        title=_(u'state'), required=False, 
        source=gocept.country.SubdivisionSource(country_code=['DE']))
    notes = zope.schema.Text(title=_(u'notes'), required=False)

    @zope.interface.invariant
    def state_country(obj):
        if not obj.state:
            return None
        if obj.state and not obj.country:
            raise StateWithoutCountryError(obj)
        if obj.country.alpha2 != obj.state.country_code:
            raise StateCountryMismatchError(obj)


class IEMailAddress(zope.interface.Interface):
    """An e-mail address."""

    kind = zope.schema.Choice(
        title=_(u'kind'), required=False,
        source=icemac.addressbook.sources.WorkPrivateKindSource())
    email = zope.schema.TextLine(
        title=_(u'e-mail address'), required=False,
        constraint=re.compile(
            "^[=+A-Za-z0-9_.-]+@([A-Za-z0-9_]+\.)+[A-Za-z]{2,6}$").match)
    notes = zope.schema.Text(title=_(u'notes'), required=False)

class IHomePageAddress(zope.interface.Interface):
    """A home page address."""

    kind = zope.schema.Choice(
        title=_(u'kind'), required=False,
        source=icemac.addressbook.sources.WorkPrivateKindSource())
    url = zope.schema.URI(title=_(u'URL'), required=False)
    notes = zope.schema.Text(title=_(u'notes'), required=False)

class IPhoneNumber(zope.interface.Interface):
    """A phone number."""

    kind = zope.schema.Choice(
        title=_(u'kind'), required=False,
        source=icemac.addressbook.sources.PhoneNumberKindSource())
    number = zope.schema.TextLine(title=_(u'number'), required=False)
    notes = zope.schema.Text(title=_(u'notes'), required=False)


class IPersonDefaults(zope.interface.Interface):
    """Default addresses, phone numbers etc."""

    default_postal_address = zope.schema.Object(
        IPostalAddress, title=_(u'main postal address'))
    default_email_address = zope.schema.Object(
        IEMailAddress, title=_(u'main e-mail address'))
    default_home_page_address = zope.schema.Object(
        IHomePageAddress, title=_(u'main home page address'))
    default_phone_number = zope.schema.Object(
        IPhoneNumber, title=_(u'main phone number'))


class IKeywords(zope.interface.Interface):
    """Collection of keywords."""

    def get_keywords():
        """Get the keywords in the collection."""

    def get_titles():
        """Get the titles of the keywords in the collection."""


class IKeyword(zope.interface.Interface):
    """A keyword."""

    title = zope.schema.TextLine(title=_(u'keyword'))
    notes = zope.schema.Text(title=_(u'notes'), required=False)
