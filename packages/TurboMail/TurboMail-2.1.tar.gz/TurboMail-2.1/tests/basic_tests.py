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
from turbomail.dispatch import Dispatch

from tests.lib.smtp_mailsink import SMTPMailsink
from tests.lib.utils import get_received_mail, save_config

class TestBasicTests(unittest.TestCase):
	"Basic test cases for TurboMail."

	def setUp(self):
		server_port = 42042
		
		test_config = {'mail.on': True, 'mail.timeout': 1,
					   'mail.server': 'localhost:%d' % server_port}
		self._original_config = save_config(test_config.keys())
		turbogears.config.update(test_config)
		
		self.sink = SMTPMailsink(host='localhost', port=server_port)
		self.sink.start()
		
		turbomail.start_extension()


	def tearDown(self):
		turbomail.shutdown_extension()
		turbogears.config.update(self._original_config)
		self.sink.stop()


	def test_simple(self):
		"Test that sending a simple mail with turbomail.Message works."
		sender = 'sender@foo.example'
		recipient = 'recipient@foo.example'
		subject = 'foo bar'
		message = turbomail.Message(sender, recipient, subject)
		message.plain = 'Hello World!'		  
		turbomail.enqueue(message)

		msginfo = get_received_mail(self.sink)
		self.assertEqual(sender, msginfo['from'])
		self.assertEqual([recipient], msginfo['recipients'])
		msg = email.message_from_string(msginfo['mail']) 
		self.failIf(msg.has_key('Old-Return-Path'))
		self.failIf(msg.has_key('Return-Path'))
		assert 'Hello World' in msg.get_payload() 

	def test_smtpfrom(self):
		"Test that smtpfrom is being honored and used as envelope sender."
		sender = 'sender@foo.example'
		recipient = 'recipient@foo.example'
		subject = 'foo bar'
		smtpfrom = 'devnull@foo.example'
		message = turbomail.Message(sender, recipient, subject, 
									smtpfrom=smtpfrom)
		message.plain = 'Hello World!'		  
		turbomail.enqueue(message)
		msginfo = get_received_mail(self.sink)
		self.assertEqual(smtpfrom, msginfo['from'])
		self.assertEqual([recipient], msginfo['recipients'])

	def test_add_custom_headers_dict(self):
		"Test that custom headers (dict type) can be attached."
		extra_headers = {'Precendence': 'bulk', 'X-User': 'Alice'}
		message = turbomail.Message('sender@foo.example', 
									'recipient@foo.example', 'foo bar')
		message.plain = 'Hello World!'
		message.headers = extra_headers
		turbomail.enqueue(message)
		msginfo = get_received_mail(self.sink)
		msg = email.message_from_string(msginfo['mail']) 
		for header_name in extra_headers.keys():
			self.failUnless(msg.has_key(header_name))
			self.assertEquals(extra_headers[header_name], msg[header_name])

	def test_add_custom_headers_tuple(self):
		"Test that a custom header (tuple type) can be attached."
		extra_headers = (('Precendence', 'bulk'), ('X-User', 'Alice'))
		message = turbomail.Message('sender@foo.example', 
									'recipient@foo.example', 'foo bar')
		message.plain = 'Hello World!'
		message.headers = extra_headers
		turbomail.enqueue(message)
		msginfo = get_received_mail(self.sink)
		msg = email.message_from_string(msginfo['mail']) 
		for name, value in extra_headers:
			self.failUnless(msg.has_key(name))
			self.assertEquals(value, msg[name])

	def test_add_custom_headers_list(self):
		"Test that a custom header (list type) can be attached."
		extra_headers = [('Precendence', 'bulk'), ('X-User', 'Alice')]
		message = turbomail.Message('sender@foo.example', 
									'recipient@foo.example', 'foo bar')
		message.plain = 'Hello World!'
		message.headers = extra_headers
		turbomail.enqueue(message)
		msginfo = get_received_mail(self.sink)
		msg = email.message_from_string(msginfo['mail']) 
		for name, value in extra_headers:
			self.failUnless(msg.has_key(name))
			self.assertEquals(value, msg[name])

