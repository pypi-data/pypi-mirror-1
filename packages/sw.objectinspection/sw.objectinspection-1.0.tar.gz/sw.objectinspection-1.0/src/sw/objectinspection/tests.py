# Copyright (c) 2009 Sebastian Wehrmann
# See also LICENSE.txt

import re
import zope.testing.renormalizing
import zope.app.testing.functional
import os.path
import sw.objectinspection.testing

patterns = [(re.compile('0x[0-9a-f]+'), "<MEM ADDRESS>")]

checker = zope.testing.renormalizing.RENormalizing(patterns)

def test_suite():
    suite = zope.app.testing.functional.FunctionalDocFileSuite(
        "README.txt",
        checker=checker,
    )
    suite.layer = sw.objectinspection.testing.FunctionalLayer
    return suite
