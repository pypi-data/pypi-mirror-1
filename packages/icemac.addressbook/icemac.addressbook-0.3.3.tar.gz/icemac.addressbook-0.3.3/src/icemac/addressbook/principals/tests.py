# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 1080 2009-03-26 17:41:06Z mac $

import gocept.reference.verify
import unittest
import zope.interface.verify

import icemac.addressbook.testing
import icemac.addressbook.principals.interfaces
import icemac.addressbook.principals.principals


class TestInterfaces(unittest.TestCase):

    def test_principal(self):
        principal = icemac.addressbook.principals.principals.Principal()
        # need to call created event handler here, because person
        # attribute is a descriptor wrapping the one verifyObject
        # expects.
        icemac.addressbook.principals.principals.created(principal, None)
        gocept.reference.verify.verifyObject(
            icemac.addressbook.principals.interfaces.IPrincipal, principal)
        zope.interface.verify.verifyObject(
            icemac.addressbook.principals.interfaces.IPasswordFields, principal)
        zope.interface.verify.verifyObject(
            icemac.addressbook.principals.interfaces.IRoles, principal)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInterfaces))
    suite.layer = icemac.addressbook.testing.AddressBookUnitTests
    return suite
