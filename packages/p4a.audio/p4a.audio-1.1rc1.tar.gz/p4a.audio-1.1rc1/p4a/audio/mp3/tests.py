import doctest
import unittest
from zope import component
from zope.component import testing
from zope.testing import doctestunit

def test_suite():
    return unittest.TestSuite((
        doctestunit.DocFileSuite('mp3.txt',
                                 package="p4a.audio.mp3",
                                 optionflags=doctest.ELLIPSIS,
                                 setUp=testing.setUp,
                                 tearDown=testing.tearDown),
        ))
