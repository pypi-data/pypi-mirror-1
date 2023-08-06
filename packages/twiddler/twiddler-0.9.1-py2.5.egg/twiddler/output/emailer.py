# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from email.Charset import Charset,QP
from email.MIMEMultipart import MIMEMultipart
from email.Utils import make_msgid, formatdate 
from new import classobj
from smtplib import SMTP
from twiddler.interfaces import IOutput
from twiddler.output.default import _render
from twiddler.output.MTMultipart import MTMultipart
from twiddler.output.MTText import MTText
from zope.interface import implements

# default character set that uses Quoted Printable
default_charset = Charset('utf-8')
default_charset.body_encoding = QP

# dummy SMTP class for debugging or testing
class DummySMTP:

    def __init__(self,*args):
        pass

    def sendmail(self,mfrom,mto,msgstr):
        print 'Dummy SMTP send from %r to %r' % (mfrom,mto)
        print msgstr

    def quit(self):
        pass
    
class Email:

    implements(IOutput)

    def __init__(self,
                 smtp_host='localhost',
                 smtp_port='25',
                 mfrom=None,
                 mto=None,
                 mcc=None,
                 mbcc=None,
                 subject=None,
                 content_type='text/plain',
                 charset=default_charset,
                 headers=None):
        self.charset = charset
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.mfrom = mfrom
        self.mto = mto
        self.mcc = mcc
        self.mbcc = mbcc
        self.subject = subject
        self.content_type = content_type
        self.headers = headers or {}

    def _process(self,root,kw):
        # sort out what charset we're going to use
        charset = kw.get('charset',self.charset)
        content_type = kw.get('content_type',self.content_type)
        output = []
        _render(output, root._root, {})
        text = u''.join(output)
        # now turn the result into a MTText object
        msg = MTText(text.replace('\r',''),
                     content_type.split('/')[1],
                     charset)
        # sort out what headers and addresses we're going to use
        headers = {}
        values = {}
        # add date and message-id headers
        # we do this early so that they can be overriden later if desired
        headers['Date']=formatdate()
        headers['Message-ID']=make_msgid()
        # headers from ourself
        headers.update(self.headers)
        # headers from the headers parameter
        headers_param = kw.get('headers',{})
        headers.update(headers_param)
        # values and some specific headers
        for key,header in (('mfrom','From'),
                           ('mto','To'),
                           ('mcc','Cc'),
                           ('mbcc','Bcc'),
                           ('subject','Subject')):
            value = kw.get(key,
                           headers_param.get(header,
                                             getattr(self,
                                                     key) or headers.get(header)))
            if value is not None:
                values[key]=value
                # turn some sequences in coma-seperated strings
                if isinstance(value,tuple) or isinstance(value,list):
                    value = u', '.join(value)
                headers[header]=value
        # check required values have been supplied
        errors = []
        for param in ('mfrom','mto','subject'):
            if not values.get(param):
                errors.append(param)
        if errors:
            raise TypeError(
                'The following parameters were required by not specified: '+(
                ', '.join(errors)
                ))
        # turn headers into an ordered list for predictable header order
        keys = headers.keys()
        keys.sort()
        return msg,values,[(key,headers[key]) for key in keys]
        
    def _send(self,mfrom,mto,msg):
        # allow passing of DummySMTP as smtp_host
        if isinstance(self.smtp_host,classobj):
            klass = self.smtp_host
        else:
            klass = SMTP
        server = klass(self.smtp_host,self.smtp_port)
        server.sendmail(mfrom,mto,msg.as_string())
        server.quit()

    def __call__(self,root,*args,**kw):        
        if kw.get('as_message'):
            # build multipart
            msg,values,headers = self._process(root,kw)
    
            multipart_kw = {}
            subtype = kw.get('subtype')
            if subtype:
                multipart_kw['_subtype'] = subtype
            boundary = kw.get('boundary')
            if boundary:
                multipart_kw['boundary'] = boundary
                
            multipart = MTMultipart(self,
                                    values['mfrom'],
                                    values['mto'],
                                    **multipart_kw)
    
            # set the charset for the container
            multipart.set_charset(msg.get_charset())
            
            for header,value in headers:
                multipart[header]=value
                
            multipart.attach(msg)

            # return the multipart message
            return multipart

        else:
            
            # build single message
            msg,values,headers = self._process(root,kw)

            for header,value in headers:
                msg[header]=value
            # send it 
            self._send(values['mfrom'],values['mto'],msg)
