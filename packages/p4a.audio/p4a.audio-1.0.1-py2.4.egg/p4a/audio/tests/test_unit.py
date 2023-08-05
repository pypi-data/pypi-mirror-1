import unittest
from zope import component
from zope.component import testing
from zope.testing import doctestunit

def test_suite():
    return unittest.TestSuite((
        doctestunit.DocTestSuite('p4a.audio.audioanno'),
        doctestunit.DocTestSuite('p4a.audio.genre'),
        doctestunit.DocTestSuite('p4a.audio.migration'),
        doctestunit.DocTestSuite('p4a.audio.utils'),

        doctestunit.DocTestSuite('p4a.audio.browser.audio'),
        doctestunit.DocTestSuite('p4a.audio.browser.media'),
        doctestunit.DocTestSuite('p4a.audio.browser.support'),
        doctestunit.DocTestSuite('p4a.audio.browser.widget'),

        doctestunit.DocFileSuite('p4a-audio.txt',
                                 package="p4a.audio"),
        ))
