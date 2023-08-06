import os
import doctest
import unittest
from App import Common

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from p4a import plonevideo
from p4a.video import interfaces as video_ifaces

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup, PloneSite

@onsetup
def load_package_products():
    import p4a.z2utils
    import p4a.common
    import p4a.fileimage
    import p4a.subtyper
    import p4a.video
    import p4a.plonevideo

    fiveconfigure.debug_mode = True
    zcml.load_config('meta.zcml', p4a.subtyper)
    zcml.load_config('configure.zcml', p4a.subtyper)
    zcml.load_config('configure.zcml', p4a.common)
    zcml.load_config('configure.zcml', p4a.fileimage)
    zcml.load_config('configure.zcml', p4a.video)
    zcml.load_config('configure.zcml', p4a.plonevideo)
    fiveconfigure.debug_mode = False
    ztc.installPackage('p4a.plonevideo')

load_package_products()
ptc.setupPloneSite(products=['p4a.plonevideo'])

def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(ztc.FunctionalDocFileSuite(
        'plone-video.txt',
        package='p4a.plonevideo',
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE,
        test_class=ptc.FunctionalTestCase))

    suite.addTest(ztc.FunctionalDocFileSuite('syndication.txt',
                                             package='p4a.plonevideo',
                                             optionflags=doctest.ELLIPSIS,
                                             test_class=ptc.FunctionalTestCase))

    import p4a.video.tests
    pkg_home = Common.package_home({'__name__': 'p4a.video.tests'})
    samplesdir = os.path.join(pkg_home, 'samples')

    # More quicktime samples here:
    # http://docs.info.apple.com/article.html?artnum=75424

    SAMPLES = (
    ('sample_sorenson.mov', 'video/quicktime', dict(
        width=190,
        height=240,
        duration=5.0)),
    
    ('sample_mpeg4.mp4', 'video/mp4', dict(
        width=190,
        height=240,
        duration=4.9666670000000002)),
    
    ('barsandtone.flv', 'video/x-flv', dict(
        width=360,
        height=288,
        duration=6.0)),
    
    ('sample_wmv.wmv', 'video/x-ms-wmv', dict(
        width=video_ifaces.IVideo['width'].default,
        height=video_ifaces.IVideo['height'].default,
        duration=5.7729999999999997)),
    )

    for relsamplefile, mimetype, samplefields in SAMPLES:
        class MediaTestCase(ptc.FunctionalTestCase):
            required_mimetype = mimetype
            samplefile = os.path.join(samplesdir, relsamplefile)
            file_content_type = 'File'
            fields = samplefields

        test = ztc.FunctionalDocFileSuite('plone-video-impl.txt',
                                          package='p4a.plonevideo',
                                          optionflags=doctest.ELLIPSIS,
                                          test_class=MediaTestCase)

        suite.addTest(test)

    return suite
