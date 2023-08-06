from p4a.video import interfaces
from p4a.plonevideo import content
from p4a.common import site
from p4a.z2utils import indexing
from p4a.z2utils import utils
from p4a.subtyper import sitesetup as subtypersetup
from p4a.subtyper import interfaces as subtyper_ifaces

from Products.CMFCore import utils as cmfutils 
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem

import logging
logger = logging.getLogger('p4a.plonevideo.sitesetup')

try:
    import five.localsitemanager
    HAS_FLSM = True
    logger.info('Using five.localsitemanager')
except ImportError, err:
    HAS_FLSM = False

def setup_portal(portal):
    site.ensure_site(portal)
    setup_site(portal)
    indexing.ensure_object_provides(portal)

def setup_site(site):
    """Install all necessary components and configuration into the
    given site.

      >>> from p4a.video import interfaces
      >>> from p4a.common.testing import MockSite

      >>> site = MockSite()
      >>> site.queryUtility(interfaces.IVideoSupport) is None
      True

    """

    sm = site.getSiteManager()
    if not sm.queryUtility(interfaces.IVideoSupport):
        # registerUtility api changed between Zope 2.9 and 2.10
        if HAS_FLSM:
            sm.registerUtility(content.VideoSupport('video_support'),
                               interfaces.IVideoSupport)
        else:
            sm.registerUtility(interfaces.IVideoSupport,
                               content.VideoSupport('video_support'))

    mr = cmfutils.getToolByName(site, 'mimetypes_registry')
    mimetype = MimeTypeItem(name='Flash Video', mimetypes=('video/x-flv',),
                            extensions=('flv',), binary=1)
    mr.register(mimetype)
    mimetype = MimeTypeItem(name='iPod Video', mimetypes=('video/x-m4v',),
                            extensions=('m4v',), binary=1)
    mr.register(mimetype)
    
    subtypersetup.setup_site(site)

def _cleanup_utilities(site):
    raise NotImplementedError('Current ISiteManager support does not '
                              'include ability to clean up')

def unsetup_portal(portal):
    count = utils.remove_marker_ifaces(
        portal,
        [interfaces.IVideoEnhanced,
         interfaces.IVideoContainerEnhanced,
         subtyper_ifaces.ISubtyped])
    logger.warn('Removed IVideoEnhanced, IVideoContainerEnhanced, '
                'ISubtyped interfaces from %i objects for cleanup'
                % count)
