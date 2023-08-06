# -*- coding: utf-8 -*-
#
# File: api.py
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

LOGGER="silverpop"


def info(msg):
    logging.getLogger(LOGGER).info(msg)


def submit_to_silverpop(request):
    """submit a request to silverpop"""
    handle = urllib2.urlopen(request)
    response = handle.read()
    info('Silverpop API response: %s' % response)
    result = response.lower()
    if '<success>true</success>' in result:
        return True
    elif '<success>success</success>' in result:
        return True
    elif '<success>false</success>' in result:
        return False
    else:
        return False


def add_recipient(api_url, list_id, email, columns=[]):
    """Add recipient to a list (only email key supported)
       api_url, list_id, email are required, optionally
       takes a list of dicts to define additional columns like
       [{'column_name':'State', 'column_value':'Germany'},]
       returns True or False
    """
    parts = []
    parts.append("""<Envelope>
  <Body>
    <AddRecipient>
      <LIST_ID>%s</LIST_ID>
      <CREATED_FROM>2</CREATED_FROM>
      <UPDATE_IF_FOUND>true</UPDATE_IF_FOUND>
      <COLUMN>
        <NAME>EMAIL</NAME>
        <VALUE>%s</VALUE>
      </COLUMN>""" % (list_id, email)
          )

    for column in columns:
        parts.append("""
      <COLUMN>
        <NAME>%s</NAME>
        <VALUE>%s</VALUE>
      </COLUMN>""" % (column['column_name'], column['column_value'])
              )

    parts.append("""
    </AddRecipient>
  </Body>
</Envelope>"""
        )
    xml = "".join(parts)
    info('xml: %s' % xml)
    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    xml = urllib.urlencode({'xml': xml})
    req = urllib2.Request(api_url, xml, headers)
    return submit_to_silverpop(req)


def is_opted_in(api_url, list_id, email):
    """Is the specified email opted in to the list?
       api_url, list_id, email are required
       returns True or False
    """

    return True


def opt_out_recipient(api_url, list_id, email):
    """opt out a recipient from a list
       api_url, list_id, email are required
       returns True or False
    """
    xml = """<Envelope>
  <Body>
    <OptOutRecipient>
      <LIST_ID>%s</LIST_ID>
      <EMAIL>%s</EMAIL>
    </OptOutRecipient>
  </Body>
</Envelope>""" % (list_id, email)
    info('xml: %s' % xml)
    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    xml = urllib.urlencode({'xml': xml})
    req = urllib2.Request(api_url, xml, headers)
    return submit_to_silverpop(req)


def select_recipient_data(api_url, list_id, email, columns=[]):
    """get the recipients data
       api_url, list_id, email are required
       returns a string (xml)
    """

    return '<tobedone>foo</tobedone>'


def xml_request(api_url, xml):
    """submit a custom xml request
       api_url, xml, are required
       returns a string (xml)
    """

    return '<tobedone>foo</tobedone>'

# vim: set ft=python ts=4 sw=4 expandtab :
