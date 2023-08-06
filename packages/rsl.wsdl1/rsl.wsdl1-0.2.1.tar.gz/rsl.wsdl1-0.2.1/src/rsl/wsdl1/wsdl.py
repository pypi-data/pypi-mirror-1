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
This module provides an IServiceDescription for WSDL 1 to use with rsl.
'''
from urlparse import urljoin
from urllib2 import urlopen
from warnings import warn

from pkg_resources import working_set
from lxml import etree
from zope.interface import implements

from rsl.globalregistry import lookupimpl
from rsl.interfaces import ISchema
from rsl.xsd.manager import GLOBALSCHEMAMANAGER, XMLSchemaManager
from rsl.misc.namespace import clark, clark2tuple, qname2clark
from rsl.wsdl.interfaces import IWSDL
from rsl.wsdl1.namespace import NS_WSDL
from rsl.interfaces import  IProxyFactory

def findextensionfactories(category, name):
    '''
    search WSDL extensions with the help of setuptools.
    
    category:
        rsl.wsdl1.porttype.operation.inout:parse
        rsl.wsdl1.porttype.operation.fault:parse
    
    yields: functions to parse extensions
    '''
    for ept in working_set.iter_entry_points(category, name):
        ret = ept.load()
        yield ret
    
def findextensionfactory(category, name):
    '''
    search a WSDL extension with the help of setuptools.
    
    category:
        rsl.wsdl1.service.port
        rsl.wsdl1.binding
        rsl.wsdl1.binding.operation
        rsl.wsdl1.binding.operation.input
        rsl.wsdl1.binding.operation.output
        rsl.wsdl1.binding.operation.fault
                
    name: namespace to search for
    
    returns: class or other object which implements IExtensionFactory
    '''
    for ept in working_set.iter_entry_points(category, name):
        ret = ept.load()
        return ret

class WSDL(object):
    '''
    A class which knows how to handle WSDL 1 descriptions.
    '''
    
    implements(IWSDL)
    
    descname = NS_WSDL
    
    def __init__(self, url=None):
        '''
        initialise this instance with empty values.
        '''
        self.name = None
        self.targetnamespace = None
        self.documentation = None
        self.url = url
        self.types = XMLSchemaManager(GLOBALSCHEMAMANAGER)
        self.messages = {}
        self.porttypes = {}
        self.bindings = {}
        self.services = {}
        
    def fromURL(self, url, **kws):
        '''
        load a wsdl file from url and parse it in.
        '''
        self.url = url
        fobj = urlopen(url)
        data = fobj.read()
        fobj.close()
        root = etree.fromstring(data)
        self.frometree(root)

    def frometree(self, wsdlelem):
        '''
        parse a wsdl given as etree.
        '''
        self.targetnamespace = wsdlelem.get("targetNamespace")
        self.name = wsdlelem.get("name")
        self._parseimports(wsdlelem.findall(clark(NS_WSDL, 'import')))
        self._parsetypes(wsdlelem.find(clark(NS_WSDL, 'types')))
        self._parsemessages(wsdlelem.findall(clark(NS_WSDL, 'message')))
        self._parseporttypes(wsdlelem.findall(clark(NS_WSDL, 'portType')))
        # here we have the complete interface description
        # now start with protocol specific things
        self._parsebindings(wsdlelem.findall(clark(NS_WSDL, 'binding')))
        self._parseservices(wsdlelem.findall(clark(NS_WSDL, 'service')))
        return self
    
    def getProxy(self, namespace=None, name=None, portname=None, **_):
        '''
        This is the factory method for proxy objects. WSDL has all the infos 
        to create a proxy.
        '''
        portlist = self._getportlist(namespace, name, portname)
        # we got a portlist...
        # go through list and return first not None proxy.
        for port in portlist:
            proxyf = lookupimpl(IProxyFactory, port[3].namespace)
            if proxyf is not None:
                proxy = proxyf(port[3].location, name=port[3].name)
                if port[3].binding in self.bindings:
                    ops = self.bindings[port[3].binding].operations
                    for operation in ops.values():
                        proxy.addOperation(operation.name, 
                                           operation.getOperationInfo())
                    return proxy
        return None

    def _parseimports(self, importelems):
        '''
        parse all import tags in WSDL

        @param wsdl: an etree containing the wsdl
        @type wsdl: L{etree}
        '''
        for importelem in importelems:
            oldname = self.name
            oldtargetnamespace = self.targetnamespace
            oldurl = self.url
            #namespace = importelem.get("namespace")
            location = importelem.get("location")
            location = urljoin(oldurl, location)
            fobj = urlopen(location)
            importstr = fobj.read()
            fobj.close()
            # TODO: check new and old namespace before importing
            self.url = location
            tree = etree.fromstring(importstr)
            xns, _ = clark2tuple(tree.tag)
            if xns == NS_WSDL:
                self.frometree(tree)
            else:
                # TODO: maybe support other schemata types
                fac = lookupimpl(ISchema, xns)
                schema = fac(uri=self.url).frometree(tree)
                self.types.addSchema(schema)
            self.name = oldname
            self.targetnamespace = oldtargetnamespace
            self.url = oldurl
    
    def _parsetypes(self, typeselem):
        '''
        parse all types definitions
        
        @param wsdl: an etree containing the wsdl
        @type wsdl: L{etree}
        
        @todo: support other type definitions than XMLSchema
        '''
        if typeselem is None:
            return
        for child in typeselem.iterchildren(tag=etree.Element):
            childns, _ = clark2tuple(child.tag)
            #print "Get Schema factory for:", childns
            fac = lookupimpl(ISchema, childns)
            schema = fac(self.types, uri=self.url).frometree(child)
            self.types.addSchema(schema)
            
    def _parsemessages(self, msgelems):
        ''' 
        parse all message definitions
        message elements are stored in the self.message dictionary
        message name is the key entry and is in clark notation
        the value is a list of parts which are a dictionary containing name and element or type
        
        @param wsdl: an etree containing the wsdl
        @type wsdl: L{etree}
        
        '''
        for msg in msgelems:
            parts = []
            for msgpart in msg.findall(clark(NS_WSDL, 'part')):
                part = {}
                part['name'] = msgpart.get('name')
                if "element" in msgpart.attrib:
                    part["element"] = qname2clark(msgpart.get("element"), 
                                                  msgpart.nsmap)
                if "type" in msgpart.attrib:
                    part["type"] = qname2clark(msgpart.get("type"), 
                                               msgpart.nsmap)
                parts.append(part)
            self.messages[clark(self.targetnamespace, msg.get('name'))] = parts
            
    def _parseporttypes(self, porttypelems):
        '''
        read in all portTypes.
        a porttype  has a set of operations which refer to messages.
        a porttype has a name which will be stored in clark notation as dict key
        
        @param wsdl: an etree containing the wsdl
        @type wsdl: L{etree}
        '''
        for porttypeelem in porttypelems:
            operations = {}
            for opelem in porttypeelem.findall(clark(NS_WSDL, 'operation')):
                # TODO: message exchange pattern is defined by order of sub 
                #       elements
                operation = {}
                for msgelem in opelem:
                    # namespace must be NS_WSDL
                    _, msgtype = clark2tuple(msgelem.tag) 
                    # TODO: wsdl defines some defaults for input/output names
                    #       append Request/Solicit and Response to operation 
                    #       name depending on message exchange pattern 
                    #       ( faults must have names)
                    msgname = msgelem.get("name")
                    msgref = qname2clark(msgelem.get("message"), msgelem.nsmap)
                    if msgtype == 'fault':
                        if 'fault' not in operation:
                            # the order of fault elements is not significant
                            operation['fault'] = {} 
                        operation['fault'][msgname] = {'name': msgname, 
                                                       'message': msgref}
                        # parse wsaw:action attribute
                        for parsefunc in findextensionfactories('rsl.wsdl1.porttype.operation.fault', 'parse'):
                            parsefunc(operation['fault'][msgname], msgelem)
                    else:
                        operation[msgtype] = {'name': msgname, 
                                              'message': msgref}
                        # parse wsaw:action attribute
                        for parsefunc in findextensionfactories('rsl.wsdl1.porttype.operation.inout', 'parse'):
                            parsefunc(operation[msgtype], msgelem)
                operations[opelem.get("name")] = operation
            self.porttypes[clark(self.targetnamespace, 
                                 porttypeelem.get("name"))] = operations
            
    def _parsebindings(self, bindingelems):
        '''
        parse protocol specific binding elements.
        '''
        for bindingelem in bindingelems:
            # go through all alle childelements. if namespace is not WSDL then
            # try to find a bindingfactory.
            extbindingelems = bindingelem.xpath('*[namespace-uri() != "%s"]' % 
                                                NS_WSDL)
            if len(extbindingelems) > 0:
                binding = None
                bindingfound = False # TODO: I don't like this hack
                for extbindingelem in extbindingelems:
                    bindns, _ = clark2tuple(extbindingelem.tag)
                    bfac = findextensionfactory('rsl.wsdl1.binding', bindns)
                    try:
                        if bfac is not None:
                            bindingfound = True
                            binding = bfac(self, bindingelem)
                            self.bindings[clark(self.targetnamespace, 
                                                binding.name)] = binding
                    except Exception, exc:
                        warn('Can not create Binding for "%s": %s' % 
                             (bindns, repr(exc)))
                if binding is not None:
                    # if we have a binding let's look for other extensions 
                    # like wsaw, and wsp
                    for parsefunc in findextensionfactories('rsl.wsdl1.binding',
                                                            'parse'):
                        parsefunc(binding, bindingelem)
                elif not bindingfound: 
                    warn('No BindingFactory for "%s" found.' % bindns)
            else:
                warn('No extension element for binding found.')
                
    def _parseservices(self, serviceelems):
        '''
        parse wsdl service elements.
        '''
        for serviceelem in serviceelems:
            service = {}
            service['name'] = serviceelem.get('name')
            service['ports'] = {}
            self.services[clark(self.targetnamespace, 
                                serviceelem.get("name"))] = service
            for portelem in serviceelem.findall(clark(NS_WSDL, "port")):
                extportelems = portelem.xpath('*[namespace-uri() != "%s"]' % 
                                              NS_WSDL)
                if len(extportelems) > 0:
                    port = None
                    for extportelem in extportelems:
                        portns, _ = clark2tuple(extportelem.tag)
                        pfac = findextensionfactory('rsl.wsdl1.service.port', 
                                                    portns)
                        if pfac is not None:
                            port = pfac(self, portelem)
                            service['ports'][port.name] = port
                    if port is not None:
                        # if we have a port let's look for further extensions 
                        # like wsaw and wsp
                        for parsefunc in findextensionfactories('rsl.wsdl1.service.port', 'parse'):
                            parsefunc(port, portelem)
                    else:
                        warn('No PortFactory for "%s" found.' % portns)
                else:
                    warn('No extension element for port found.')
                    
    def _getportlist(self, namespace=None, servicename=None, portname=None):
        '''
        Get a list of ports filtered with given parameters. If more than
        one parameter is not None, then the criterias are connected with 
        'and'.
        '''
        portlist = []
        for qsn, svc in self.services.items(): 
            # qsn ... qualified service name
            _, lsn = clark2tuple(qsn)
            for pname, pval in svc['ports'].items():
                portlist.append((lsn, pname, pval.namespace, pval))
        if portname is not None:
            portlist = [p for p in portlist if p[1] == portname]
        if servicename is not None:
            portlist = [p for p in portlist if p[0] == servicename]
        if namespace is not None:
            portlist = [p for p in portlist if p[2] == namespace]
        if len(portlist) > 0:
            return portlist
        return []

    def getServices(self):
        '''
        return list of known services of this WSDL.
        '''
        return [{'portname': port[1], 'name':port[0], 'namespace':port[2]} 
                for port in self._getportlist()] 
