"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup


@onsetup
def setup_product():
    """Set up the package and its dependencies.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer. We could have created our
    own layer, but this is the easiest way for Plone integration tests.
    """
    
    # Load the ZCML configuration for the example.tests package.
    # This can of course use <include /> to include other packages.
    
    fiveconfigure.debug_mode = True
    import example.archetype
    zcml.load_config('configure.zcml', example.archetype)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML. Thus, we do it here. Note the use of installPackage() instead
    # of installProduct().
    # 
    # This is *only* necessary for packages outside the Products.* namespace
    # which are also declared as Zope 2 products, using 
    # <five:registerPackage /> in ZCML.
        
    ztc.installPackage('example.archetype')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need for this product. Then, we let PloneTestCase 
# set up this product on installation.

setup_product()
ptc.setupPloneSite(products=['example.archetype'])


class InstantMessageTestCase(ptc.PloneTestCase):
    """Base class for integration tests.

    This may provide specific set-up and tear-down operations, or provide
    convenience methods.
    """


class InstantMessageFunctionalTestCase(ptc.FunctionalTestCase):
    """Base class for functional integration tests.

    This may provide specific set-up and tear-down operations, or provide
    convenience methods.
    """