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
this module provides an IServiceDescription implementation for SMD 0.1
'''
from urllib2 import urlopen
from urlparse import urljoin

from zope.interface import implements

from rsl.globalregistry import lookupimpl
from rsl.interfaces import IProxyFactory
from rsl.implementations import OperationInfo, ParamInfo
from rsl.smd01.interfaces import ISMD

from simplejson import loads

def loadSMD(url):
    '''
    return an IServiceDescription instance for the given url.
    this method tries to find a suitable SMD implementation for
    the required SMD-Version.
    '''
    fobj = urlopen(url)
    data = fobj.read()
    fobj.close()
    smddoc = loads(data)
    if 'SMDVersion' in smddoc:
        smdfactoryname = 'SMD-' + smddoc['SMDVersion']
    else:
        smdfactoryname = 'SMD-.1'
    smdfac = lookupimpl(ISMD, smdfactoryname)
    smd = smdfac()
    smd.fromDict(smddoc)
    return smd
    

class SMD01(object):
    '''
    SMD 0.1 implementation
    '''
    
    implements(ISMD)
    
    descname = 'SMD-.1'
    
    def __init__(self):
        '''
        create SMD01 instance.
        '''
        super(SMD01, self).__init__()
        self.url = None
        self.serviceType = None
        self.methods = None
        self.objectName = None
        self.version = None
        self.serviceURL = None

    def fromURL(self, url, **kws):
        '''
        initialise this instance with data read from url.
        '''
        self.url = url
        fobj = urlopen(url)
        data = fobj.read()
        fobj.close()
        self.fromString(data)
        
    def fromString(self, smdstr):
        '''
        initialise this instance with an SMD document given in a string.
        '''
        #TODO: here we could use IDeserializer for JSON
        smddoc = loads(smdstr)
        self.fromDict(smddoc)
        
    def fromDict(self, smddoc):
        '''
        initialise this instance from a dictionary most likely, this 
        dictionary is a parsed SMD document.
        '''
        self.version = smddoc.get('SMDVersion', '.1') # can't be different
        self.objectName = smddoc.get('objectName', None) # service name
        self.serviceType = smddoc['serviceType'] # "JSON-RPC", "JSON-P"...
        self.serviceURL = smddoc.get('serviceURL', None) # rel or abs url
        # make serviceurl absolute
        if self.url is None:
            self.serviceURL = urljoin('', self.serviceURL)
        else:
            self.serviceURL = urljoin(self.url, self.serviceURL)
        self.methods = smddoc['methods']
        
    def getProxy(self, **_):
        '''
        create a proxy instance from this description.
        '''
        proxyfac = lookupimpl((), IProxyFactory, self.serviceType)
        proxy = proxyfac(self.serviceURL)
        for method in self.methods:
            # convert method to IOperationInfo
            opinfo = OperationInfo()
            opinfo.name = method['name']
            opinfo.serializer = self.serviceType
            opinfo.location = method.get('serviceURL', None)
            opinfo.input = []
            for param in method['parameters']:
                pinfo = ParamInfo()
                pinfo.name = param['name']
                pinfo.type = param.get('type', None)
                opinfo.input.append(pinfo)
            proxy.addOperation(method['name'], opinfo)
        return proxy
    
    def getServices(self):
        '''
        return all service names described in this SMD document.
        '''
        return [{'name': self.objectName}]
