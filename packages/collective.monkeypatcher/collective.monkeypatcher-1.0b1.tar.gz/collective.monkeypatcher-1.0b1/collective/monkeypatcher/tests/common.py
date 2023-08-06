# -*- coding: utf-8
# $Id: common.py 84133 2009-04-12 21:17:24Z glenfant $
"""Common resources for unit testing"""

import unittest

import zope.component
from zope.app.testing.placelesssetup import PlacelessSetup
from zope.configuration.xmlconfig import XMLConfig

import collective.monkeypatcher


class MonkeypatcherTestCase(PlacelessSetup, unittest.TestCase):
    """Base for test cases"""

    def setUp(self):
        XMLConfig('meta.zcml', zope.component)()
        XMLConfig('meta.zcml', collective.monkeypatcher)()
        XMLConfig('configure.zcml', collective.monkeypatcher)()
        XMLConfig('dummypatch.zcml', collective.monkeypatcher.tests)()
        return
