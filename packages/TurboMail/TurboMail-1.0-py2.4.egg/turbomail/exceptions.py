# encoding: utf-8


__all__ = ['MailException', 'MailNotEnabledException', 'MailConfigurationException']


class MailException(Exception):
    pass

        
class MailNotEnabledException(MailException):
    def __str__(self):
        return "An attempt was made to use a facility of the Turbo-Mail " \
               "framework but outbound mail hasn't been enabled in the" \
               "config file [via mail.on]."
    
    
class MailConfigurationException(MailException):
    args = ()
    def __init__(self, message):
        self.message= message
        
    def __str__(self):
        return self.message
