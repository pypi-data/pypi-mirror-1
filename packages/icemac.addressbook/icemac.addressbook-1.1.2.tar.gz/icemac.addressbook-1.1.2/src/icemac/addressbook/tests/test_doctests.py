# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: test_doctests.py 783 2010-01-09 14:28:06Z icemac $

import icemac.addressbook.testing

def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        'adapter.txt', # Caution: none of these tests can run as unittest!
        'address.txt',
        'catalog.txt',
        'person.txt',
        )
