# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 1066 2009-03-20 17:13:24Z mac $

import icemac.addressbook.testing


def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        "browser/addressbook/addressbook.txt",
        "browser/authentication/login.txt",
        "browser/export/export.txt",
        "browser/keyword/keyword.txt",
        "browser/masterdata/masterdata.txt",
        "browser/person/person.txt",
        "browser/principals/principals.txt",
        "browser/rootfolder/rootfolder.txt",
        "browser/search/search.txt",
        )
