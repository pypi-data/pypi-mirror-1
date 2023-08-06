from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

ztc.installProduct('medialog.emailfield')
ptc.setupPloneSite(extension_profiles=('medialog.emailfield:test',))
ptc.setupPloneSite(products=['medialog.emailfield'])

class EmailFieldTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """

    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            import medialog.emailfield
            zcml.load_config('configure.zcml', medialog.emailfield)
            fiveconfigure.debug_mode = False
            ztc.installPackage('medialog.emailfield');





