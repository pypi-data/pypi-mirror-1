import doctest
import unittest
from zope.component import testing
from zope.testing import doctestunit

from p4a.plonevideo import has_fatsyndication_support

def test_suite():
    suite = unittest.TestSuite((
        doctestunit.DocTestSuite('p4a.plonevideo.atct'),
        doctestunit.DocTestSuite('p4a.plonevideo.content'),
        doctestunit.DocTestSuite('p4a.plonevideo.sitesetup',
                                 optionflags=doctest.ELLIPSIS),

        doctestunit.DocFileSuite('p4a-plonevideo.txt',
                                 package="p4a.plonevideo",
                                 setUp=testing.setUp,
                                 tearDown=testing.tearDown,
                                 optionflags=doctest.ELLIPSIS),
        ))

    if has_fatsyndication_support():
        suite.addTest(doctestunit.DocTestSuite('p4a.plonevideo.syndication'))

    return suite
