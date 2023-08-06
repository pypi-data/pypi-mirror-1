import unittest
from zope.testing import doctestunit

def test_suite():
    return unittest.TestSuite((
        doctestunit.DocTestSuite('Products.PloneFlashUpload.ticket'),
        doctestunit.DocTestSuite('Products.PloneFlashUpload.browser'),
        doctestunit.DocTestSuite('Products.PloneFlashUpload.atct'),
        ))
