from zope.app.component import hooks

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from collective.testcaselayer import ptc as tcl_ptc

from p4a import ploneimage
from p4a.ploneimage import sitesetup

class InstallLayer(tcl_ptc.BasePTCLayer):
    """Install p4a.ploneimage"""

    def afterSetUp(self):
        ZopeTestCase.installPackage('p4a.ploneimage')
        self.addProfile('p4a.ploneimage:default')

        # Disable the storage quota
        self.app._p_jar._storage._quota = None

install_layer = InstallLayer([tcl_ptc.ptc_layer])

DEPENDENCIES = ['CMFonFive', 'Archetypes']
try:
    import Products.ATPhoto
    DEPENDENCIES.append('ATPhoto')
except ImportError, e:
    pass

PRODUCT_DEPENDENCIES = ['MimetypesRegistry', 'PortalTransforms']

if ploneimage.has_fatsyndication_support():
    PRODUCT_DEPENDENCIES += ['basesyndication', 'fatsyndication']
if ploneimage.has_blobfile_support():
    DEPENDENCIES += ['BlobFile']

# Install all (product-) dependencies, install them too
for dependency in PRODUCT_DEPENDENCIES + DEPENDENCIES:
    PloneTestCase.installProduct(dependency)

PRODUCTS = list(DEPENDENCIES)

PloneTestCase.setupPloneSite(products=PRODUCTS)

from Products.Five import zcml
import p4a.common
import p4a.image
import p4a.ploneimage

class IntegrationTestCase(PloneTestCase.PloneTestCase):
    """Plone based integration test for p4a.ploneimage."""

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        zcml.load_config('configure.zcml', p4a.common)
        zcml.load_config('configure.zcml', p4a.image)
        zcml.load_config('configure.zcml', p4a.ploneimage)
        zcml.load_config('configure.zcml', p4a.fileimage)
        hooks.setHooks()

        sitesetup.setup_portal(self.portal)

def testclass_builder(**kwargs):   
    class GeneratedIntegrationTestCase(IntegrationTestCase):
        """Generated integration TestCase for p4a.ploneimage."""

    for key, value in kwargs.items():
        setattr(GeneratedIntegrationTestCase, key, value)

    return GeneratedIntegrationTestCase
