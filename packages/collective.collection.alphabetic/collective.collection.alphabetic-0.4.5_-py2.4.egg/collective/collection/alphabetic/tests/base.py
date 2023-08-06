# -*- coding: utf-8 -*-
from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_collective_collection_alphabetic():

    fiveconfigure.debug_mode = True
    import collective.collection.alphabetic
    zcml.load_config('configure.zcml', collective.collection.alphabetic)
    fiveconfigure.debug_mode = False

    ztc.installPackage('collective.collection.alphabetic')

# The order here is important: We first call the (deferred) function which
# installs the products we need for the currency converter package. Then, we let 
# PloneTestCase set up this product on installation.

setup_collective_collection_alphabetic()
ptc.setupPloneSite(products=['collective.collection.alphabetic'])

class CollectionAlphabeticTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """

    def afterSetUp( self ):
        """Code that is needed is the afterSetUp of both test cases.
        """

        # Set up sessioning objects
        ztc.utils.setupCoreSessions(self.app)

class CollectionAlphabeticFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
