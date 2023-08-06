from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

ztc.installProduct('Relations')
ztc.installProduct('slc.seminarportal')

PRODUCTS = ['Relations', 'slc.seminarportal']
ptc.setupPloneSite(products=PRODUCTS)
class SeminarPortalTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            import slc.seminarportal
            zcml.load_config('configure.zcml', slc.seminarportal)
            fiveconfigure.debug_mode = False
            ztc.installProduct('Relations')
            ztc.installPackage('slc.seminarportal');



