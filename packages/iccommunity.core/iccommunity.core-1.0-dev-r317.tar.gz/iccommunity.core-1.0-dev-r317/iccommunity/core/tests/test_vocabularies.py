# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_vocabularies.py 242 2008-06-11 14:31:30Z crocha $
#
# end: Platecom header
import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import PloneSite

from iccommunity.core.config import *
import base

class TestVocabularies(base.icCommunityTestCase):
    """
    """

class FunctionalTestVocabularies(base.icCommunityFunctionalTestCase):
    """
    """

def test_suite():
    return unittest.TestSuite([

        # Unit tests
        ztc.ZopeDocTestSuite(
                module=PACKAGENAME + '.vocabularies',
                test_class=TestVocabularies),

        # Integration tests that use PloneTestCase
        ztc.FunctionalDocFileSuite(
            'test_vocabularies.txt',
            package=PACKAGENAME + '.tests',
            test_class=FunctionalTestVocabularies),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
