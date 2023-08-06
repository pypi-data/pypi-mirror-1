# encoding: utf-8

"""TurboMail UTF-8 quoted-printable encoding extension."""


import logging

import codecs
from encodings.utf_8 import StreamReader, StreamWriter

from turbomail.api import Extension
from turbomail.compat import charset


__all__ = ['interface', 'UTF8QuotedPrintable']

log = logging.getLogger("turbomail.extension.utf8qp")



try:
    from encodings.utf_8 import encode, decode
except ImportError:
    # Python 2.3 does not have encode/decode in that module
    from encodings.utf_8 import Codec
    encode = Codec.encode
    decode = Codec.decode


class UTF8QuotedPrintable(Extension):
    name = 'utf8qp'
    
    def register():
        """Add 'utf8qp' as a special codec to the email module which uses UTF-8
        quoted printable as encoding in email. To do this, a fake codec 'utf8qp'
        needs to be registered in Python's codec system as well (it behaves exactly
        like the built-in UTF-8 codec)."""
        
        if 'uft8qp' not in charset.CHARSETS:
            def is_utf8qp(codec_name):
                if codec_name in ('utf8qp', 'utf-8-qp'):
                    return (encode, decode, StreamReader, StreamWriter)
                return None
            
            codecs.register(is_utf8qp)
            charset.add_charset('utf8qp', charset.SHORTEST, charset.QP, 'utf-8')
            # If we don't register the alias, the email module will set 'utf-8-qp'
            # as encoding in the generated mail - however this is not a valid 
            # encoding so most mail clients will not be able to display the contents
            # correctly.
            charset.add_alias('utf-8-qp', 'utf8qp')
    
    register = staticmethod(register)
    
    def start(self):
        super(UTF8QuotedPrintable, self).start()
        
        log.info("Configuring UTF-8 character set to use Quoted-Printable encoding.")
        charset.add_charset('utf-8', charset.SHORTEST, charset.QP, 'utf-8')
    
    def stop(self):
        super(UTF8QuotedPrintable, self).stop()
        
        log.info("Configuring UTF-8 character set to use Base-64 encoding.")
        charset.add_charset('utf-8', charset.SHORTEST, charset.BASE64, 'utf-8')


interface = UTF8QuotedPrintable()
