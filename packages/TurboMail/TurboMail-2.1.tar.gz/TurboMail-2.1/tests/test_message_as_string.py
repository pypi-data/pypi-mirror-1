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
import unittest

logging.disable(logging.WARNING)

import turbogears
import turbomail

from tests.lib.smtp_mailsink import SMTPMailsink
from tests.lib.utils import get_received_mail, save_config


class TestMessageAsString(unittest.TestCase):
	"Test cases for sending emails as plain strings with TurboMail."

	def setUp(self):
		server_port = 42042
		test_config = {'mail.on': True, 'mail.timeout': 1,
					   'mail.server': 'localhost:%d' % server_port}
		self._original_config = save_config(test_config.keys())
		turbogears.config.update(test_config)
		
		self.sink = SMTPMailsink(host='localhost', port=server_port)
		self.sink.start()
		turbogears.startup.startTurboGears()


	def tearDown(self):
		turbogears.startup.stopTurboGears()
		turbogears.config.update(self._original_config)
		self.sink.stop()


	def test_message_string(self):
		"""Test that a message can be submitted as string (not as 
		turbomail.Message). This is important when existing (e.g. from a 
		mailbox) or digitally signed messages should be sent through 
		TurboMail."""
		msg_string = """From: bar@xams.example
To: foo@xams.example
Subject: foo bar
MIME-Version: 1.0
Content-Type: text/plain;
Date: Fri, 15 Dec 2006 01:54:00 +0200

Hello World!"""
		sender = 'sender@foobar.example'
		recipient = 'recipient@foo.example'
		msginfo = dict(sender=sender, recipients=[recipient], message=msg_string)
		turbomail.enqueue(msginfo)

		msginfo = get_received_mail(self.sink)
		self.assertEqual(sender, msginfo['from'])
		self.assertEqual([recipient], msginfo['recipients'])
		self.assertEqual(msg_string, msginfo['mail'])

