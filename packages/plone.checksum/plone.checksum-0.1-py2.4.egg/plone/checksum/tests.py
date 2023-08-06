import sys
import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

import Products.Five.zcml as zcml
from Products.Five import fiveconfigure
import Products.PloneTestCase.layer
from Products.PloneTestCase import PloneTestCase

import plone.checksum

try:
    import Products.BlobFile
except ImportError:
    print >> sys.stderr, "Skipping plone.checksum tests for BlobFile."
    import Products
    Products.BlobFile = False
else:
    ztc.installProduct('BlobFile')

try:
    import Products.CMFEditions
except ImportError:
    Products.CMFEditions = False
    print >> sys.stderr, "Skipping plone.checksum tests for CMFEditions."
else:
    ztc.installProduct('CMFEditions')
    ztc.installProduct('CMFDiffTool')
    ztc.installProduct('CMFUid')

PloneTestCase.setupPloneSite()

class TestCase(PloneTestCase.PloneTestCase):
    class layer(Products.PloneTestCase.layer.PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml', plone.checksum)
            fiveconfigure.debug_mode = False


def test_suite():
    suites = [
        ztc.ZopeDocFileSuite(
            'README.txt', package='plone.checksum',
            test_class=TestCase),

        ztc.ZopeDocFileSuite(
            'README.txt', package='plone.checksum.browser',
            test_class=TestCase),

        doctestunit.DocTestSuite(
            module='plone.checksum.browser')
        ]

    if Products.BlobFile:
        suites.append(
            ztc.ZopeDocFileSuite(
               'BlobFile.txt', package='plone.checksum',
               test_class=TestCase),
            )

    if Products.CMFEditions:
        suites.append(
            ztc.ZopeDocFileSuite(
               'CMFEditions.txt', package='plone.checksum.browser',
               test_class=TestCase),
            )

    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
