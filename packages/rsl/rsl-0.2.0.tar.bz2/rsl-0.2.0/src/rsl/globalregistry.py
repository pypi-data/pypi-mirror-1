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
This modules provides the global factory registry.

practical especially for wsdl to find implementations for various
bindings and protocols.
'''
from zope.interface.adapter import AdapterRegistry

FACTORYREGISTRY = AdapterRegistry()

def initrsl():
    '''
    this method must be called once, before rsl is used. this function
    cares about loading and registering all plugins foudn through setuptools.
    
    TODO: this may be possible to be done during import/module initialisation
          time.
    '''
    from pkg_resources import working_set
    for entrypoint in working_set.iter_entry_points('rsl.register', 'method'):
        #print "Loading:", str(entrypoint)
        regfunc = entrypoint.load()
        #print "Register:", entrypoint.module_name
        regfunc()

def registerimpl(interface, name, obj):
    '''
    convenience method to register an implementation for an interface.
    '''
    FACTORYREGISTRY.register((), interface, name, obj)

def lookupimpl(interface, name):
    '''
    convenience method to find a registered implementation for an interface.
    '''
    return FACTORYREGISTRY.lookup((), interface, name)

# initialise rsl library here.
# TODO: maybe do this in a nice global import module for user convenience
initrsl()