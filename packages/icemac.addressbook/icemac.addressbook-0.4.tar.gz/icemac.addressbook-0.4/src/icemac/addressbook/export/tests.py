# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 1124 2009-04-07 18:42:58Z mac $

import unittest
import zope.interface.verify

import icemac.addressbook.export.interfaces
import icemac.addressbook.export.xls.simple
import icemac.addressbook.testing


class TestInterfaces(unittest.TestCase):

    def test_xls(self):
        zope.interface.verify.verifyObject(
            icemac.addressbook.export.interfaces.IExporter,
            icemac.addressbook.export.xls.simple.XLSExport())
        zope.interface.verify.verifyObject(
            icemac.addressbook.export.interfaces.IExporter,
            icemac.addressbook.export.xls.simple.DefaultsExport())
        zope.interface.verify.verifyObject(
            icemac.addressbook.export.interfaces.IExporter,
            icemac.addressbook.export.xls.simple.CompleteExport())


def test_suite():
    return icemac.addressbook.testing.UnittestSuite(TestInterfaces)
