# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 913 2009-01-02 12:47:38Z mac $
"""Database initialisation and upgrading."""

import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=2,
    generation=2,
    package_name='icemac.addressbook.generations')
