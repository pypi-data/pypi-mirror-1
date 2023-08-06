# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: ftests.py 918 2009-01-02 19:35:06Z mac $

import icemac.addressbook.testing


def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        'adapter.txt',
        'address.txt',
        'catalog.txt',
        'export/export.txt',
        'person.txt',
        )
