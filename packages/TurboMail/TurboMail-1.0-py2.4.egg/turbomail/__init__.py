# encoding: utf-8

import logging
log = logging.getLogger("turbomail")

from turbomail.startup import start_extension, shutdown_extension
from turbomail.exceptions import *
from turbomail.message import Message, TemplateMessage


__all__ = ['MailException', 'MailNotEnabledException', 'MailConfigurationException', 'Message', 'TemplateMessage', 'enqueue']


queue = None
enqueue = None
