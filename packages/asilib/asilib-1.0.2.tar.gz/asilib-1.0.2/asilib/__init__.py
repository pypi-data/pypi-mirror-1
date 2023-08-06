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

from __future__ import with_statement # for Python 2.5

__author__ = 'eemeli.kantola@iki.fi (Eemeli Kantola)'

import restlib

try: # Python 3.x
    import http.cookiejar as cookielib
except ImportError: # Python 2.x
    import cookielib

from urllib import quote_plus as q
from datetime import datetime

import json
import urllib
import collections

import opensocial.data as data

# Extend the default Person.__init__ with one that sets the instance fields
# for easier use
oldInitPerson = data.Person.__init__
def initPerson(self, fields):
    oldInitPerson(self, fields)
    self.__dict__.update(fields)
data.Person.__init__ = initPerson

debug = False

def build_param_string(context=None, **kwargs):
    ''' Construct a parameter string using the given mappings.
    
    >>> build_param_string(a='aa', b='two words')
    'a=aa&b=two+words'
    >>> build_param_string()
    ''
    >>> build_param_string('context', a='aa', b='bee')
    'context[a]=aa&context[b]=bee'
    >>> build_param_string('context', subcontext=dict(prop=123))
    'context[subcontext[prop]]=123'
    '''
    
    qs = [''] # Python 2.x's way of Python 3.x's nonlocal.
              # See http://stackoverflow.com/questions/1195577/python-scoping-problem
    
    if context:
        pattern = q(context) + '[%s]=%s'
    else:
        pattern = '%s=%s'

    def qsappend(key, val):
        if qs[0]:
            qs[0] += '&'
        qs[0] += pattern % (key, val)
    
    for key, val in kwargs.items():
        if isinstance(val, dict):
            for subkey, subval in val.items():
                qsappend('%s[%s]' % (q(key), q(subkey)), q(str(subval)))
        else:
            qsappend(q(key), q(str(val)))
    
    return qs[0]

class ASIConnection:
    session_url = '/session'
    people_url = '/people'
    groups_url = '/groups'
    search_url = '/search'

    def __init__(self, base_url, **session_params):
        self.session = {}
        self.session_params = session_params
        
        self.base_url = base_url
        
        self.cookiejar = cookielib.CookieJar()
        self.opener = restlib.build_opener(restlib.HTTPCookieProcessor(self.cookiejar),
                                           restlib.RestfulHTTPErrorProcessor)
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, type, value, traceback):
        self.close()
    
    def open(self):
        self.session = self.do_request(ASIConnection.session_url, 
                                       post_params=build_param_string('session', **self.session_params))
        return self.session
    
    def close(self):
        self.session = {}
        return self.do_request(ASIConnection.session_url, method="DELETE")
    
    def do_request(self, url, data_type=data.Object, post_params=None, get_params=None, method=None):
        ''' Send the actual ASI request and parse response from JSON if possible. Parameters:
        
        url
            The site-relative URL to send the request to. Will be prefixed
            with self.base_url.
        
        data_type
            Expected data subtype of the JSON response. Possible values are
            data.Object, data.Person, and tuple (data.Collection, elementtype)
            where elementtype is either data.Object or data.Person.
        
        post_params
            HTTP POST parameter string
        
        get_params
            HTTP GET parameter string
        
        method
            HTTP method (GET, POST, PUT, DELETE)
        '''
        query_string = '?'+get_params if get_params else ''
        
        request = restlib.RestfulRequest(self.base_url + url + query_string, method=method, data=post_params)
        if debug:
            start_time = datetime.now()
            print(request)
        
        s = self.opener.open(request)
        if debug:
            delta = datetime.now() - start_time
            print('HTTP %i %s (request processed in %i.%06i seconds)'
                  % (s.code, s.msg, delta.seconds, delta.microseconds))
        
        resp_data = s.read()
        if debug:
            print('Response body = "%s"' % resp_data)
        
        try:
            result = json.loads(resp_data.decode('utf-8'))
        except Exception, e:
            return resp_data
        
        #if debug:
            #print(result)
            #print('cookies: ' + str(self.cookiejar))
        
        if isinstance(data_type, collections.Sequence):
            if issubclass(data_type[0], data.Collection) and issubclass(data_type[1], data.Object):
                try:
                    return data_type[0].parse_json(result, data_type[1])
                except TypeError:
                    return []
            else:
                raise TypeError
        elif data_type == data.Object:
            return data.Object(result)
        elif issubclass(data_type, data.Object):
            return data_type.parse_json(result)
        else:
            raise TypeError
    
    def get_session(self):
        return self.do_request(ASIConnection.session_url)

    def search(self, query):
        return self.do_request(ASIConnection.search_url,
                               data_type=(data.Collection, data.Object),
                               get_params = build_param_string(search=query))
    
    def find_users(self, query=None):
        return self.do_request(ASIConnection.people_url,
                               data_type=(data.Collection, data.Person),
                               get_params = query and build_param_string(search=query))
    
    def find_groups(self, query=None):
        return self.do_request(ASIConnection.groups_url + '/@public',
                               data_type=(data.Collection, data.Object),
                               get_params = query and build_param_string(search=query))

    def get_friends(self, uid):
        return self.do_request(ASIConnection.people_url + '/' + uid + '/@friends',
                               data_type=(data.Collection, data.Person))

    def create_user(self, **kwargs):
        ''' Create a user. Parameters:
        username        The desired username. Must be unique in the system.
                        Length 4-20 characters.
        password        User's password.
        email           User's email address.
        is_association  'true' if this user is an association. Associations
                        may be displayed differently by applications, and they
                        cannot send or receive friend requests.
        consent         The version of the consent that the user has agreed to.
                        For example: 'FI1'/'EN1.5'/'SE4'
        '''
        return self.do_request(ASIConnection.people_url,
                               data_type=data.Person,
                               post_params = build_param_string('person', **kwargs))
    
    def get_user(self, uid):
        return self.do_request(ASIConnection.people_url + '/' + uid + '/@self',
                               data_type=data.Person)

    def update_user(self, uid, **kwargs):
        return self.do_request(ASIConnection.people_url + '/' + uid + '/@self',
                               post_params = build_param_string('person', **kwargs),
                               method='PUT')

    def get_location(self, uid):
        return self.do_request(ASIConnection.people_url + '/' + uid + '/@location')
