# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from email.Charset import Charset
from email.MIMEText import MIMEText as OriginalMIMEText
from email.MIMENonMultipart import MIMENonMultipart

class MTText(OriginalMIMEText):

    def __init__(self, _text, _subtype='plain', _charset='us-ascii'):
        if not isinstance(_charset,Charset):
            _charset = Charset(_charset)
        if isinstance(_text,unicode):
            _text = _text.encode(_charset.input_charset)
        MIMENonMultipart.__init__(self, 'text', _subtype,
                                  **{'charset': _charset.input_charset})
        self.set_payload(_text, _charset)

