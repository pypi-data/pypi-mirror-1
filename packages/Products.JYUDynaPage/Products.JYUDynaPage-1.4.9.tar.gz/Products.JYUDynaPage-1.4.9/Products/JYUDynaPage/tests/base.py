# -*- coding: utf-8 -*-

__author__="jutaojan"
__date__ ="$7.12.2008 20:13:11$"

from Products.Five                  import zcml
from Products.Five                  import fiveconfigure
from Testing                        import ZopeTestCase as ztc
from Products.PloneTestCase         import PloneTestCase as ptc
from Products.PloneTestCase.layer   import onsetup

# Old style products will be installed here
ztc.installPackage('JYUDynaPage')

@onsetup
def setup_jyudynapage():
    """Set up the additional products required for the JYUDynaPage.

    The @onsetup decorator causes the execution of this body to be
    deferred until the setup of the Plone site testing layer.
    """

    # Load the ZCML configuration for the Products.JYUPolicy package.

    fiveconfigure.debug_mode = True
    import Products.JYUDynaPage
    zcml.load_config('configure.zcml', Products.JYUPage)
    fiveconfigure.debug_mode = False

    ztc.installPackage('Products.JYUPolicy')

# The order here is important: We first call the (deferred) function
# which installs the products we need for the site. Then, we let
# PloneTestCase set up this product on installation.
setup_jyudynapage()
ptc.setupPloneSite(products=['Products.JYUDynaPage'])

class JYUDynaPageTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here.
    """
