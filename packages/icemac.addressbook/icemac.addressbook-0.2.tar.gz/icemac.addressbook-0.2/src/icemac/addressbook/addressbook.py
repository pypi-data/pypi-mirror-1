# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: addressbook.py 913 2009-01-02 12:47:38Z mac $

import zc.catalog.catalogindex
import zope.app.appsetup.bootstrap
import zope.app.catalog.catalog
import zope.app.catalog.interfaces
import zope.app.component.interfaces
import zope.app.component.site
import zope.app.container.btree
import zope.app.container.interfaces
import zope.app.intid
import zope.app.intid.interfaces
import zope.component
import zope.interface
import zope.location
import zope.schema.fieldproperty

import icemac.addressbook.interfaces
import icemac.addressbook.keyword
import icemac.addressbook.utils


class AddressBook(zope.app.container.btree.BTreeContainer, 
                  zope.app.component.site.SiteManagerContainer):
    "An address book."

    zope.interface.implements(icemac.addressbook.interfaces.IAddressBook)

    keywords = None

    title = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IAddressBook['title'])
    notes = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IPerson['notes'])

@zope.component.adapter(
    icemac.addressbook.interfaces.IAddressBook,
    zope.app.container.interfaces.IObjectAddedEvent)
def create_address_book_infrastructure(addressbook, event):
    """Create initial infrastructure or update existing infrastructure to
    current requirements (using generation)."""
    # add site manager
    if not zope.app.component.interfaces.ISite.providedBy(addressbook):
        site_manager = zope.app.component.site.LocalSiteManager(addressbook)
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

@icemac.addressbook.utils.set_site
def add_more_addressbook_infrastructure(addressbook):
    "Add more infrastructure which depends on addressbook set as site."
    intids = zope.component.queryUtility(
        zope.app.intid.interfaces.IIntIds)
    if intids is None:
        # add intid utility
        intids = zope.app.appsetup.bootstrap.ensureUtility(
            addressbook, zope.app.intid.interfaces.IIntIds, '',
            zope.app.intid.IntIds, asObject=True)

        # register persons with intid utility
        for person in addressbook.values():
            intids.register(person)
            # register adresses of persons
            for value in person.values():
                intids.register(value)

    catalog = zope.component.queryUtility(
        zope.app.catalog.interfaces.ICatalog)
    if catalog is None:
        # add catalog
        catalog = zope.app.appsetup.bootstrap.ensureUtility(
            addressbook, zope.app.catalog.interfaces.ICatalog, '',
            zope.app.catalog.catalog.Catalog, asObject=True)

    # indexes
    if 'keywords' not in catalog:
        catalog['keywords'] = zc.catalog.catalogindex.SetIndex(
            'get_titles', icemac.addressbook.interfaces.IKeywords,
            field_callable=True)
