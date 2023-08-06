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

__author__ = 'Jacques Supcik'

class aspxml(object):
    # Note: I wanted to call this class just "xml", but then, I would not
    # have been able to use "xml.dom.minidom" in the api class. I could
    # have solved this issue by importing "absolute_import" from "__future__",
    # but this would have restricted this "py-aspsms" to python 2.5.
    def __init__(self, userkey=None, password=None):
        self.stack = []
        self.xml = ''
        if userkey != None:
            self.tag("Userkey", userkey)
        if password != None:
            self.tag("Password", password)


    def open_tag(self, tag):
        self.xml += "  " * len(self.stack) + "<%s>\n" % tag
        self.stack.insert(-1, tag)

    def close_tag(self, tag=None):
        if tag == None:
            tag = self.stack.pop()
        else:
            self.stack.pop()
        self.xml += "  " * len(self.stack) + "</%s>\n" % tag

    def tag(self, tag, value=''):
        self.xml += "  " * len(self.stack) + "<%s>%s</%s>\n" % \
                (tag, value, tag)

    def __str__(self):
        return '<?xml version="1.0" encoding="ISO-8859-1"?>\n' + \
               '<aspsms>\n' + self.xml + '</aspsms>'

