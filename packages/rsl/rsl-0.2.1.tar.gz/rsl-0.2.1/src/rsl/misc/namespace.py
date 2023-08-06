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
This module defines some helper functions to deal with xml-namespace-urls to
xml-namespace-prefix mappings. It also defines a couple of methods to  
convert from Clark-notation to xml-notation. 
'''

def qname2tuple(name, nsmap):
    '''
    Convert a xml-QNAME to a tuple. The tuple then contains
    the namespace url.
    '''
    if name is None:
        return None, None
    if name.find(':') > 0:
        xns, localname = name.split(':')
        return nsmap[xns], localname
    else:
        # if no namespace prefix use default namespace
        if None in nsmap:
            return nsmap[None], name
        return None, name
    
def url2ns(nsurl, nsmap):
    '''
    Convert a namespace url to a xml-namespace-prefix.
    '''
    for key, value in nsmap.items():
        if nsurl == value:
            return key
    raise KeyError("%s not found" % (nsurl))
    
def clark2qname(cname, nsmap):
    '''
    Convert a QName in Clark notation to a QName.
    '''
    xns, name = clark2tuple(cname)
    if xns is None:
        return name
    else:
        return "%s:%s" % (url2ns(xns, nsmap), name)
    
def qname2clark(name, nsmap):
    '''
    Convert a QName to a QName in Clark notation.
    '''
    if name is None:
        return None
    xns, name = qname2tuple(name, nsmap)
    return clark(xns, name)
    
def clark2tuple(name):
    '''
    Convert a QName in Clark notation into a tuple.
    '''
    if name[0] == '{':
        return name[1:].split('}')
    else:
        return None, name

def clark(xns, name):
    '''
    Create a QName in Clark notation using a namespace url
    and a name.
    '''
    if xns is None:
        return name
    return "{%s}%s" % (xns, name)
