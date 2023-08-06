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
this module provides an implementation for ITransport based on urllib2.
'''
from zope.interface import implements

from rsl.interfaces import ITransport
from rsl.misc.http import Request

from urllib2 import urlopen, HTTPError

class Urllib2Transport(object):
    '''
    an ITransport http-implementation based on urllib2.
    '''
    
    implements(ITransport)
    
    @classmethod
    def send(cls, dest, data, **kws):
        '''
        send data to destionation.
        
        kw may contain headers and method as params.
        headers ... additional http headers
        method  ... http method to use
        
        all other additional params are ignored.
        
        returns tuple of (header, data) 
        '''
        kwparams = {}
        if 'headers' in kws:
            kwparams['headers'] = kws['headers']
        if 'method' in kws:
            kwparams['method'] = kws['method']
        req = Request(dest, data=data, **kwparams)
        #code = None
        try:
            response = urlopen(req) # URLError if url dows not exist.
            #code = f.code
            respheaders = dict(response.headers)
            respdata = response.read()
            response.close()
        except HTTPError, err:
            # TODO: ignore all HTTPErrors for now till I know which error
            #       codes are legal for SOAP over HTTP or whatever protocol
            #       is used
            # TODO: e.g.: handling of redirect and similar response code would
            #       be nice (if they are applicable for soap)
            #code = err.code
            respheaders = dict(err.headers)
            respdata = err.fp.read()
            err.fp.close()
        # TODO: do something useful with code?
        # response.msg + response.code ... http return values
        return respheaders, respdata
