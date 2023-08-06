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
this module implements all de/serialisers defied in WSDL 1 for mime encoding.
'''
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.generator import Generator
from email import message_from_file
from StringIO import StringIO

from lxml import etree
from zope.interface import classProvides

from rsl.globalregistry import lookupimpl
from rsl.interfaces import ISerializer, IDeserializer
from rsl.xsd.interfaces import IXMLDeserializer, IXMLSerializer

def splitmime(mimetype):
    '''
    split a mime type name into two parts.
    e.g.: text/xml => (text, xml)
    '''
    if mimetype is None:
        return None, None
    mtsplit = mimetype.split('/')
    if len(mtsplit) == 1:
        if mtsplit[0] in ('', '*'):
            return None, None # no major defined
        else:
            return mtsplit[0], None
    if mtsplit[0] in ('', '*'):
        if mtsplit[1] in ('', '*'):
            return None, None
        else:
            return None, mtsplit[1]
    if mtsplit[1] in ('', '*'):
        return mtsplit[0], None
    return mtsplit[0], mtsplit[1]

# some predefined majore mime types and their classes.
mimeclsmap = {'text': MIMEText,
              'application': MIMEApplication,
              'audio': MIMEAudio,
              'image': MIMEImage}
        
def getmimeclass(mimetype):
    '''
    helper function to resolve class in mimclsmap for mimetype.
    '''
    major, minor = splitmime(mimetype)
    cls = mimeclsmap.get(major.lower(), None)
    return major, minor, cls
     
# 'mime:content'
class MimeContentSerializer(object):
    '''
    implement mime:content en/decoding rules.
    '''
    
    classProvides(ISerializer, IDeserializer)
    
    @classmethod
    def serialize(cls, params, operationinfo, **kw):
        '''
        params    ... dict of values to serialise
        operationinfo ... IOperationInfo instance
        mimeobj   ... if this is set and true, then return created MIMEBase instance
        '''
        # only one part allowd here...
        # part['type'] ... mime-type
        # part['mimetype'] ... mime-type
        # part['name'] ... name of part in params dict
        # only one part allowed here or no part for empty messages
        if len(operationinfo.input) > 0:
            pinfo = operationinfo.input[0]
        else: 
            # if we don't serialize anything, then we have no content-type?
            return {}, '' 
        value = params[pinfo.name]
        if pinfo.type:
            value = operationinfo.typesystem.getType(pinfo.type).encode(value) # what about complex types? should not happen here
        if pinfo.serializer == 'application/x-www-form-urlencoded':
            msg = MIMENonMultipart('application', 'x-www-form-urlencoded')
            serialiser = lookupimpl(ISerializer, 'urlEncoded')
            _, value = serialiser.serialize(params, operationinfo)
            msg.set_payload(value)
        else:
            major, minor, cls = getmimeclass(pinfo.serializer)
            if cls is None:
                msg = MIMENonMultipart(major, minor)
                msg.set_payload(value)
            else:
                msg = cls(value, minor)
        if kw.get('mimeobj', False):
            return msg
        outstr = StringIO()
        mimegenerator = Generator(outstr)
        mimegenerator._dispatch(msg) # not that nice to use private methods, but there is no separate content/header method
        return dict(msg), outstr.getvalue()
    
    @classmethod
    def deserialize(cls, data, operationinfo, **kw):
        '''
        extracts parameter names and values from mime-encoded data.
        '''
        # this must be some text/xml or whatever namespace.
        # 1. check for mime-type:
        #     which one to use?, the one in kw['headers'] or the one from partsinfo
        # only one part allowed here
        pinfo = operationinfo.output[0]
        deserializer = lookupimpl(IDeserializer, pinfo.serializer)
        if deserializer is not None:
            return deserializer.deserialize(data, operationinfo, **kw) 
        else:
            # ok... nothing to do, return what we have
            return kw['headers'], data
    
# 'mime:mimeXml'
class MimeXmlSerializer(object):
    '''
    implement mime:mimeXml en/decoding rules.
    '''
    
    classProvides(ISerializer, IDeserializer)
    
    @classmethod
    def serialize(cls, params, operationinfo, **kw):
        '''
        params    ... dict of values to serialise
        operationinfo ... IOperationInfo instance
        mimeobj   ... if this is set and true, then return created MIMEBase instance
        '''
        # only one part allowed here
        pinfo = operationinfo.input[0]
        value = params[pinfo.name]
        serializer = lookupimpl(IXMLSerializer, pinfo.serializer)
        _, encvalue = serializer.serialize(value, pinfo.type, operationinfo.typesystem, None)
        msg = MIMEText(encvalue, 'xml')
        if kw.get('mimeobj', False):
            return msg
        outstr = StringIO()
        mimegenerator = Generator(outstr)
        mimegenerator._dispatch(msg) # not that nice to use private methods, but there is no separate content/header method
        return dict(msg), outstr.getvalue()
    
    @classmethod
    def deserialize(cls, data, operationinfo, **_):
        '''
        extracts parameter names and values from xml-encoded data.
        '''
        # this must be some text/xml for whatever namespace.
        # 1. parse xml:
        datatree = etree.fromstring(data)
        # only one part allowed here?
        pinfo = operationinfo.output[0]
        serialiser = lookupimpl(IXMLDeserializer, pinfo.serializer)
        value = serialiser.deserialize(datatree, pinfo.type, operationinfo.typesystem)
        return None, value
            
    
# 'mime:multipartRelated'
class MimeMultipartRelatedSerializer(object):
    '''
    implement mime:multipartRelated en/decoding rules.
    '''
    
    classProvides(ISerializer, IDeserializer)
    
    @classmethod
    def serialize(cls, params, operationinfo, **kw):
        '''
        params    ... dict of values to serialise
        operationinfo ... IOperationInfo
        mimeobj   ... if this is set and true, then return created MIMEBase instance
        '''
        # this is quite some overhaed but very generic :)
        # serialise each part....
        # attach all parts to mimemultipart...
        # serialise this again and return it.
        msg = MIMEMultipart('related')
        for pinfo in operationinfo.input:
            serialiser = lookupimpl((), ISerializer, pinfo.serializer)
            partval = serialiser.serialize(params, operationinfo, mimeobj=True)
            if isinstance(partval, MIMENonMultipart):
                msg.attach(partval)
            else:
                # TODO: for now assume it is a text/xml
                mnp = MIMENonMultipart(None, None)
                del mnp['Content-Type']
                if partval[0] is not None:
                    for key, value in partval[0]:
                        mnp.add_header(key, value)
                mnp.set_payload(partval[1])                    
                msg.attach(mnp)
        if kw.get('mimeobj', False):
            return msg
        outstr = StringIO()
        mimegenerator = Generator(outstr)
        mimegenerator._dispatch(msg) # not that nice to use private methods, but there is no separate content/header method
        return dict(msg), outstr.getvalue()
    
    @classmethod
    def deserialize(cls, data, operationinfo, **kw):
        '''
        extracts parameter names and values from mime-multipart-encoded data.
        '''
        # 1. rebuild multipart message
        headers = kw['headers']
        buf = StringIO()
        for k,v in headers.items():
            buf.write('%s: %s\r\n' % (k,v))
        buf.write('\r\n')
        buf.write(data)
        buf.seek(0)
        mpm = message_from_file(buf)
        value = []
        i = 0 # index into multipart message
        for pinfo in operationinfo.output:
            serialiser = lookupimpl((), IDeserializer, pinfo.serializer)
            partmsg = mpm.get_payload()[i]
            partheaders, partvalue = serialiser.deserialize(partmsg.get_payload(), operationinfo, headers=dict(partmsg))
            value.append((partheaders,partvalue))
        return None, partvalue
