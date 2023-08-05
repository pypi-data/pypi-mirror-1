from p4a import plonevideo
from p4a.plonevideo import sitesetup
from Products.PloneTestCase import PloneTestCase
from zope.app.component import hooks

DEPENDENCIES = ['CMFonFive', 'Archetypes']
try:
    import Products.ATVideo
    DEPENDENCIES.append('ATVideo')
except ImportError, e:
    pass

PRODUCT_DEPENDENCIES = ['MimetypesRegistry', 'PortalTransforms']

if plonevideo.has_fatsyndication_support():
    PRODUCT_DEPENDENCIES += ['basesyndication', 'fatsyndication']
if plonevideo.has_blobfile_support():
    DEPENDENCIES += ['BlobFile']

# Install all (product-) dependencies, install them too
for dependency in PRODUCT_DEPENDENCIES + DEPENDENCIES:
    PloneTestCase.installProduct(dependency)

PRODUCTS = list(DEPENDENCIES)

PloneTestCase.setupPloneSite(products=PRODUCTS)

from Products.Five import zcml
import p4a.common
import p4a.video
import p4a.plonevideo
import plone.app.form

class IntegrationTestCase(PloneTestCase.PloneTestCase):
    """Plone based integration test for p4a.plonevideo."""

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        zcml.load_config('configure.zcml', plone.app.form)
        zcml.load_config('configure.zcml', p4a.common)
        zcml.load_config('configure.zcml', p4a.video)
        zcml.load_config('configure.zcml', p4a.plonevideo)
        zcml.load_config('configure.zcml', p4a.fileimage)
        hooks.setHooks()

        sitesetup.setup_portal(self.portal)

def testclass_builder(**kwargs):   
    class GeneratedIntegrationTestCase(IntegrationTestCase):
        """Generated integration TestCase for p4a.plonevideo."""

    for key, value in kwargs.items():
        setattr(GeneratedIntegrationTestCase, key, value)

    return GeneratedIntegrationTestCase
