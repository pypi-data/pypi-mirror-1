# -*- coding: utf-8 -*-
#
# File: utils.py
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

import urllib
import urllib2

import logging

from collective.pfg.silverpop.config import COLUMN_NAME_PREFIX
from collective.pfg.silverpop.config import COLUMN_MAPPING


LOGGER="collective.pfg.silverpop"


def info(msg):
    logging.getLogger(LOGGER).info(msg)


def submit_to_silverpop(request):
    """submit a request to silverpop"""
    handle = urllib2.urlopen(request)
    response = handle.read()
    info('Silverpop API response: %s' % response)


def construct_xml(listid, data, ignores=[]):
    """
    construct silverpop xml
    data: dict key = fieldname, value=fieldvalue
    ignore: list of fields to ignore
    system fields must be uppercase,
    all column names are case sensitive
    """
    parts = []
    parts.append("<Envelope><Body><AddRecipient>")
    parts.append("<LIST_ID>%s</LIST_ID>" % listid)
    parts.append("<CREATED_FROM>2</CREATED_FROM>")
    parts.append("<UPDATE_IF_FOUND>true</UPDATE_IF_FOUND>")
    for key in data:
        if key not in ignores:
            parts.append("<COLUMN><NAME>%s</NAME><VALUE>%s</VALUE></COLUMN>" % (key, data[key]))
    parts.append("</AddRecipient></Body></Envelope>")
    xml = "".join(parts)
    info('xml: %s' % xml)
    return xml


def make_request(apiurl, listid, data, ignores=[]):
    """
    construct the request and submit it
    data: dict key = fieldname, value=fieldvalue
    ignore: list of fields to ignore
    system fields must be uppercase,
    all column names are case sensitive
    """
    info("data: %s" % data)
    xdata = dict()

    for key in data:
        xkey = transform_column_name(key)
        if xkey is not None:
            xdata[xkey] = data[key]

    if not len(xdata):
        return

    xml = construct_xml(listid, xdata, ignores)
    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    xml = urllib.urlencode({'xml': xml})
    req = urllib2.Request(apiurl, xml, headers)
    submit_to_silverpop(req)


def transform_column_name(id):
    """Xlate column name from plone IDs to silverpop column names"""
    if not id.startswith(COLUMN_NAME_PREFIX):
        return None

    silverpop = id[len(COLUMN_NAME_PREFIX):].lower()
    return COLUMN_MAPPING.get(silverpop, silverpop)


# vim: set ft=python ts=4 sw=4 expandtab :
