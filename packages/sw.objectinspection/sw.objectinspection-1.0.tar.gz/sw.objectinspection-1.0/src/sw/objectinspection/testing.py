# Copyright (c) 2009 Sebastian Wehrmann
# See also LICENSE.txt

import os.path
import sw.objectinspection
import zope.app.testing.functional

ftesting_zcml = os.path.join(
    os.path.dirname(sw.objectinspection.__file__), 'ftesting.zcml')
FunctionalLayer = zope.app.testing.functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer')

