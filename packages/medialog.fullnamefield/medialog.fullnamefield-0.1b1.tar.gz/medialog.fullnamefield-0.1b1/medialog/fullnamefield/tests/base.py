from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

ztc.installProduct('medialog.fullnamefield')
ptc.setupPloneSite(extension_profiles=('medialog.fullnamefield:test',))
ptc.setupPloneSite(products=['medialog.fullnamefield'])

class FullnameFieldTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """

    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            import medialog.fullnamefield
            zcml.load_config('configure.zcml', medialog.fullnamefield)
            fiveconfigure.debug_mode = False
            ztc.installPackage('medialog.fullnamefield');





