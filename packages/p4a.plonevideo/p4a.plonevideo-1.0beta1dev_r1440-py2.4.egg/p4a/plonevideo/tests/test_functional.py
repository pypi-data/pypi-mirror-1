import os
import unittest
import doctest
from zope.testing import doctestunit
from p4a import plonevideo
from p4a.plonevideo.tests import testing
from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite
from Testing.ZopeTestCase import FunctionalDocFileSuite
from App import Common
from Products.PloneTestCase import layer

def test_suite():
    suite = unittest.TestSuite()
    if __name__ not in ('__main__', 'p4a.plonevideo.tests.test_functional'):
        return suite
    
    #    suite = unittest.TestSuite((
    #       doctestunit.DocTestSuite('p4a.plonevideo.atct'),
    #      ))

    if plonevideo.has_fatsyndication_support():
        suite.addTest(ZopeDocFileSuite(
            'syndication.txt',
            package='p4a.plonevideo',
            test_class=testing.IntegrationTestCase,
            optionflags=doctest.ELLIPSIS,
            )
        )

    suite.addTest(ZopeDocFileSuite(
        'plone-video.txt',
        package='p4a.plonevideo',
        test_class=testing.testclass_builder(file_type='File')
        )
    )

    import p4a.video.tests
    pkg_home = Common.package_home({'__name__': 'p4a.video.tests'})
    samplesdir = os.path.join(pkg_home, 'samples')

    # More quicktime samples here:
    # http://docs.info.apple.com/article.html?artnum=75424

    SAMPLES = (
        # current mov parser doesn't understand width/height
        ('sample_sorenson.mov', 'video/quicktime', dict(width=0,#190,
                                                        height=0,#240,
                                                        duration=0)),#5.0
        
        # current mp4 parser doesn't understand width/height
        ('sample_mpeg4.mp4', 'video/mp4', dict(width=0,#190
                                               height=0,#240
                                               duration=0)),#4.966
        
        ('barsandtone.flv', 'video/x-flv', dict(width=360,
                                                height=288,
                                                duration=6.0)),
        
        ('sample_wmv.wmv', 'video/x-ms-wmv', dict(width=0,
                                                  height=0,
                                                  duration=5.7729999999999997)),
    )

    for samplefile, mimetype, fields in SAMPLES:
        suite.addTest(ZopeDocFileSuite(
            'plone-video-impl.txt',
            package='p4a.plonevideo',
            test_class=testing.testclass_builder(
                samplefile=os.path.join(samplesdir, samplefile),
                required_mimetype=mimetype,
                file_content_type='File',
                fields=fields)
            )
        )

    if plonevideo.has_blobfile_support():
        # setup the same test to run against BlobFile if available
        samplefile, mimetype, fields = SAMPLES[0]
        suite.addTest(ZopeDocFileSuite(
            'plone-video-impl.txt',
            package='p4a.plonevideo',
            test_class=testing.testclass_builder(samplefile=samplefile,
                                                 required_mimetype=mimetype,
                                                 file_content_type='BlobFile',
                                                 fields=fields)
            )
        )

    suite.layer = layer.ZCMLLayer

    return suite
