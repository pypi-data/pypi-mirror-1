# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 805 2010-01-23 20:31:46Z icemac $
"""Database initialisation and upgrading."""

import zope.app.generations.generations


GENERATION = 8


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.addressbook.generations')
