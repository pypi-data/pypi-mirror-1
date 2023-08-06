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
This module defines all base classes for the various extensions points
available in WSDL.
'''
from warnings import warn

from zope.interface import implements

from rsl.implementations import OperationInfo
from rsl.misc.namespace import qname2clark, clark, clark2tuple
from rsl.wsdl1.namespace import NS_WSDL
from rsl.wsdl1.interfaces import IPort, IBinding, IOperation, IParamInfo 
from rsl.wsdl1.interfaces import IFault
from rsl.wsdl1.wsdl import findextensionfactory, findextensionfactories

class WSDLPort(object):
    '''
    The WSDL-port element.
    '''
    
    implements(IPort)
    
    def __init__(self, wsdl):
        '''
        initialise empty WSDLPort instance.
        '''
        self.wsdl = wsdl
        self.name = None
        self.binding = None
        
    def frometree(self, etree):
        '''
        load data from etree into this instance.
        '''
        self.name = etree.get('name')
        self.binding = qname2clark(etree.get('binding'), etree.nsmap)
        return self

class WSDLBinding(object):
    '''
    The WSDL-binding element.
    '''
    
    implements(IBinding)
    
    def __init__(self, wsdl):
        '''
        initialise a empty WSDLBinding instance.
        '''
        self.wsdl = wsdl
        self.name = None
        self.porttype = None
        self.operations = {} # the parsed instances of wsdl:operation tags
        
    def frometree(self, etree):
        '''
        load data from etree element into this instance and parse sub elements
        like operation.
        '''
        self.name = etree.get('name')
        self.porttype = qname2clark(etree.get("type"), etree.nsmap)
        self._parseoperations(etree.findall(clark(NS_WSDL,'operation')))
        return self
    
    def _parseoperations(self, etrees):
        '''
        parse all binding.operation tags.
        '''
        for opelem in etrees:
            extopelems = opelem.xpath('*[local-name()="operation"]')
            if len(extopelems) > 0:
                xns, _ = clark2tuple(extopelems[0].tag)
                opf = findextensionfactory('rsl.wsdl1.binding.operation', xns)
                operation = opf(self, opelem)
                self.operations[operation.name] = operation
            else:
                warn("can not find binding/operation extension element.")

class WSDLOperation(object):
    '''
    The wsdl binding.operation element.
    '''
    
    implements(IOperation)
    
    def __init__(self, binding):
        '''
        initialise empty instance.
        '''
        self.binding = binding
        self.name = None
        self.input = None
        self.output = None
        self.faults = None # {}
        
    def frometree(self, operationelem):
        '''
        parse data from etree element into this instance and parse sub elements.
        '''
        self.name = operationelem.get('name')
        self._parseinput(operationelem.find(clark(NS_WSDL, 'input')))
        self._parseoutput(operationelem.find(clark(NS_WSDL, 'output')))
        self._parsefaults(operationelem.findall(clark(NS_WSDL, 'fault')))
        # search for extensions like wsaw
        for parsefunc in findextensionfactories('rsl.wsdl1.binding.operation',
                                                'parse'):
            parsefunc(self, operationelem)
        return self
    
    def getOperationInfo(self):
        '''
        return IOperationInfo instance filled with information about this 
        operation.
        '''
        opinfo = OperationInfo()
        opinfo.name = self.name
        opinfo.typesystem = self.binding.wsdl.types
        if self.input is not None:
            opinfo.serializer = self.input.getSerializer()
            opinfo.input = self.input.getParamInfo()
        if self.output is not None:
            opinfo.output = self.output.getParamInfo()
            opinfo.deserializer = self.output.getSerializer()
        # TODO: what about faults?
        return opinfo
    
    def _parseinput(self, inputelem):
        '''
        parse binding.operation.input tags.
        '''
        if inputelem is None:
            return
        xns, _ = clark2tuple(inputelem[0].tag)
        pif = findextensionfactory('rsl.wsdl1.binding.operation.input', xns)
        self.input = pif(self, inputelem)
        
    def _parseoutput(self, outputelem):
        '''
        parse binding.operation.output tags.
        '''
        if outputelem is None:
            return
        xns, _ = clark2tuple(outputelem[0].tag)
        pif = findextensionfactory('rsl.wsdl1.binding.operation.output', xns)
        self.output = pif(self, outputelem)
        
    def _parsefaults(self, faultelems):
        '''
        parse binding.operation.fault tags.
        '''
        for faultelem in faultelems:
            extfaultelems = faultelem.xpath('*[local-name()="fault"]')
            if len(extfaultelems) > 0:
                xns, _ = clark2tuple(extfaultelems[0].tag)
                opf = findextensionfactory('rsl.wsdl1.binding.operation.fault',
                                           xns)
                fault = opf(self, faultelem)
                if self.faults is None:
                    self.faults = {}
                self.faults[fault.name] = fault
            else:
                warn("can not find binding/operation/fault extension element.")
    
class WSDLParamInfo(object):
    '''
    As WSDL splits its infos about operation parameters in input,
    output, header, aso..., a special IParamInfo implementation is necessary.
    '''

    implements(IParamInfo)
    
    def __init__(self, operation):
        '''
        initialise empty instance.
        '''
        self.operation = operation
        self.name = None
        self.message = None
        self.tag = None
    
    def frometree(self, inputelem): # inputelem can also be an outputelem
        '''
        parse informations about parameters in input/output tags.
        '''
        _, self.tag = clark2tuple(inputelem.tag)   
        self.name = inputelem.get('name')
        self.message = qname2clark(inputelem.get('message'), inputelem.nsmap)
        return self

class WSDLFault(object):
    '''
    A WSDL fault tag.
    '''
    
    implements(IFault)
    
    def __init__(self, operation):
        '''
        initialise empty instance.
        '''
        self.name = None
        self.message = None
        
    def frometree(self, faultelem):
        '''
        parse fault tag.
        '''
        self.name = faultelem.get('name')
        self.message = qname2clark(faultelem.get('message'), faultelem.nsmap)
        return self
