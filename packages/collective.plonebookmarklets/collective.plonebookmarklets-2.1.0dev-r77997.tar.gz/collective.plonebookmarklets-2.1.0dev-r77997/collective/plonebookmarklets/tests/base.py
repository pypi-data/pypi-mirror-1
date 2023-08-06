
from zope.testing import doctest
from Products.PloneTestCase.PloneTestCase import setupPloneSite, installProduct
from Products.PloneTestCase.PloneTestCase import PloneTestCase, FunctionalTestCase
from setuptools import find_packages

from Products.Five import fiveconfigure
from Products.Five import zcml
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase.layer import onsetup


packages=find_packages('src')
package_dir={'':'src'},

@onsetup
def setup_plonebookmarklets_project():
    """
    Load and install packages required for the collective.plonebookmarklets tests
    """

    fiveconfigure.debug_mode = True
    
    import collective.plonebookmarklets
    zcml.load_config('configure.zcml',collective.plonebookmarklets)
    zcml.load_config('browser/configure.zcml',collective.plonebookmarklets)
    
    fiveconfigure.debug_mode = False

    ztc.installPackage('collective.plonebookmarklets')


setup_plonebookmarklets_project()
setupPloneSite(with_default_memberarea=0,extension_profiles=['collective.plonebookmarklets:default'])

oflags = (doctest.ELLIPSIS |
          doctest.NORMALIZE_WHITESPACE)

prod = "collective.plonebookmarklets"

class PloneBookmarkletsTestCase(PloneTestCase):
    """ Test Class """

class PloneBookmarkletsFunctionalTestCase(FunctionalTestCase, PloneBookmarkletsTestCase):
    """ Functional test class """
