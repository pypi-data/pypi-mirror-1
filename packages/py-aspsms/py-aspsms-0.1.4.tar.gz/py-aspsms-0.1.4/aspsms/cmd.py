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

import optparse
import os
import sys

def exit(sms, debug=False):
    if debug:
        print "Debug: return=%s (%s)" % (sms.error_code, sms.error_description)
        print "---BEGIN REPLY---"
        print sms.reply.toprettyxml(),
        print "---END REPLY---"
        
    code = int(sms.error_code)
    if code == 1:
        sys.exit(0)
    elif code == 0:
        print "Error: %s" % sms.error_description
        sys.exit(-1)
    else:
        print "Error: %s" % sms.error_description
        sys.exit(code)


class OptionParser(optparse.OptionParser):

    def __init__(self):
        optparse.OptionParser.__init__(self)
        self.add_option("-u", "--userkey", dest="userkey",
            default=os.environ.get("ASPSMS_USERKEY", None),
            help="user key",
        )
        self.add_option("-p", "--password", dest="password",
            default=os.environ.get("ASPSMS_PASSWORD", None),
            help="password",
        )
        self.add_option("--debug", dest="debug",
            default=os.environ.get("ASPSMS_DEBUG", False),
            action="store_true", help="Debug"
        )

    def add_originator_option(self):
        self.add_option("-o", "--originator", dest="originator",
              default=os.environ.get("ASPSMS_ORIGINATOR", None))

    def add_recipient_option(self):
        self.add_option("-r", "--recipient", dest="recipient",
              default=os.environ.get("ASPSMS_RECIPIENT", None))

