from zope.testing import doctestunit
import unittest

def test_suite():
    return unittest.TestSuite((
        doctestunit.DocTestSuite('p4a.audio.ogg._audiodata'),
        doctestunit.DocTestSuite('p4a.audio.ogg._player'),
        ))
