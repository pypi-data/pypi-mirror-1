# -*- coding: latin-1 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 767 2008-10-31 13:00:04Z mac $

import gocept.reference.verify
import unittest
import zope.annotation.attribute
import zope.component
import zope.interface.verify
import zope.testing.cleanup
import zope.testing.doctest

import icemac.addressbook.address
import icemac.addressbook.addressbook
import icemac.addressbook.interfaces
import icemac.addressbook.keyword
import icemac.addressbook.person
import icemac.addressbook.testing

try:
    from zope.testing.testrunner.layer import UnitTests
except ImportError:
    # zope.testing < 3.6.0 has no unittest layer class
    class UnitTests(object):
        pass

class AddressBookUnitTests(UnitTests):
    """Layer for gathering addressbook unit tests."""

    @classmethod
    def setUp(cls):
        # some classes use gocept.reference and store default values for
        # which annotations are needed.        
        zope.component.provideAdapter(
            zope.annotation.attribute.AttributeAnnotations)

    @classmethod
    def tearDown(cls):
        zope.testing.cleanup.tearDown()

class TestInterfaces(unittest.TestCase):

    def test_person(self):
        person = icemac.addressbook.person.Person()
        gocept.reference.verify.verifyObject(
            icemac.addressbook.interfaces.IPerson, person)

        gocept.reference.verify.verifyObject(
            icemac.addressbook.interfaces.IPersonDefaults, person)

    def test_address_book(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IAddressBook,
            icemac.addressbook.addressbook.AddressBook())

    def test_postal_address(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IPostalAddress,
            icemac.addressbook.address.PostalAddress())

    def test_email_address(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IEMailAddress,
            icemac.addressbook.address.EMailAddress())

    def test_home_page_address(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IHomePageAddress,
            icemac.addressbook.address.HomePageAddress())

    def test_phone_number(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IPhoneNumber,
            icemac.addressbook.address.PhoneNumber())

    def test_keywords(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IKeywords,
            icemac.addressbook.keyword.KeywordContainer())
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IKeywords,
            icemac.addressbook.person.Keywords(None))

    def test_keyword(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.interfaces.IKeyword,
            icemac.addressbook.keyword.Keyword())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInterfaces))
    suite.addTest(zope.testing.doctest.DocTestSuite(icemac.addressbook.person))
    suite.addTest(zope.testing.doctest.DocTestSuite(icemac.addressbook.address))
    suite.addTest(icemac.addressbook.testing.FunctionalDocFileSuite(
            'catalog.txt', 'export/export.txt'))
    suite.layer = AddressBookUnitTests
    return suite
