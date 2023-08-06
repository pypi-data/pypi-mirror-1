# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: tests.py 571 2009-09-26 19:44:29Z icemac $

import icemac.addressbook.testing
import icemac.ab.importer.browser.testing

def test_suite():
    return icemac.addressbook.testing.FunctionalDocFileSuite(
        "constraints.txt",
        "edgecases.txt",
        "keywords.txt",
        "multientries.txt",
        "wizard.txt",
        package='icemac.ab.importer.browser.wizard',
        layer=icemac.ab.importer.browser.testing.ImporterLayer,
        )
