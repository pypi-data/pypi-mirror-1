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

'''
Extensions for the standard urllib2 to support RESTful client applications.
'''

try: # Python 3.x
    from urllib.request import *
except ImportError: # Python 2.x
    from urllib2 import *

class RestfulHTTPErrorProcessor(HTTPErrorProcessor):
    def http_response(self, request, response):
        '''Overridden urllib2.Request.get_method to return error responses
        as they are'''
        #code, msg, hdrs = response.code, response.msg, response.info()
        #if code not in (200, 201, 206, 400):
        #    response = self.parent.error('http', request, response, code, msg, hdrs)

        return response

class RestfulRequest(Request):
    def __init__(self, url, data=None, headers={}, origin_req_host=None, unverifiable=False, method=None):
        '''Create a new RestfulRequest. See urllib2.Request for details. Additions:
        
        method: Force HTTP method to be used, instead of the default behavior of
        guessing between POST and GET. You can use any legal HTTP/1.1 method here,
        e.g. GET, POST, PUT, DELETE.
        
        Example:
        req = RestfulRequest('http://test.domain', data='Spam', method='PUT')
        '''
        Request.__init__(self, url, data=data, headers=headers,
                         origin_req_host=origin_req_host, unverifiable=unverifiable)
        
        self.method = method
    
    def get_method(self):
        '''Overridden urllib2.Request.get_method to return the forced HTTP method if set'''
        return self.method or Request.get_method(self)

    def __str__(self):
        method = self.get_method()
        s = '%s %s' % (method, self.get_full_url())
        if method in ('POST', 'PUT'):
            s += ' ' + self.data
        
        return s
