import os

import unittest
from zope.testing import doctest
from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase
import Products.Five
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import PloneSite

from users import setupUsers

import ely.contentgenerator

fiveconfigure.debug_mode = True
zcml.load_config('configure.zcml', Products.Five)
zcml.load_config('configure.zcml', ely.contentgenerator)
fiveconfigure.debug_mode = False

PloneTestCase.setupPloneSite()


optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

class TestCase(PloneTestCase.FunctionalTestCase):

    def _setup(self):
        super(TestCase, self)._setup()
        portal = self.portal
        setupUsers(self)

    def _file(self, filename=None):
        here = os.path.dirname(os.path.realpath(__file__))
        if filename:
            return os.path.join(here, filename)
        else:
            return here

def test_suite():
    return unittest.TestSuite([
        ZopeTestCase.ZopeDocFileSuite(
            'testcontent1.txt',
            package='ely.contentgenerator.tests',
            test_class=TestCase,
            optionflags=optionflags,
            ),
        ])
