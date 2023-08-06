# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 1075 2009-03-21 09:29:00Z mac $
"""Database initialisation and upgrading."""

import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=4,
    generation=4,
    package_name='icemac.addressbook.generations')
