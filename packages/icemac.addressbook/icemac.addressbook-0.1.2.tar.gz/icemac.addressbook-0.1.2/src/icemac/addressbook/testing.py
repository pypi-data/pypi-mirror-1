import doctest
import os.path
import zope.app.testing.functional
import zope.testing.doctest

import icemac.addressbook.address
import icemac.addressbook.addressbook
import icemac.addressbook.keyword
import icemac.addressbook.person
import icemac.addressbook.utils


ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = zope.app.testing.functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer')


def FunctionalDocTestSuite(module=None, **kw):
    module = zope.testing.doctest._normalize_module(module)
    suite = zope.app.testing.functional.FunctionalDocTestSuite(module, **kw)
    suite.layer = FunctionalLayer
    return suite


def FunctionalDocFileSuite(*paths, **kw):
    kw['optionflags'] = (kw.get('optionflags', 0) | 
                         doctest.ELLIPSIS |
                         doctest.NORMALIZE_WHITESPACE)
    suite = zope.app.testing.functional.FunctionalDocFileSuite(*paths, **kw)
    suite.layer = FunctionalLayer
    return suite


class FunctionalTestCase(zope.app.testing.functional.FunctionalTestCase):
    layer = FunctionalLayer


def create_addressbook(parent=None, name='ab', title=u'test address book'):
    ab = icemac.addressbook.utils.create_obj(
        icemac.addressbook.addressbook.AddressBook, title=title)
    if parent is None:
        parent = zope.app.testing.functional.getRootFolder()
    parent[name] = ab
    return ab


def create_keyword(addressbook, title, notes=u''):
    parent = addressbook.keywords
    name = icemac.addressbook.utils.create_and_add(
        parent, icemac.addressbook.keyword.Keyword, title=title, notes=notes)
    return parent[name]


@icemac.addressbook.utils.set_site
def create_person(parent, last_name, **kw):
    kw['last_name'] = last_name
    name = icemac.addressbook.utils.create_and_add(
        parent, icemac.addressbook.person.Person, **kw)
    return parent[name]


@icemac.addressbook.utils.set_site
def create_postal_address(person, set_as_default=True, **kw):
    name = icemac.addressbook.utils.create_and_add(
        person, icemac.addressbook.address.PostalAddress, **kw)
    address = person[name]
    if set_as_default:
        person.default_postal_address = address
    return address


@icemac.addressbook.utils.set_site
def create_email_address(person, set_as_default=True, **kw):
    name = icemac.addressbook.utils.create_and_add(
        person, icemac.addressbook.address.EMailAddress, **kw)
    address = person[name]
    if set_as_default:
        person.default_email_address = address
    return address


@icemac.addressbook.utils.set_site
def create_home_page_address(person, set_as_default=True, **kw):
    name = icemac.addressbook.utils.create_and_add(
        person, icemac.addressbook.address.HomePageAddress, **kw)
    address = person[name]
    if set_as_default:
        person.default_home_page_address = address
    return address


@icemac.addressbook.utils.set_site
def create_phone_number(person, set_as_default=True, **kw):
    name = icemac.addressbook.utils.create_and_add(
        person, icemac.addressbook.address.PhoneNumber, **kw)
    number = person[name]
    if set_as_default:
        person.default_phone_number = number
    return number
