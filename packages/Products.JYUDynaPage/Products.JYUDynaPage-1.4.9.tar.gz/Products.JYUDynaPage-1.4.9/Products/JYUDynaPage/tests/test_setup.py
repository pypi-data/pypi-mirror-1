# -*- coding: utf-8 -*-

__author__="jutaojan"
__date__ ="$7.12.2008 20:17:54$"

import unittest
from Products.JYUDynaPage.tests.base import JYUDynaPageTestCase

class TestSetup(JYUDynaPageTestCase):
    """ Contains test functions """


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite

