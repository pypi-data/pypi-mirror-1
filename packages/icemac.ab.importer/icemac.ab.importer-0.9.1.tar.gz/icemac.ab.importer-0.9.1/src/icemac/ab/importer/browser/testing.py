# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id: testing.py 550 2009-09-22 19:18:04Z icemac $

import os.path
import zope.app.testing.functional


zope.app.testing.functional.defineLayer(
    'ImporterLayer', 'ftesting.zcml', allow_teardown=True)
