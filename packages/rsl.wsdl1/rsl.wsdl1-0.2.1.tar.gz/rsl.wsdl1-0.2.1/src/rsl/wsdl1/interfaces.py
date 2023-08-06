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
Define interfaces for various elements of a WSDL document.

The frometree method always takes the wsdl-scoped element.

To initialise an extension in a fromtree method, the extension should first 
initialise itself, and then call the fromtree method of the superclass to 
ensure, that all necessary properties are available for further initalisation.
'''
from zope.interface import Interface

class IWSDLExtensionFactory(Interface):
    '''
    A generic factory interface for WSDL-Extensions.
    '''
    
    def __call__(parent, etree):
        '''
        create WSDL extension instance from etree and return
        the newly created instance.
        '''
        
class IPort(Interface):
    '''
    A WSDL port element
    '''
    
    def frometree(etree):
        '''
        init port instance from etree and return
        self or IPort instance.
        '''

class IBinding(Interface):
    '''
    A WSDL Binding element.
    '''
    
    def frometree(etree):
        '''
        init binding instance from etree and return 
        self or IBinding Instance
        '''
        
class IOperation(Interface):
    '''
    A binding operation
    '''
    
    def frometree(etree):
        '''
        init operationf instance from etree and return 
        self or IOperation Instance
        '''
        
    def getOperationInfo():
        '''
        return rsl.interfaces.IOperationInfo instances
        '''
        
class IParamInfo(Interface):
    '''
    Parameter infos for binding operations
    '''
    
    def frometree(etree):
        '''
        init IParamInfo instance from etree and return 
        self or IParamInfo Instance
        '''
        
    def getSerializer():
        '''
        return name of 'operation' - serializer to use.
        this is necessary to know, whether an envelope must be used or not.
        '''
        
    def getParamInfo():
        ''' 
        return list of rsl.interfaces.IParamInfo instances
        '''

class IFault(Interface):
    '''
    Fault infos for binding operations
    '''
    
    def frometree(etree):
        '''
        init IFault instance from etree and return 
        self or IFault Instance
        '''
