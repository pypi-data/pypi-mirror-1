import unittest

from Testing import ZopeTestCase as ztc
# from Testing.ZopeTestCase import ZopeDocFileSuite
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import ptc
from Products.PloneTestCase.layer import onsetup

from zope.testing import doctest

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.NORMALIZE_WHITESPACE)

@onsetup
def setup_product():
    """Set up the package and its dependencies.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer. We could have created our
    own layer, but this is the easiest way for Plone integration tests.
    """
    
    # Load the ZCML configuration for the collective.lorem package.
    # This can of course use <include /> to include other packages.
    
    fiveconfigure.debug_mode = True
    import collective.lorem
    zcml.load_config('configure.zcml', collective.lorem)
    fiveconfigure.debug_mode = False
    
    # We may also need to load dependencies, e.g.:
    # 
    #   ztc.installPackage('borg.localrole')
    ztc.installPackage('collective.lorem')
    
setup_product()
ptc.setupPloneSite()

class BenchmarkingTestCase(ptc.FunctionalTestCase):
    pass 
        
def test_suite():
    return unittest.TestSuite((
        Suite(
            'generation.txt',
            optionflags=OPTIONFLAGS,
            test_class=BenchmarkingTestCase,
            ),
        ))
