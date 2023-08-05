import os
from zope.app.testing.functional import ZCMLLayer

AtomLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'AtomLayer', allow_teardown=True)

