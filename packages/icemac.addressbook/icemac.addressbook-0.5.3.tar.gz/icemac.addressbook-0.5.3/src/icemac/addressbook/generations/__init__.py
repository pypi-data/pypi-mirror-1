# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 679 2009-11-21 14:33:08Z icemac $
"""Database initialisation and upgrading."""

import zope.app.generations.generations


GENERATION = 7


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.addressbook.generations')
