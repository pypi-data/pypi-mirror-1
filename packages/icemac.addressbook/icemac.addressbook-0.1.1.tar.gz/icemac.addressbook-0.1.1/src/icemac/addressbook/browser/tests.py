# -*- coding: latin-1 -*-
# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 767 2008-10-31 13:00:04Z mac $

import unittest

import icemac.addressbook.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(icemac.addressbook.testing.FunctionalDocFileSuite(
            "browser/person/person.txt",
            "browser/addressbook/addressbook.txt",
            "browser/masterdata/masterdata.txt",
            "browser/keyword/keyword.txt",
            "browser/search/search.txt",
            "browser/export/export.txt",
            ))
    return suite
