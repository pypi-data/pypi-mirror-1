# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: test_doctests.py 510 2009-07-18 18:53:29Z mac $

import icemac.addressbook.testing

def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        'adapter.txt', # Caution: none of these tests can run as unittest!
        'address.txt',
        'catalog.txt',
        'person.txt',
        )
