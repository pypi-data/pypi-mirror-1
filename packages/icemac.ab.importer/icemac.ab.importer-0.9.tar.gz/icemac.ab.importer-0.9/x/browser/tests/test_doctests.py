# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: test_doctests.py 550 2009-09-22 19:18:04Z icemac $

import icemac.addressbook.testing
import zope.app.testing.functional
import icemac.ab.importer.browser.testing


def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        "importer.txt",
        "masterdata.txt",
        package='icemac.ab.importer.browser',
        layer=icemac.ab.importer.browser.testing.ImporterLayer,
        )
