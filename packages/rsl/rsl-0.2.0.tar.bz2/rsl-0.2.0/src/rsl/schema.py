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
This Module defines the global schema manager. Its intent is to provide various
standard schemata. The reason to have them global is, to make them available to 
all sub schemata. This is especially useful for the default XSD Schema and 
various other like XSI and XML aso.... 
'''
from rsl.interfaces import ISchemaCollection
from zope.interface import implements
from warnings import warn

class SchemaManager(object):
    ''' 
    This it the default implementation for SchemaCollection.
    
    Schema lookup happens first in this collection and then strictly upwards.
    '''
    
    implements(ISchemaCollection)
    
    name = 'GlobalSchemaManager'
    
    parent = None
    
    schemamap = {}
    
    def addSchema(self, schema):
        '''
        add an ISchema instance to this schema manager.
        '''
        if schema.name in self.schemamap:
            warn("schema '%s' already in collection '%s' -> will be replaced."
                 % (schema.name, self.name), UserWarning)
        self.schemamap[schema.name] = schema
        
    def getSchema(self, name):
        '''
        return an ISchema instance by name.
        '''
        if name not in self.schemamap:
            if self.parent is not None:
                return self.parent.getSchema(name)
            raise AttributeError()
        return self.schemamap[name]


GLOBALSCHEMAMANAGER = SchemaManager()
