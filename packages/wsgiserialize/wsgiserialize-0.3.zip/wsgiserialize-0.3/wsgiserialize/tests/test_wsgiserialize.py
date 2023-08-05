# Copyright (c) 2006 L. C. Rees.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 2.  Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 3.  Neither the name of the Portable Site Information Project nor the names
# of its contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import unittest
from wsgiserialize import *


class WsgiSerializerTest(unittest.TestCase):
        
    def test_jsonize(self):
        @json.jsonize
        def dummy_app(environ, start_response):
            return dict(tuple=(), list=[], str='', dict={}, int=1)
        self.assertEqual(dummy_app({}, ()), ['{"int": 1, "dict": {}, "list": [], "str": "", "tuple": []}'])

    def test_marshaller(self):
        @marshaller.marshaller
        def dummy_app(environ, start_response):
            return dict(tuple=(), list=[], str='', dict={}, int=1)
        self.assertEqual(dummy_app({}, ()), ['{t\x03\x00\x00\x00inti\x01\x00\x00\x00t\x04\x00\x00\x00dict{0t\x04\x00\x00\x00list[\x00\x00\x00\x00t\x03\x00\x00\x00strt\x00\x00\x00\x00t\x05\x00\x00\x00tuple(\x00\x00\x00\x000'])

    def test_cpickler(self):
        @cpickler.cpickler
        def dummy_app(environ, start_response):
            return dict(tuple=(), list=[], str='', dict={}, int=1)
        self.assertEqual(dummy_app({}, ()), ["(dp1\nS'int'\np2\nI1\nsS'dict'\np3\n(dp4\nsS'list'\np5\n(lp6\nsS'str'\np7\nS''\nsS'tuple'\np8\n(ts."])

    def test_pickler(self):
        @pickler.pickler
        def dummy_app(environ, start_response):
            return dict(tuple=(), list=[], str='', dict={}, int=1)
        self.assertEqual(dummy_app({}, ()), ["(dp0\nS'int'\np1\nI1\nsS'dict'\np2\n(dp3\nsS'list'\np4\n(lp5\nsS'str'\np6\nS''\np7\nsS'tuple'\np8\n(ts."])

    def test_yamlize(self):
        @yamlize.yamlize
        def dummy_app(environ, start_response):
            return dict(tuple=(), list=[], str='', dict={}, int=1)
        self.assertEqual(dummy_app({}, ()), ["dict: {}\nint: 1\nlist: []\nstr: ''\ntuple: !!python/tuple []\n"])

    def test_xmlrpc(self):
        @xmlrpc.xmlrpc
        def dummy_app(environ, start_response):
            return dict(tuple=(), list=[], str='', dict={}, int=1)
        self.assertEqual(dummy_app({}, ()), ['<params>\n<param>\n<value><struct>\n<member>\n<name>int</name>' \
'\n<value><int>1</int></value>\n</member>\n<member>\n<name>dict</name>\n<value><struct>\n</struct></value>\n' \
'</member>\n<member>\n<name>list</name>\n<value><array><data>\n</data></array></value>\n' \
'</member>\n<member>\n<name>str</name>\n<value><string></string></value>\n</member>\n' \
'<member>\n<name>tuple</name>\n<value><array><data>\n</data></array></value>\n' \
'</member>\n</struct></value>\n</param>\n</params>\n'])


if __name__ == '__main__': unittest.main()      
            
        

