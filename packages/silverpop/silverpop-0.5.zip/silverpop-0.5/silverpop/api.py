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


def log(msg):
    logging.getLogger(LOGGER).debug(msg)


def simple_submit(api_url, xml):
    """submit a request to silverpop
       api_url, xml are required
       intended to be used, when the response of
       silverpop doesn't need to be interpreted further
       returns True, if the API request was successful,
       otherwise False
    """
    response = xml_request(api_url, xml)
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
    return simple_submit(api_url, xml)


def update_recipient(api_url, list_id, old_email, columns=[]):
    """Update recipient of a list,
       if the old_email is not a recipient of the list, a recipient will be added.
       api_url, list_id, old_email are required, optionally
       takes a list of dicts to define additional columns like:
       [{'column_name':'State', 'column_value':'Germany'},]
       Can change the email of a recipient by specifiying a column like:
       {'column_name':'EMAIL', 'column_value':'new@email.com'}
       Can re-opt-in an opted-out recipient by specifying a column like:
       {'column_name':'OPT_OUT', 'column_value':'False'}
       returns True or False
    """
    parts = []
    parts.append("""<Envelope>
  <Body>
    <UpdateRecipient>
      <LIST_ID>%s</LIST_ID>
      <CREATED_FROM>2</CREATED_FROM>
      <OLD_EMAIL>%s</OLD_EMAIL>""" % (list_id, old_email)
          )

    for column in columns:
        parts.append("""
      <COLUMN>
        <NAME>%s</NAME>
        <VALUE>%s</VALUE>
      </COLUMN>""" % (column['column_name'], column['column_value'])
              )

    parts.append("""
    </UpdateRecipient>
  </Body>
</Envelope>"""
        )
    xml = "".join(parts)
    return simple_submit(api_url, xml)



def is_opted_in(api_url, list_id, email):
    """Is the specified email opted in to the list?
       api_url, list_id, email are required
       returns True or False
    """
    response = select_recipient_data(api_url, list_id, email)
    result = response.lower()
    if '<success>false</success>' in result:
        return False
    elif '<optedout/>' in result:
        return True
    else:
        return False

def opt_in_recipient(api_url, list_id, email, columns=[]):
    """opt in a recipient to a list (only email key supported)
       api_url, list_id, email are required, optionally
       takes a list of dicts to define additional columns like
       [{'column_name':'State', 'column_value':'Germany'},]
       returns True or False
    """
    columns = filter(lambda column:column['column_name'] != 'OPT_OUT', columns)
    columns.insert(0, {'column_name': 'OPT_OUT', 'column_value': 'False'})
    return update_recipient(api_url, list_id, email, columns)


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
    return simple_submit(api_url, xml)


def select_recipient_data(api_url, list_id, email, column=None):
    """get the recipients data
       api_url, list_id, email are required
       you may specify a column dict for non email key lists, like
       {'column_name': 'USER_ID', 'column_value': '4711'}
       returns the silverpop response (xml)
    """
    parts = []
    parts.append("""<Envelope>
  <Body>
    <SelectRecipientData>
       <LIST_ID>%s</LIST_ID>
       <EMAIL>%s</EMAIL>""" % (list_id, email)
          )

    if column:
        parts.append("""
       <COLUMN>
         <NAME>%s</NAME>
         <VALUE>%s</VALUE>
       </COLUMN>""" % (column['column_name'], column['column_value'])
              )

    parts.append("""
    </SelectRecipientData>
  </Body>
</Envelope>"""
        )
    xml = "".join(parts)
    return xml_request(api_url, xml)


def xml_request(api_url, xml):
    """submit a custom xml request
       api_url, xml, are required
       returns the silverpop response (xml)
    """
    log('xml: %s' % xml)

    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    xml = urllib.urlencode({'xml': xml})
    request = urllib2.Request(api_url, xml, headers)

    handle = urllib2.urlopen(request)

    response = handle.read()
    log('Silverpop API response: %s' % response)
    return response


# vim: set ft=python ts=4 sw=4 expandtab :
