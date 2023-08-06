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


"""aspsms provides an interface to the aspsms.com services
  
  references: http://www.aspsms.com/xml/doc/xmlsvr191.pdf

  ASPSMS: Main Class
"""

__author__ = 'Jacques Supcik'
__version  = '0.1.3'

import httplib
import random
import xml.dom.minidom
from warnings import warn
from aspsms.aspxml import aspxml

valid_action = {
  'send_random_logo'               : 'SendRandomLogo',
  'send_text_sms'                  : 'SendTextSMS',
  'send_picture_message'           : 'SendPictureMessage',
  'send_logo'                      : 'SendLogo',
  'send_group_logo'                : 'SendGroupLogo',
  'send_ringtone'                  : 'SendRingtone',
  'inquire_delivery_notifications' : 'InquireDeliveryNotifications',
  'show_credits'                   : 'ShowCredits',
  'send_vcard'                     : 'SendVCard',
  'send_binary_data'               : 'SendBinaryData',
  'send_wap_push_sms'              : 'SendWAPPushSMS',
  'send_originator_unlock_code'    : 'SendOriginatorUnlockCode',
  'unlock_originator'              : 'UnlockOriginator',
  'check_originator_authorization' : 'CheckOriginatorAuthorization'
}

class ASPSMS(object):
    """Main Class
    """

    #Default values for members
    reply = None

    def __init__(self, **kwargs):
        """Creates a new ASMSMS object"""

        self.message = aspxml(**kwargs)

    def reply_attribute(self, attribute):
        """"Extracts an attribute from the reply"""

        i=self.reply.getElementsByTagName(attribute).item(0)
        return (i != None and i.firstChild.data) or None

    def __send(self):
        """Sends the message"""

        urls = [
            "xml1.aspsms.com:5061", "xml1.aspsms.com:5098",
            "xml2.aspsms.com:5061", "xml2.aspsms.com:5098",
        ]
        random.shuffle(urls)

        while urls:
            try:
                url = urls.pop(0)
                conn = httplib.HTTPConnection(url)
                conn.request("POST", "/xmlsvr.asp", str(self.message))
                r = conn.getresponse()
                reply = r.read()
                if r.status == 200:
                    break
                warn("Error % (%)" % (r.status, r.reason))
            except Exception, inst:
                warn("%s / error using %s" % (inst, url))
  
        self.reply = xml.dom.minidom.parseString(reply)
        self.error_code = self.reply_attribute("ErrorCode")
        self.error_description = self.reply_attribute("ErrorDescription")

    def __getattr__(self, name):
        def decorated(*args, **kwargs):
            return self.action(name, *args, **kwargs)

        if valid_action.has_key(name):
            return decorated
        else:
            raise AttributeError

    def set (self, **kwargs):
        for key in kwargs:
            setattr(self.message, key, kwargs[key])

    def action(self, name, **kwargs):
        for key in kwargs:
            setattr(self.message, key, kwargs[key])

        self.message.Action = valid_action[name]
        self.__send()

