#!/usr/bin/python
#
# Copyright (C) 2008 Jacques Supcik
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__  = 'Jacques Supcik'
__version__ = '0.1.4'

import re
from types import *


tag_list = ['Userkey', 'AffiliateId', 'Password', 'Originator',
    'UsedCredits', 'Recipient_PhoneNumber', 'Recipient_TransRefNumber',
    'DeferredDeliveryTime', 'LifeTime', 'MessageData', 'URLBinaryFile',
    'FlashingSMS', 'BlinkingSMS', 'MCC', 'MNC',
    'URLBufferedMessageNotification', 'URLDeliveryNotification',
    'URLNonDeliveryNotification', 'TimeZone', 'XSer', 'BinaryFileDataHex',
    'TransRefNumber', 'ReplaceMessage', 'VCard_VName', 'VCard_VPhoneNumber',
    'WAPPushDescription', 'WAPPushURL', 'OriginatorUnlockCode', 'Action',
]

valid_tag = dict.fromkeys(map(lambda x: x.lower(), tag_list), True)

def _sms_encode(s):
    if type(s) is UnicodeType:
        return re.sub(
            r'[\x26\x3c\x3e\x80-\xff]',
            lambda c: '&#'+str(ord(c.group(0)))+';',
            unicode(s, 'utf-8').encode("iso8859_15")
        )
    elif type(s) is StringType:
        return re.sub(
            r'[\x26\x3c\x3e\x80-\xff]',
            lambda c: '&#'+str(ord(c.group(0)))+';', s
        )
    else:
        return s

class aspxml(object):
    # Note: I wanted to call this class just "xml", but then, I would not
    # have been able to use "xml.dom.minidom" in the api class. I could
    # have solved this issue by importing "absolute_import" from "__future__",
    # but this would have restricted the "py-aspsms" module to python 2.5
    # or higher.
    data = dict()

    def __init__(self, **tags):
        for tag in map(lambda x: x.lower(), tags.keys()):
            if valid_tag[tag]:
                self.data[tag] = tags[tag]
            else:
                raise AttributeError

    def __setattr__(self, name, value):
        tag = name.lower()
        if valid_tag[tag]:
            self.data[tag] = value
        else:
            raise AttributeError

    def __getattr__(self, name):
        tag = name.lower()
        if valid_tag[tag]:
            return self.data.get(tag, None)
        else:
            raise AttributeError

    def __str__(self):
        result = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
        result += '<aspsms>\n'
        container = ''
        for tag in tag_list:
            if self.data.has_key(tag.lower()):
                m = (re.match(r'(.+)_(.+)', tag))
                if m:
                    c = m.group(1)
                    t = m.group(2)
                else:
                    c = ''
                    t = tag
                if c != container:
                    if container:
                        result += '  </%s>\n' % container
                    if c:
                        result += '  <%s>\n' % c
                    container = c
                if container:
                    result += '  '
                result += '  <%s>%s</%s>\n' % \
                    (t, _sms_encode(self.data[tag.lower()]), t)
        if container:
            result += '  </%s>\n' % container
        result += '</aspsms>'
        return result

