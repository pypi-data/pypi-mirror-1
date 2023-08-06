# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: evolve3.py 679 2009-11-21 14:33:08Z icemac $

__docformat__ = "reStructuredText"


import icemac.addressbook.generations.utils


generation = 3


def evolve(context):
    """Installs the authentication utility.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
