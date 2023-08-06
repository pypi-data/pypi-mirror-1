# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 677 2009-11-21 13:54:42Z icemac $
"""Database initialisation and upgrading."""

import zope.app.generations.generations


GENERATION = 0


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.ab.importer.generations')
