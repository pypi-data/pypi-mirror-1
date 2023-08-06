import unittest
from zope import component
from zope.component import testing
from zope.testing import doctestunit

from p4a.z2utils import patches

def setUp(test):
    # apply monkey patches
    patches.apply_patches()

def tearDown(test):
    # unapply monkey patches
    patches.unapply_patches()

def test_suite():
    return unittest.TestSuite((
        doctestunit.DocTestSuite('p4a.audio.audioanno'),
        doctestunit.DocTestSuite('p4a.audio.genre'),
        doctestunit.DocTestSuite('p4a.audio.migration'),
        doctestunit.DocTestSuite('p4a.audio.utils'),

        doctestunit.DocTestSuite('p4a.audio.browser.audio'),
        doctestunit.DocTestSuite('p4a.audio.browser.displays',
                                 setUp=setUp, tearDown=tearDown),
        doctestunit.DocTestSuite('p4a.audio.browser.media'),
        doctestunit.DocTestSuite('p4a.audio.browser.support'),
        doctestunit.DocTestSuite('p4a.audio.browser.widget'),

        doctestunit.DocFileSuite('p4a-audio.txt',
                                 package="p4a.audio",
                                 setUp=setUp,
                                 tearDown=tearDown),

        doctestunit.DocFileSuite('media-player.txt',
                                 package="p4a.audio",
                                 setUp=testing.setUp,
                                 tearDown=testing.tearDown),

        doctestunit.DocFileSuite('migration.txt',
                                 package="p4a.audio",
                                 setUp=testing.setUp,
                                 tearDown=testing.tearDown)
        ))
