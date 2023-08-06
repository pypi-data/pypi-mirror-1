# -*- coding: utf-8 -*-
#
# File: test_silverpop.py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__ = """Hans-Peter Locher <hans-peter.locher@inquant.de>"""
__docformat__ = 'plaintext'


import unittest

from zope import interface

from Products.CMFCore.utils import getToolByName

from Products.PloneFormGen.interfaces import IPloneFormGenActionAdapter

from collective.pfg.silverpop.interfaces.formsilverpopadapter import IFormSilverpopAdapter

from collective.pfg.silverpop.content.formsilverpopadapter import FormSilverpopAdapter

from collective.pfg.silverpop.tests.base import TestCase


class TestSetup(TestCase):
    """ The tests don't pass due to a bug in ATVM
    """

    def afterSetUp(self):
        self.setRoles(['Member', 'Manager'])
        self.types = getToolByName(self.portal, 'portal_types')
        self.properties = getToolByName(self.portal, 'portal_properties')
        self.qi = getToolByName(self.portal, 'portal_quickinstaller')
        self.portal.invokeFactory('FormFolder', 'testform')
        self.portal.testform.invokeFactory('FormSilverpopAdapter', 'testadapter')

        self.testform = self.portal.testform
        self.testadapter = self.portal.testform.testadapter

    def test_type_registered(self):
        self.failUnless('FormSilverpopAdapter' in self.types.listContentTypes())

    def test_class_fulfills_pfg_interface_contract(self):
        self.failUnless(interface.verify.verifyClass(IPloneFormGenActionAdapter, FormSilverpopAdapter))

    def test_object_fulfills_pfg_interface_contract(self):
        self.failUnless(interface.verify.verifyObject(IPloneFormGenActionAdapter, FormSilverpopAdapter('formsilverpopadapter')))

    def test_class_fulfills_silverpop_interface_contract(self):
        self.failUnless(interface.verify.verifyClass(IFormSilverpopAdapter, FormSilverpopAdapter))

    def test_object_fulfills_silverpop_interface_contract(self):
        self.failUnless(interface.verify.verifyObject(IFormSilverpopAdapter, FormSilverpopAdapter('formsilverpopadapter')))

    def test_type_excluded_from_nav(self):
        self.failUnless('FormSilverpopAdapter' in self.properties.navtree_properties.getProperty('metaTypesNotToList'))

    def test_type_excluded_from_search(self):
        self.failUnless('FormSilverpopAdapter' in self.properties.site_properties.getProperty('types_not_searched'))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
