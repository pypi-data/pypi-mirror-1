import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml

from quintagroup.pingtool.config import PROJECTNAME
from base import FunctionalTestCase

def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='%s' % PROJECTNAME,
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='%s.PingTool' % PROJECTNAME,
            setUp=testing.setUp, tearDown=testing.tearDown),

        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='%s' % PROJECTNAME,
        #    test_class=TestCase),

        ztc.FunctionalDocFileSuite(
            'browser.txt', package='%s.tests' % PROJECTNAME,
            test_class=FunctionalTestCase),

        ])
