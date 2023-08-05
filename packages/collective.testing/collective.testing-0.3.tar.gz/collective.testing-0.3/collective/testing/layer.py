from utils import setDebugMode
from debug import dfunc

try:
    from Products.PloneTestCase.layer import ZCML as ZCMLLayer
except ImportError:
    class ZCMLLayer:
        @classmethod
        def setUp(cls):
            # this keeps five from hiding config errors while toggle debug
            # back on to let PTC perform efficiently
            setDebugMode(1)
            from Products.Five import zcml
            zcml.load_site()
            setDebugMode(0)

        @classmethod
        def tearDown(cls):
            from zope.testing.cleanup import cleanUp
            cleanUp()
            import Products.Five.zcml
            Products.Five.zcml._initialized=False
