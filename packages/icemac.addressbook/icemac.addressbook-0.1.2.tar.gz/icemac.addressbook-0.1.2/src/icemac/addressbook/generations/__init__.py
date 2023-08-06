# Copyright (c) 2008 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 686 2008-10-02 16:25:28Z mac $
"""Database initialisation and upgrading."""

import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=1,
    generation=1,
    package_name='icemac.addressbook.generations')
