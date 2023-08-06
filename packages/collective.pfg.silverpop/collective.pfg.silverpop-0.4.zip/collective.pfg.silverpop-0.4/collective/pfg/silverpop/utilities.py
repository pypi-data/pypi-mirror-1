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

from Acquisition import aq_parent
from zope.annotation.interfaces import IAnnotations

from collective.pfg.silverpop.config import COLUMN_NAME_PREFIX
from collective.pfg.silverpop.config import COLUMN_MAPPING
from collective.pfg.silverpop.config import SILVERPOP_API_KEY_IDENTIFIER


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


def make_request(apiurl, listid, data, fields=[], ignores=[]):
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
        fields_for_key = filter(lambda field: field.id == key, fields)
        num_fields = len(fields_for_key)
        if num_fields != 1:
            info("warning: got %d fields for id %s: %s" % (num_fields, key, fields_for_key))
            xkey = transform_column_name(key)
        else:
            xkey = transform_column_name(key, fields_for_key[0])
        if xkey is not None:
            xdata[xkey] = data[key]

    if not len(xdata):
        return

    xml = construct_xml(listid, xdata, ignores)
    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    xml = urllib.urlencode({'xml': xml})
    req = urllib2.Request(apiurl, xml, headers)
    submit_to_silverpop(req)


def transform_column_name(id, field=None):
    """Xlate column name from plone IDs to silverpop column names
       respect user defined mappings
    """
    if not id.startswith(COLUMN_NAME_PREFIX):
        return None
    silverpop = COLUMN_MAPPING.get(id, id)
    if not field:
        info("warning, no field for id %s, no user defined mappings for this field possible" % id)
        #we have no user defined mapping, cut away the prefix
        silverpop = silverpop[len(COLUMN_NAME_PREFIX):]
        return silverpop

    if get_storage(field)[SILVERPOP_API_KEY_IDENTIFIER] != '':
        #we have a user defined mapping, apply it
        silverpop = get_storage(field)[SILVERPOP_API_KEY_IDENTIFIER]
    else:
        #we have no user defined mapping, cut away the prefix
        silverpop = silverpop[len(COLUMN_NAME_PREFIX):]
    return silverpop


def get_mapping(self):
    """return a mapping like
            [{'silverpop api key': '', 'id': 'silverpop_field3', 'title': 'sometitle'},
             {'silverpop api key': 'KEY For SilverPOP API ', 'id': 'silverpop_field1', 'title': ''}]
    """
    mapping = []
    form_folder = aq_parent(self)
    ids = filter(lambda x: x.startswith(COLUMN_NAME_PREFIX), form_folder.objectIds())
    for id in ids:
        if id == self.id:
            # we are the silverpop adapter itself, do nothing
            pass
        elif id in COLUMN_MAPPING:
            # we are a special field, with a not editable mapping,
            # do nothing
            pass
        else:
            field = getattr(form_folder, id, None)
            if field:
                mapping.insert(0, get_storage(field))
    return mapping


def set_mapping(self, mapping):
    """we get a mapping like
        [{'id': 'field-1', 'orderindex_': '1', 'silverpop api key': 'aaaa', 'title': 'this is temporary'},
        {'id': 'field-2', 'orderindex_': '2', 'silverpop api key': 'bbbb', 'title': 'this is temporary'},
        {'orderindex_': 'template_row_marker', 'silverpop api key': ''}]
    """
    form_folder = aq_parent(self)
    for field_mapping in mapping:
        field = getattr(form_folder, field_mapping.get('id', ''), None)
        if field:
            set_storage(field, field_mapping)


def set_storage(field, mapping={SILVERPOP_API_KEY_IDENTIFIER: ''}):
    """ store the mapping sivlerpop_api_key in the annotations of the field object,
        if no mapping is provided, or the included silverpop_api_key is '', remove the annotation,
        ignore any other keys int the mapping dict
    """
    annotations = IAnnotations(field)
    if mapping.get(SILVERPOP_API_KEY_IDENTIFIER, '') == '' and SILVERPOP_API_KEY_IDENTIFIER in annotations:
        del annotations[SILVERPOP_API_KEY_IDENTIFIER]
    else:
        annotations[SILVERPOP_API_KEY_IDENTIFIER] = mapping[SILVERPOP_API_KEY_IDENTIFIER]


def get_storage(field):
    """ return a the field mapping dict with keys id, title, SILVERPOP_API_KEY_IDENTIFIER
    """
    annotations = IAnnotations(field)
    field_mapping = dict(id=field.id, title=field.title)
    field_mapping.update({SILVERPOP_API_KEY_IDENTIFIER: annotations.get(SILVERPOP_API_KEY_IDENTIFIER, '')})
    return field_mapping

# vim: set ft=python ts=4 sw=4 expandtab :
