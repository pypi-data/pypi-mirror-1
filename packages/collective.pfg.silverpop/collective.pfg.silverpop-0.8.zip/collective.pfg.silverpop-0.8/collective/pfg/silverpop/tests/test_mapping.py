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

from collective.pfg.silverpop.tests.base import TestCase


class TestMapping(TestCase):
    """ test mapping functionality
    """

    def afterSetUp(self):
        self.setRoles(['Member', 'Manager'])
        self.types = getToolByName(self.portal, 'portal_types')
        self.properties = getToolByName(self.portal, 'portal_properties')
        self.qi = getToolByName(self.portal, 'portal_quickinstaller')
        self.portal.invokeFactory('FormFolder', 'testform')
        self.portal.testform.invokeFactory('FormStringField', 'some_field')
        self.portal.testform.invokeFactory('FormStringField', 'silverpop_field1')
        self.portal.testform.invokeFactory('FormStringField', 'silverpop_field2')
        self.portal.testform.invokeFactory('FormStringField', 'silverpop_field3')
        self.portal.testform.invokeFactory('FormSilverpopAdapter', 'silverpop_adapter')

        self.testform = self.portal.testform
        self.testadapter = self.portal.testform.silverpop_adapter
        self.some_field = self.portal.testform.some_field
        self.silverpop_field1 = self.portal.testform.silverpop_field1
        self.silverpop_field2 = self.portal.testform.silverpop_field2
        self.silverpop_field3 = self.portal.testform.silverpop_field3

    def test_initial_get_mapping(self):
        result = self.testadapter.get_mapping()
        self.failUnless(result ==
            [{'silverpop api key': '', 'id': 'silverpop_field3', 'title': ''},
             {'silverpop api key': '', 'id': 'silverpop_field2', 'title': ''},
             {'silverpop api key': '', 'id': 'silverpop_field1', 'title': ''}]
            )

    def test_set_mapping(self):
        mapping = [{'silverpop api key': 'key1', 'id': 'silverpop_field3', 'title': ''},
                   {'silverpop api key': 'key2', 'id': 'silverpop_field2', 'title': ''},
                   {'silverpop api key': '', 'id': 'silverpop_field1', 'title': ''}]
        self.testadapter.set_mapping(mapping)
        result = self.testadapter.get_mapping()
        self.failUnless(result ==
            [{'silverpop api key': 'key1', 'id': 'silverpop_field3', 'title': ''},
             {'silverpop api key': 'key2', 'id': 'silverpop_field2', 'title': ''},
             {'silverpop api key': '', 'id': 'silverpop_field1', 'title': ''}]
            )

    def test_get_mapping_additional_field(self):
        self.testform.invokeFactory('FormStringField', 'silverpop_field4', title='new field')
        result = self.testadapter.get_mapping()
        self.failUnless(result ==
            [{'silverpop api key': '', 'id': 'silverpop_field4', 'title': 'new field'},
             {'silverpop api key': '', 'id': 'silverpop_field3', 'title': ''},
             {'silverpop api key': '', 'id': 'silverpop_field2', 'title': ''},
             {'silverpop api key': '', 'id': 'silverpop_field1', 'title': ''}]
            )

    def test_set_mapping_removed_field(self):
        mapping = [{'silverpop api key': 'key1', 'id': 'silverpop_field3', 'title': ''},
                   {'silverpop api key': 'key2', 'id': 'silverpop_field2', 'title': ''},
                   {'silverpop api key': '', 'id': 'silverpop_field1', 'title': ''}]
        del self.testform.silverpop_field1
        self.testadapter.set_mapping(mapping)
        result = self.testadapter.get_mapping()
        self.failUnless(result ==
            [{'silverpop api key': 'key1', 'id': 'silverpop_field3', 'title': ''},
             {'silverpop api key': 'key2', 'id': 'silverpop_field2', 'title': ''}]
            )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMapping))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
