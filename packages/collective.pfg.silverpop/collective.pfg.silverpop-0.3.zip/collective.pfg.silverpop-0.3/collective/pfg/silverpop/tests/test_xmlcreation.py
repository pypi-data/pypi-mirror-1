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

from collective.pfg.silverpop.tests.base import TestCase

from collective.pfg.silverpop.utilities import construct_xml

XML1 = "<Envelope><Body><AddRecipient><LIST_ID>1</LIST_ID>\
<CREATED_FROM>2</CREATED_FROM>\
<UPDATE_IF_FOUND>true</UPDATE_IF_FOUND><COLUMN><NAME>State</NAME>\
<VALUE>Germany</VALUE></COLUMN><COLUMN><NAME>EMAIL</NAME>\
<VALUE>x@x.com</VALUE></COLUMN></AddRecipient></Body></Envelope>"

XML2 = "<Envelope><Body><AddRecipient><LIST_ID>1</LIST_ID>\
<CREATED_FROM>2</CREATED_FROM>\
<UPDATE_IF_FOUND>true</UPDATE_IF_FOUND>\
<COLUMN><NAME>EMAIL</NAME><VALUE>x@x.com</VALUE></COLUMN>\
</AddRecipient></Body></Envelope>"


class TestSetup(TestCase):
    """ test xml creation
    """

    def afterSetUp(self):
        self.setRoles(['Member', 'Manager'])

    def test_email_state(self):
        """we get an EMAIL and a State"""
        listid = 1
        data = {'EMAIL': 'x@x.com', 'State': 'Germany'}
        self.assertEqual(construct_xml(listid, data), XML1)

    def test_ignore(self):
        """if we provide a ignore list, ids in this list
        mustn't lead to nodes in xml
        """
        listid = 1
        data = {'EMAIL': 'x@x.com', 'confirm': True, 'ignore_me': 'something'}
        ignores = ['confirm', 'ignore_me']
        self.assertEqual(construct_xml(listid, data, ignores), XML2)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
