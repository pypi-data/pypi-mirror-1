# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: ftests.py 1104 2009-03-31 19:53:53Z mac $

import icemac.addressbook.testing


def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        'adapter.txt',
        'address.txt',
        'catalog.txt',
        'export/export.txt',
        'person.txt',
        )
