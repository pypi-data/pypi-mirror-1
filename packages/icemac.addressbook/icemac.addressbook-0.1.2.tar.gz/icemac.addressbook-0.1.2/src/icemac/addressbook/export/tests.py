# -*- coding: latin-1 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 775 2008-11-01 14:41:29Z mac $

import unittest
import zope.interface.verify

import icemac.addressbook.export.interfaces
import icemac.addressbook.export.xls.simple
import icemac.addressbook.tests


class TestInterfaces(unittest.TestCase):

    def test_xls(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.export.interfaces.IExporter,
            icemac.addressbook.export.xls.simple.DefaultsExport())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInterfaces))
    suite.layer = icemac.addressbook.tests.AddressBookUnitTests
    return suite
