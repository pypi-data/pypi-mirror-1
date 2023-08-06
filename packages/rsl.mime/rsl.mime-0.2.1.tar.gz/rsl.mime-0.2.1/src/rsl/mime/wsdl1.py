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
This module defines the WSDL mime extension elements.
'''
from zope.interface import directlyProvides

from rsl.wsdl1.interfaces import IWSDLExtensionFactory

from rsl.globalregistry import lookupimpl
from rsl.implementations import ParamInfo
from rsl.wsdl1.binding import WSDLParamInfo
from rsl.wsdl1.interfaces import IParamInfo
from rsl.misc.namespace import clark2tuple

# mime:content  part?,type?
# mime:mimeXml part?
# mime:multipartRelated
#    mime:part
#       soap:body
#       mime:content
#       mime:mimeXml
class MIMEParamInfo(WSDLParamInfo):
    '''
    extend WSDL specific I/O parameter infos with mime specific information.
    '''
    
    def __init__(self, operation):
        '''
        initialise empty instance.
        '''
        super(MIMEParamInfo, self).__init__(operation)
        self.exttag = None
        self.type = None
        self.part = None
        self.subparts = None
    
    def frometree(self, inputelem): #also used for outputelem
        '''
        parse information about I/O parameters from etree instance. 
        ''' 
        super(MIMEParamInfo, self).frometree(inputelem)
        _, self.exttag = clark2tuple(inputelem[0].tag)
        # check whether tag is mimeContent, mimeXml or multipartRelated
        if self.exttag == 'content':
            # TODO: there can be more than one content tags
            self.part = inputelem[0].get('part')
            self.type = inputelem[0].get('type')
            self.getMsgPart() # test if part exists.
        elif self.exttag == 'mimeXml':
            self.part = inputelem[0].get('part')
            self.type = 'text/xml'
        elif self.exttag == 'multipartRelated':
            self.type = 'multipart/related'
            for partelem in inputelem[0]:
                # parse mime:part elements
                childns, _ = clark2tuple(partelem[0])
                pif = lookupimpl(IParamInfo, childns)
                subpif = pif(self.operation).frometree(partelem) # maybe it's not nice to pass something different than wsdl:input/output/fault to this factory
                if self.subparts is None:
                    self.subparts = []
                self.subparts.append(subpif)
        return self
    
    def getSerializer(self):
        '''
        return name of serializer for WSDL-mime
        '''
        if self.exttag == 'content' and self.type=='application/x-www-form-urlencoded':
            return self.type
        return 'mime:' + self.exttag
    
    def getMsgPart(self):
        '''
        helper method to find all related and valid msgParts.
        '''
        # for http binding there can only be urlEncoded or urlReplacement and all parts for a
        # message are used.
        porttype = self.operation.binding.wsdl.porttypes[self.operation.binding.porttype]
        porttypeoperation = porttype[self.operation.name]
        message = self.operation.binding.wsdl.messages[porttypeoperation[self.tag]['message']]
        if self.part is not None:
            for p in message:
                if p['name'] == self.part:
                    return p
        else:
            if len(message) > 1:
                #warn('Illegal mime binding. specify part attribute or make sure there is only one part in the message.')
                raise ValueError('Illegal mime binding. specify part attribute or make sure there is only one part in the message.')
            elif len(message) > 0:
                return message[0] # assume there is only one part
            else:
                return None # empty message is possible
        raise ValueError('Invalid WSDL file. Can not find msg. part %s.' % self.part)

    def getParamInfo(self):
        '''
        return IParamInfo instance filled with information from this instance.
        '''
        pinfos = []
        if self.exttag == 'multipartRelated':
            for subpart in self.subparts:
                pinfos.extend(subpart.getParamInfo())
        else:
            msgpart = self.getMsgPart()
            if msgpart is not None:
                pinfo = ParamInfo()
                pinfo.name = msgpart['name']
                if self.type == 'text/xml':
                    pinfo.serializer = 'xml'
                    if 'type' in msgpart:
                        pinfo.type = msgpart['type']
                        pinfo.serializer = pinfo.serializer + ':type'
                    elif 'element' in msgpart:
                        pinfo.type = msgpart['element']
                        pinfo.serializer = pinfo.serializer + ':element'
                else:
                    pinfo.type = msgpart['type']
                pinfos.append(pinfo)
        return pinfos

def mimeparaminfofactory(operation, inputelem):
    '''
    Factory for MIMEParamInfo instances.
    '''
    paraminfo = MIMEParamInfo(operation)
    paraminfo = paraminfo.frometree(inputelem)
    return paraminfo
directlyProvides(mimeparaminfofactory, IWSDLExtensionFactory)
