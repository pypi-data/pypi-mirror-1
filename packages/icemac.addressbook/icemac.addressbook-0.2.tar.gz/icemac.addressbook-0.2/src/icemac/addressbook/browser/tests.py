# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 913 2009-01-02 12:47:38Z mac $

import icemac.addressbook.testing


def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        "browser/person/person.txt",
        "browser/addressbook/addressbook.txt",
        "browser/masterdata/masterdata.txt",
        "browser/keyword/keyword.txt",
        "browser/search/search.txt",
        "browser/export/export.txt",
        )
