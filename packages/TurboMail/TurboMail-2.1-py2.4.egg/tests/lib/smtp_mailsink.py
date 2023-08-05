# -*- coding: UTF-8 -*-
"""A library which implements a SMTP mail sink (dummy SMTP server) in order 
to test correct sending of emails."""

# Copyright (c) 2007 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301	USA 


# This coded is based on code published on 
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/440690/ but was 
# heavily modified for easier usage and Python 2.3 compatibility.
#
# Copyright 2005 Aviarc Corporation
# Written by Adam Feuer, Matt Branthwaite, and Troy Frever
# Published under the Python License (http://www.python.org/license).
 
# Example usage:
# 
# #!/usr/bin/env python
# # -*- coding: UTF-8 -*-
# "Wait until a single message was received on localhost/port 10026"
# 
# from smtp_mailsink import SMTPMailsink
# sink = SMTPMailsink(host='localhost', port=10026)
# sink.start()
# while not sink.has_message():
#	  time.sleep(1)
# print "received message: " + str(sink.get_messages())
# sink.stop()

version = '1.0.1'

import asyncore
import select
import errno
import copy
import smtpd
import threading

class SMTPMailsinkServer(smtpd.SMTPServer):
	"""This is the actual mailsink server which stores all received messages in
	an internal queue. Do not access the queue directly. All accessor methods
	in this object are sufficiently guarded against race conditions."""
	
	def __init__( self, *args, **kwargs):
		smtpd.SMTPServer.__init__( self, *args, **kwargs )
		self.queued_mails = []
		self.lock = threading.Lock()

	def has_message(self):
		"""Return True if at least one message was received successfully. The 
		access to the internal queue is synchronized so the caller will be 
		blocked until the necessary lock was aquired."""
		self.lock.acquire()
		number_messages = len(self.queued_mails)
		self.lock.release()
		return number_messages > 0

	def get_messages(self):
		"""Return a copy of the internal queue with all received messages. The 
		access to the internal queue is synchronized so the caller will be 
		blocked until the necessary lock was aquired."""
		self.lock.acquire()
		messages = copy.copy(self.queued_mails)
		self.lock.release()
		return messages

	def pop(self, index=None):
		"""Return the index'th message in the queue (default=last) which is
		removed from the queue afterwards. Throws IndexError if index is bigger 
		than the number of messages in the queue."""
		item = None
		self.lock.acquire()
		if index == None:
			index = len(self.queued_mails) - 1
		try:
			item = self.queued_mails.pop(index)
		except Exception:
			print 'pop: before lock release'
			self.lock.release()
			raise
		self.lock.release()
		return item


	def process_message(self, peer, mailfrom, rcpttos, data):
		"Store a received message in the internal queue. For internal use only!"
		msg = {'client': peer, 'from': mailfrom, 'recipients': rcpttos, 
			   'mail': data}
		self.lock.acquire()
		self.queued_mails.append(msg)
		self.lock.release()


class SMTPMailsink(threading.Thread):
	"""This class is responsible for controlling the actual mailsink server 
	class."""	

	def __init__(self, host='localhost', port=25):
		threading.Thread.__init__(self)
		self.stop_event = threading.Event()
		self.server = SMTPMailsinkServer((host, port), None)

	def run(self):
		"Just run in a loop until stop() is called."
		while not self.stop_event.isSet():
                        try:
                                asyncore.loop(timeout=0.1)
                        except select.error, e:
                                if e.args[0] != errno.EBADF:
                                        raise

	def stop(self, timeout_seconds=5.0):
		"""Stop the mailsink and shut down this thread. timeout_seconds 
		specifies how long the caller should wait for the mailsink server to 
		close down (default: 5 seconds). If the server did not stop in time, a
		warning message is printed."""
		self.stop_event.set()
		self.server.close()
		threading.Thread.join(self, timeout=timeout_seconds)
		if self.isAlive():
			print "WARNING: Thread still alive. Timeout while waiting for " + \
				  "termination!"
		
	def has_message(self):
		"Return True if at least one message was received successfully."
		return self.server.has_message()
		
	def get_messages(self):
		"Return a copy of the internal queue with all received messages."
		return self.server.get_messages()

	def pop(self, index=None):
		"""Return the index'th message in the queue (default=last) which is
		removed from the queue afterwards. Throws IndexError if index is bigger 
		than the number of messages in the queue."""
		return self.server.pop(index)
