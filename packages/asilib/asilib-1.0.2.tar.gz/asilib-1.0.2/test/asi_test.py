#! /usr/bin/env python
#
# Copyright (c) 2009, Nokia Corp.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Nokia nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED THE COPYRIGHT HOLDERS AND CONTRIBUTORS ''AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__author__ = 'eemeli.kantola@iki.fi (Eemeli Kantola)'

import unittest
import doctest

from minimock import Mock

import asilib.restlib as restlib
import asilib
import opensocial.data as data

class TestModule(unittest.TestCase):
    def test_doc(self):
        doctest.testmod(asilib)

class TestASIConnection(unittest.TestCase):
    def setUp(self):
        restlib.RestfulRequest = Mock('restlib.RestfulRequest')
        restlib.RestfulRequest.mock_returns = request = Mock('request')
        request.get_type.mock_returns = 'http'
        
        restlib.build_opener = Mock('ASIConnection.build_opener')
        restlib.build_opener.mock_returns = opener = Mock('opener')
        opener.open.mock_returns = self.req_data = Mock('req_data')
        
        self.ac = asilib.ASIConnection('http://foo')
    
    def test_open(self):
        self.req_data.read.mock_returns = '{"entry": {"user_id": null, "app_id": "1234"}}'
        self.ac.open()
        self.assertEquals('1234', self.ac.session['entry']['app_id'])
        self.assertEquals(None, self.ac.session['entry']['user_id'])
    
    def test_do_request_object(self):
        self.req_data.read.mock_returns = '{"entry": {"username": "vince", "irc_nick": "da_vince"}}'
        obj = self.ac.do_request('/hubbabubba')
        self.assertEquals('vince', obj['entry']['username'])
        self.assertEquals('da_vince', obj['entry']['irc_nick'])
    
    def test_do_request_person(self):
        self.req_data.read.mock_returns = '{"entry": {"username": "vince", "irc_nick": "da_vince"}}'
        person = self.ac.do_request('/hubbabubba', data_type=data.Person)
        self.assertEquals('vince', person.username)
        self.assertEquals('da_vince', person.irc_nick)
    
    def test_do_request_collection(self):
        json = '{"entry": [{"wone": 1}, {"twoo": 2}, {"tree": 3}]}'
        self.req_data.read.mock_returns = json
        collection = self.ac.do_request('/hubbabubba', data_type=(data.Collection, data.Object))
        self.assertEquals(eval(json)['entry'], collection[:])

    def test_do_request_empty_collection(self):
        json = '{"entry": []}'
        self.req_data.read.mock_returns = json
        collection = self.ac.do_request('/hubbabubba', data_type=(data.Collection, data.Object))
        self.assertEquals(eval(json)['entry'], collection[:])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
