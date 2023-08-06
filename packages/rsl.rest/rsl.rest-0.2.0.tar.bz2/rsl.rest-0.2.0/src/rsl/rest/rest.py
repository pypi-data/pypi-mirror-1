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
this module provides IServiceDescription and IProxy implementations for ReST
ful web servics for rsl.
'''
from urlparse import urlunsplit, urlsplit
from os.path import basename
import cgi
from urllib import urlencode

from zope.interface import implements

from rsl.globalregistry import lookupimpl
from rsl.interfaces import IServiceDescription, ITransport, IProxy
from rsl.implementations import OperationInfo


def loadHTTPGET(url):
    """
    returns a Description object for a ReST-ful Web Service.
    The url is used as an example request and param and methd names
    are extracted from this url.
    
    @param url: The example url.
    @type url: C{string}
    
    @return: Returns a Description object from the given url.
    @rtype: L{RESTDescr}    
    """
    rsd = RESTDescr()
    rsd.fromURL(url)
    return rsd


class RESTDescr(object):
    ''' 
    The IServiceDescription implementation for ReST-ful Web Services.
    This class also implements the IProxy interface.
    '''
    
    implements(IServiceDescription, IProxy)
    
    descname = 'httpurl'
    ptype = 'httpget'
    
    def __init__(self, location=None):
        '''
        create an instance and empty all instance variables.
        '''
        self.url = location
        self.callables = {}

    def fromURL(self, url, **kws):
        '''
        initialise this instance. parse the url and try to identify
        methodname and parameter names.
        '''
        self.url = url
        pdu = urlsplit(self.url)
        params = cgi.parse_qs(pdu.query, True, False)
        opinfo = OperationInfo()
        opinfo.name = basename(pdu.path)
        opinfo.location = urlunsplit((pdu[0], pdu[1], pdu[2], '', ''))
        opinfo.input = params.keys()
        self.addOperation(opinfo.name, opinfo)
        
    def getProxy(self, **_):
        '''
        return self as IProxy implementation.
        '''
        return self
    
    def getServices(self):
        '''
        return all service names described by this IServiceDescription.
        '''
        return [{'name': self.url}]
    
    def callRemote(self, name, *args, **kws):
        '''
        invoke a remote method offered by this IProxy.
        '''
        self.__getattr__(name)(*args, **kws)
        
    def addOperation(self, name, operationinfo):
        '''
        add the signature of a remote method.
        '''
        self.callables[name] = Callable(operationinfo.location, 
                                        name, operationinfo.input)

    def __getattr__(self, name):
        '''
        make remote methods accessible as normal python method.
        '''
        cbl = self.callables.get(name, None)
        if cbl is not None:
            return cbl

class Callable(object):
    '''
    Callable instances are used by ReST proxy instances to provide python 
    methods which actually execute the remote method.
    '''
    
    def __init__(self, url, name, params):
        '''
        initialise this callable with all necessary information.
        '''
        pdu = urlsplit(url)
        self.purl = (pdu[0], pdu[1], pdu[2])
        self.name = name
        self.paramnames = params
    
    def __call__(self, **kwargs):
        '''
        invoke the remote method.
        '''
        target = urlunsplit((self.purl[0], self.purl[1], self.purl[2], 
                             urlencode(kwargs),''))
        transport = lookupimpl(ITransport, self.purl[0])
        headers, data =  transport.send(target, None)
        print headers['content-type']
        return data
