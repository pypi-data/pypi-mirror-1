# Copyright (c) 2005-2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from mimetypes import guess_type

def stripName(filename):
    return filename[max(filename.rfind('/'),
                        filename.rfind('\\'),
                        filename.rfind(':'),
                        )+1:]
    
class MTMultipart(MIMEMultipart):

    def __init__(self,smtp,mfrom,mto,_subtype='mixed',boundary=None):
        MIMEMultipart.__init__(self,_subtype,boundary)
        self.mfrom = mfrom
        self.mto = mto
        self.smtp = smtp

    def send(self):
        "send ourselves using our MailTemplate's send method"
        return self.smtp._send(self.mfrom,self.mto,self)

    def add_file(self,theFile=None,data=None,filename=None,content_type=None):
        "add a file to ourselves as an attachment"
        
        if theFile and data:
            raise TypeError(
                'A file-like object was passed as well as data to create a file'
                )
        if (data or filename) and not (data and filename):
            raise TypeError(
                'Both data and filename must be specified'
                )
        if data:
            # nothing to do
            pass
## Zope 2 only
##         elif isinstance(theFile,File):
##             filename = theFile.getId()
##             data = str(theFile.data)
##         elif isinstance(theFile,FileUpload):
##             filename = cookId(theFile.filename)
##             data=theFile.read()
##             headers=theFile.headers
##             if content_type is None:
##                 if headers.has_key('content-type'):
##                     content_type=headers['content-type']
        elif isinstance(theFile,file):
            filename = stripName(theFile.name)
            data = theFile.read()
        else:
            raise TypeError('Unknown object type found: %r' % theFile)

        content_type = content_type or guess_type(filename)[0]
        
        msg = MIMEBase(*content_type.split('/'))
        msg.set_payload(data)
        Encoders.encode_base64(msg)
        msg.add_header('Content-Disposition', 'attachment',
                       filename=filename)
        self.attach(msg)
