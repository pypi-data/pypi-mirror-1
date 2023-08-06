import os
from zope.app.testing.functional import ZCMLLayer

KMLLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'KMLLayer', allow_teardown=True)

