##############################################################################
# Copyright 2008, Gerhard Weis
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * Neither the name of the authors nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT
##############################################################################
'''
This module adds some extensions to the urllib2 opener.

1. A request object, which can do all sorts of HTTP request 
   (not just GET and POST)
2. A password handler, which asks the user at the command line
3. A cache handler, which reads requests from the local cache instead of 
   requesting again
4. A cookie handler, which persists cookies and reuses them

urllib2 installs also a proxy handler, which reads configuration from envvars.
    http_proxy, https_proxy, tp_proxy, aso.....
    
TODO:
Proxy: for more fine grained proxy control, a new proxy implementation has to 
       be written also maybe it would be nice to add .pac support via 
       pacparser module:  http://pacparser.googlecode.com/
Auth: add some sort of password cache. 
    What about other mechanisms (may require validation of server too) ?
    ... SP-NEGO, SSL-Certs, aso...
    
There are some hard coded path names in here. Should be made configurable.
'''

import getpass
import sys
import os
import md5

from urllib2 import Request as Urllib2Request
from urllib2 import HTTPPasswordMgrWithDefaultRealm, BaseHandler
from urllib2 import HTTPCookieProcessor
from urllib2 import HTTPBasicAuthHandler, build_opener, install_opener
from cookielib import LWPCookieJar
from httplib import HTTPMessage
from StringIO import StringIO

class Request(Urllib2Request):
    '''
    An urllib2.Request implementation, which allows to set the HTTP-Method.
    
    It can be used as full transparent replacement for the original urllib2
    Request class. 
    '''
    
    def __init__(self, url, data=None, headers={},
                 origin_req_host=None, unverifiable=False,
                 method=None):
        Urllib2Request.__init__(self, url, data, headers, origin_req_host, 
                                unverifiable)
        self.method = method
        
    def get_method(self):
        '''
        return http request method as string.
        '''
        if self.method is None:
            return Urllib2Request.get_method(self)
        return self.method
    

class AskPasswordHandler(HTTPPasswordMgrWithDefaultRealm):
    '''
    urllib2 password handler, which asks user on command line to 
    provide username and password.
    '''
    
    def find_user_password(self, realm, authuri):
        '''
        use base class to find password. if no password available, ask user
        on command line to provide one.
        '''
        user, passw = HTTPPasswordMgrWithDefaultRealm.find_user_password(self, 
                                                            realm, authuri)
        if user is None:
            user = getpass.getuser()
            sys.stdout.write('username (%s):' % user)
            newuser = sys.stdin.readline().strip()
            if newuser is not None and len(newuser) > 0:
                user = newuser
        if passw is None:
            passw = getpass.getpass('password for %s:' % user)
            #passw = raw_input('password for %s:' % user)
        HTTPPasswordMgrWithDefaultRealm.add_password(self, realm, authuri, 
                                                     user, passw)
        return user, passw
    
# CacheHandler and CacheResponse taken from 
#      http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/491261
class CacheHandler(BaseHandler):
    """Stores responses in a persistant on-disk cache.

    If a subsequent GET request is made for the same URL, the stored
    response is returned, saving time, resources and bandwith"""
    def __init__(self, cachelocation):
        """The location of the cache directory"""
        self.cachelocation = cachelocation
        if not os.path.exists(self.cachelocation):
            os.mkdir(self.cachelocation)
            
    def default_open(self, request):
        '''
        open url and return response. If http request is GET, then try cache.
        and return cached response if available. else return None and let
        next handler try to retrieve data.
        '''
        if ((request.get_method() == "GET") and 
            (CachedResponse.existsincache(self.cachelocation, 
                                          request.get_full_url()))):
            # print "CacheHandler: Returning CACHED response for %s"
            #       % request.get_full_url()
            return CachedResponse(self.cachelocation, 
                                  request.get_full_url(), setcacheheader=True)    
        else:
            return None # let the next handler try to handle the request

    def http_response(self, request, response):
        '''
        store response in cache if necessary.
        '''
        if request.get_method() == "GET":
            if 'x-cache' not in response.info():
                CachedResponse.storeincache(self.cachelocation, 
                                            request.get_full_url(), response)
                return CachedResponse(self.cachelocation, 
                                      request.get_full_url(), 
                                      setcacheheader=False)
            else:
                return CachedResponse(self.cachelocation, 
                                      request.get_full_url(), 
                                      setcacheheader=True)
        else:
            return response
    
class CachedResponse(StringIO):
    """An urllib2.response-like object for cached responses.

    To determine wheter a response is cached or coming directly from
    the network, check the x-cache header rather than the object type."""
    
    @classmethod
    def existsincache(cls, cachelocation, url):
        '''
        return true, if response for url exists in cache.
        '''
        md5hash = md5.new(url).hexdigest()
        return (os.path.exists(cachelocation + "/" + md5hash + ".headers") and 
                os.path.exists(cachelocation + "/" + md5hash + ".body"))

    @classmethod
    def storeincache(cls, cachelocation, url, response):
        '''
        store response to url in cache.
        '''
        md5hash = md5.new(url).hexdigest()
        fobj = open(cachelocation + "/" + md5hash + ".headers", "w")
        headers = str(response.info())
        fobj.write(headers)
        fobj.close()
        fobj = open(cachelocation + "/" + md5hash + ".body", "w")
        fobj.write(response.read())
        fobj.close()
    
    def __init__(self, cachelocation, url, setcacheheader=True):
        '''
        initialise response object with data from cache.
        '''
        self.cachelocation = cachelocation
        md5hash = md5.new(url).hexdigest()
        StringIO.__init__(self, file(self.cachelocation + "/" + md5hash +
                                     ".body").read())
        self.url     = url
        self.code    = 200
        self.msg     = "OK"
        headerbuf = file(self.cachelocation + "/" + md5hash+".headers").read()
        if setcacheheader:
            headerbuf += "x-cache: %s/%s\r\n" % (self.cachelocation, md5hash)
        self.headers = HTTPMessage(StringIO(headerbuf))

    def info(self):
        '''
        return http headers.
        '''
        return self.headers
    
    def geturl(self):
        '''
        return url for this response.
        '''
        return self.url

OPENER = None
COOKIEJAR = None 

def installopener():
    '''
    install caching urllib2-opener.
    '''
    global OPENER, COOKIEJAR
    if not OPENER:
        cache_handler = CacheHandler(os.path.expanduser('~/.wss/urllib2_cache'))
        COOKIEJAR = LWPCookieJar(os.path.expanduser('~/.wss/cookies.txt'))
        try:
            COOKIEJAR.load()
        except IOError:
            pass
        cookie_handler = HTTPCookieProcessor(COOKIEJAR)
        auth_handler = HTTPBasicAuthHandler(AskPasswordHandler())
        auth_handler.add_password('realm', 'host', 'username', 'password')
        OPENER = build_opener(cache_handler, cookie_handler, auth_handler)
    install_opener(OPENER)
    return OPENER

def deinstallopener():
    '''
    uninstall caching urllib2 opener.
    '''
    global OPENER, COOKIEJAR
    if OPENER:
        install_opener(None)
    COOKIEJAR.save()
    COOKIEJAR = None
    OPENER = None
