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

import httplib
import random
import re
import xml.dom.minidom
from warnings import warn
from aspsms.aspxml import aspxml

def _sms_encode(s):
    return re.sub(
        r'[\x26\x3c\x3e\x80-\xff]',
        lambda c: '&#'+str(ord(c.group(0)))+';',
        unicode(s, 'utf-8').encode("iso8859_15")
    )

class ASPSMS:
    """Main Class
    """

    #Default values for members
    reply = None

    def __init__(self, user_key=None, password=None, originator=None):
        """Creates a new ASMSMS object"""

        self.user_key = user_key
	self.password = password
	self.originator = originator

    def reply_attribute(self, attribute):
        """"Extracts an attribute from the reply"""

	i=self.reply.getElementsByTagName(attribute).item(0)
	return ((i != None and i.firstChild.data) or None)

    def __send(self, message):
        """Sends the message"""

        urls = [
            "xml1.aspsms.com:5061", "xml1.aspsms.com:5098",
            "xml2.aspsms.com:5061", "xml2.aspsms.com:5098",
        ]
        random.shuffle (urls)

        while urls:
            try:
                url = urls.pop(0)
                conn = httplib.HTTPConnection(url)
                conn.request("POST", "/xmlsvr.asp", message.__str__())
                r = conn.getresponse()
                reply = r.read()
                if r.status == 200:
                    break
                warn ("Error % (%)" % (r.status, r.reason))
            except Exception, inst:
                warn ("%s / error using %s" % (inst, url))
  
        self.reply = xml.dom.minidom.parseString(reply)
	self.error_code = self.reply_attribute("ErrorCode")
	self.error_description = self.reply_attribute("ErrorDescription")

    def send_text_sms(self, recipient, text, originator=None):
        """Sends a text sms

        Args:
          originator: str
          recipient: str
          text: str
        """

        originator = originator or self.originator
        message = aspxml(self.user_key, self.password)
        if originator:
            message.tag('Originator', originator)
        message.open_tag('Recipient')
        message.tag('PhoneNumber', recipient)
        message.close_tag()
        message.tag('MessageData', _sms_encode(text.strip()))
        message.tag('Action', 'SendTextSMS')
        self.__send(message)

    def show_credits (self):
        """Show credits

        Returns:
          the remaining credits.
        """

        message = aspxml(self.user_key, self.password)
        message.tag("Action", "ShowCredits")
        self.__send(message)
	return self.reply_attribute("Credits")

