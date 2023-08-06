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
this modules defines and documents all global interfaces which decribe the
minimal API a user needs to invoke remote services.
'''
from zope.interface import Interface, Attribute

# TODO: maybe define default Callable interface....
#          has name, paramnames, paramtypes?
#          methods: serialize, deserialize, send, __call__
#       is maybe helpful to provide consistent introspection on proxy objects and callables

class IServiceDescription(Interface):
    '''
    This interface represents a serivce proxy factory. It maintains all necessary
    information to create an IProxy object.
    '''
    
    url = Attribute('''The url from where the description was retrieved. 
    This is especially useful for XML based descriptions to support relative URL imports.''')
    
    def fromURL(url, **kw):
        '''
        Initialise a service description from an URL.
        What kind of resource the URL represents depends on the implementing class.
        e.g.: a WSDL needs an URL to a WSDL document, a XMLRPC-Service needs an XMLRPC endpoint.
        '''
    
    def getProxy(**kw): # common properties: name
        '''
        Return an IProxy instance to access the service described by this description.
        
        TODO: maybe remove this method and replace it with adapter functionality from zope.interface
              => adapt IServiceDescription to IProxy.
        '''

class IProxyFactory(Interface):
    '''
    This interface only exists, to declare an __init__ parameter for classes which implement IProxy.
    '''
    
    def __call__(location):
        '''
        Create an IProxy instance, which uses location as target address.
        '''

class IProxy(Interface):
    
    callables = Attribute('''A dict object containing a mapping from method names to callable objects.
    This attribute may not contain all available methods. e.g. an XMLRPC-service may provide methods, even it is not introspectable.''')
    
    location = Attribute('''The base location of a service endpoint.''')

    def addOperation(name, operationinfo):
        '''
        add definition for operation to this proxy. This proxy creates a callable
        for this definition and adds it to it's class.
        
        name ... should be a legal python identifier, so that operation is callable as normal python function
                 else operation has to be called over callables dictionary.
        operationinfo ... an IOperationInfo instance the proxy can use to offer methods.
        
        
        TODO: instead of direct access to callables dict, maybe add method callRemote(name, params)
        '''
        
    def callRemote(name, *args, **kw):
        '''
        Invoke a remote method.
        
        name ... the name of the operation
        *args, **kw ... parameters to pass
        '''
        
class IOperationInfo(Interface):
    '''
    A data instance which holds all necessary information for remote methods.
    
    TODO: how topack header, body into input/ouput?
          what about faults?
    '''
    name = Attribute('''The name of the operation''')
    
    location = Attribute('''The endpoint of this operation''')
    
    serializer = Attribute('''The serializer to use to create the envelope''')
    
    input = Attribute('''A list of IParamInfo instances which holds the information for parameters''')
    
    output = Attribute('''A list of IParamInfo instances which holds the information for return values''')
    
    typesystem = Attribute('''An ISchema instance to access data type meta infos''')

class IParamInfo(Interface):
    '''
    A data instance which holds all necessary information for parameters.
    '''
    name = Attribute('''The name of this parameter''')
    
    type = Attribute('''The name of the type for this parameter''')
    
    serializer = Attribute('''The name of a registered ISerializer/IDeserializer instance''')

# TODO: find out how to describe required parameters for IProxy __init__ methods. (do this with __call__ ? or __init__?, or do I need some kind of ProxyFactory which does this for me?
# TODO: go through the following structure and apply it for all getProxy methods and IProxy methods consistently
#Descr: service + 
#        location +
#        protocol 1

class ITransport(Interface):
    '''
    This interface is an abstraction to send a synchronous request over the network and
    receive a response.
    
    TODO: This interface is not designed that well. There is a need for synchronous and
          asynchronous requests.
          maybe restrict to application need. e.b. If an application needs to depend on
          asynchronous requests, then it should define it's own transport (twisted?)
    '''
    
    def send(dest, data, **kw): # comman params: method, headers
        '''
        Send data to destination and return an implementation dependent response object.
        '''

class ISerializer(Interface):
    '''
    This interface provides one method to serialize arbitrary data according to additional infos
    into something which can be transferred.
    '''
    
    def serialize(data, operationinfo, **kw):
        '''
        data ... data to serialize... may be any type of python object.
        
        operationinfo ... an IOperationInfo instance
        
        **kw additional infos, a serializer could need to perform encoding.
        
        returns a tuple (headers, payload)
        '''

class IDeserializer(Interface):
    '''
    This interface provides one method to deserialize a data block into some python structure.
    '''
    
    def deserialize(data, operationinfo, **kw):
        '''
        data ... data to deserialize... in most cases this will be a string
        
        **kw additional infos, a serializer could need to perform encoding.
        
        returns a tuple (headers, result)
        '''    

class ISchema(Interface):
    '''
    a schema provides a mapping from names to type declarations.
    
    This interface is for classes which implement an ISchema interface.
    The default way to instantiate an ISchema, is to call the constructor
    and afterwards initialise the ISchema instance with the frometree method.
    '''
    
    targetnamespace = Attribute('''The name of the Schema.''')
    
    manager = Attribute('''The SchemaCollection where this Schema is included in.''')
    
    def frometree(etree):
        '''
        create schema structure from etree root element.
        
        this may be a xsd:import or rng:include element, or a
        complete xsd:schema or rng:grammar
        '''
        
class ISchemaFactory(Interface):
    '''
    This interface serves the purpose, where a function is provided, which
    returns a complete instantiated ISchema.
    '''
    def __call__(parent):
        '''
        Creates a new ISchema instance.
        parent should be an ISchemaCollection
        '''

class ISchemaCollection(Interface):
    '''
    a schema collection itself implements partly the schema interface but can contain 
    multiple schemas. schema lookup happens in the schema collection itself and strictly 
    upwards, not sideways.
    '''
    
    def addSchema(schema):
        ''' Add a Schema to this SchemaCollection. '''
        
    # FIXME: doc strings
    # TODO: check whether __getattr__ interface is suitable or not.
    def getSchema(name):
        ''' Return a Schema by name.
        If the name is not defined in this collection the parent SchemaCollection
        is asked. If no Schema is found, a XXXException is thrown. '''
