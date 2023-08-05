#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2007 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
#
# This code is placed under the MIT license:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

import email
import logging
import time
import unittest

logging.disable(logging.ERROR)

import turbogears
import turbomail

from tests.lib.smtp_mailsink import SMTPMailsink
from tests.lib.utils import get_received_mail, save_config


class TestErrorHandling(unittest.TestCase):
	"Test cases for error conditions and error handling inside of TurboMail."

	def setUp(self):
		self.server_port = 42042
		test_config = {'mail.on': True, 'mail.timeout': 1,
						'mail.polling': True,
						'mail.server': 'localhost:%d' % self.server_port}
		self._original_config = save_config(test_config.keys())
		turbogears.config.update(test_config)
		self.sink = None
		turbogears.startup.startTurboGears()


	def tearDown(self):
		turbogears.startup.stopTurboGears()
		turbogears.config.update(self._original_config)
		if self.sink != None:
			self.sink.stop()


	def test_connection_refused(self):
		"""Test that a message is not lost if the mail hub was unavailable for
		a short period of time."""
		message = turbomail.Message('sender@foo.example',
									'recipient@foo.example', 'foo bar')
		message.plain = 'Hello World!'
		turbomail.enqueue(message)
		time.sleep(1)
		self.sink = SMTPMailsink(host='localhost', port=self.server_port)
		self.sink.start()
		msginfo = get_received_mail(self.sink)
		msg = email.message_from_string(msginfo['mail'])
		assert 'Hello World' in msg.get_payload() 

