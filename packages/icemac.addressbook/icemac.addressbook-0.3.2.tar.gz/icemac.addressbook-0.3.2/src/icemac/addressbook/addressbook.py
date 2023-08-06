# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: addressbook.py 1089 2009-03-31 16:03:01Z mac $

import zc.catalog.catalogindex
import zope.app.appsetup.bootstrap
import zope.app.authentication.authentication
import zope.app.authentication.interfaces
import zope.app.authentication.principalfolder
import zope.catalog.catalog
import zope.catalog.interfaces
import zope.authentication.interfaces
import zope.component
import zope.container.btree
import zope.container.interfaces
import zope.interface
import zope.intid
import zope.intid.interfaces
import zope.location
import zope.location.interfaces
import zope.schema.fieldproperty
import zope.site.site
import icemac.addressbook.interfaces
import icemac.addressbook.keyword
import icemac.addressbook.utils


class AddressBook(zope.container.btree.BTreeContainer,
                  zope.site.site.SiteManagerContainer):
    "An address book."

    zope.interface.implements(icemac.addressbook.interfaces.IAddressBook)

    keywords = None
    principals = None

    title = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IAddressBook['title'])
    notes = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPerson['notes'])

@zope.component.adapter(
    icemac.addressbook.interfaces.IAddressBook,
    zope.container.interfaces.IObjectAddedEvent)
def create_address_book_infrastructure(addressbook, event):
    """Create initial infrastructure or update existing infrastructure to
    current requirements (using generation)."""
    # add site manager
    if not zope.location.interfaces.ISite.providedBy(addressbook):
        site_manager = zope.site.site.LocalSiteManager(addressbook)
        addressbook.setSiteManager(site_manager)

    site_manager = addressbook.getSiteManager()

    # add keywords container
    if addressbook.keywords is None:
        keywords = icemac.addressbook.utils.create_obj(
            icemac.addressbook.keyword.KeywordContainer)
        addressbook.keywords = keywords
        zope.location.locate(keywords, addressbook, '++attribute++keywords')
        site_manager.registerUtility(
            keywords, icemac.addressbook.interfaces.IKeywords)

    add_more_addressbook_infrastructure(addressbook, addressbook)


def utility_locally_registered(site, interface):
    """Test, whether a utility is registered on the site manager of the site.

    interface ... interface the utility is registered for

    """

    for registration in site.getSiteManager().registeredUtilities():
        if registration.provided == interface:
            return True
    return False


@icemac.addressbook.utils.set_site
def add_more_addressbook_infrastructure(addressbook):
    "Add more infrastructure which depends on addressbook set as site."
    # intid utility
    if not utility_locally_registered(addressbook,
                                      zope.intid.interfaces.IIntIds):
        intids = zope.app.appsetup.bootstrap.ensureUtility(
            addressbook, zope.intid.interfaces.IIntIds, '', zope.intid.IntIds)

        # register existing persons with intid utility
        for person in addressbook.values():
            intids.register(person)
            # register adresses of persons
            for value in person.values():
                intids.register(value)

    # catalog
    if utility_locally_registered(addressbook,
                                  zope.catalog.interfaces.ICatalog):
        catalog = zope.component.queryUtility(zope.catalog.interfaces.ICatalog)
    else:
        # add catalog
        catalog = zope.app.appsetup.bootstrap.ensureUtility(
            addressbook, zope.catalog.interfaces.ICatalog, '',
            zope.catalog.catalog.Catalog)

    # indexes
    if 'keywords' not in catalog:
        catalog['keywords'] = zc.catalog.catalogindex.SetIndex(
            'get_titles', icemac.addressbook.interfaces.IKeywords,
            field_callable=True)

    # authenticator (PAU)
    if not utility_locally_registered(
        addressbook, zope.authentication.interfaces.IAuthentication):
        pau = zope.app.appsetup.bootstrap.ensureUtility(
            addressbook, zope.authentication.interfaces.IAuthentication, '',
            zope.app.authentication.authentication.PluggableAuthentication)
        pau.credentialsPlugins = (u'No Challenge if Authenticated',
                                  u'Session Credentials',)

    # principals folder
    if addressbook.principals is None:
        principals = icemac.addressbook.utils.create_obj(
            zope.app.authentication.principalfolder.PrincipalFolder)
        addressbook.principals = principals
        zope.location.locate(principals, addressbook, '++attribute++principals')
        site_manager = addressbook.getSiteManager()
        site_manager.registerUtility(
            principals, zope.app.authentication.interfaces.IAuthenticatorPlugin,
            name=u'icemac.addressbook.principals')
    pau.authenticatorPlugins = (u'icemac.addressbook.principals',)
