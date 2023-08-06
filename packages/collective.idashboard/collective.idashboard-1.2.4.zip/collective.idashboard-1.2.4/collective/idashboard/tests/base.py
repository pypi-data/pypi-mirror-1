from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from plone import browserlayer

from collective.idashboard.interfaces import IIDashboardLayer

ztc.installProduct('collective.idashboard')
ptc.setupPloneSite(products=['collective.idashboard'])

class iDashboardTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """

    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            browserlayer.utils.register_layer(IIDashboardLayer, name='collective.idashboard')

            fiveconfigure.debug_mode = True
            import collective.idashboard
            zcml.load_config('configure.zcml', collective.idashboard)
            fiveconfigure.debug_mode = False
            ztc.installPackage('collective.idashboard');





