# encoding: utf-8

import logging
log = logging.getLogger("turbomail.dispatch")

from smtplib import SMTP


__all__ = ['Dispatch']


class Dispatch(object):

	def __init__(self, server, username=None, password=None, debug=False):
		self.server = server
		self.username = username
		self.password = password
		self.debug = debug
		self.log = None
		
		log.debug("Creating SMTP object.")
		self.connection = SMTP()
		self.connection.set_debuglevel(debug)

	def __del__(self):
		self.disconnect()
	
	@property
	def connected(self):
		return getattr(self.connection, 'sock', None) is not None

	def __nonzero__(self):
		return self.connected
	
	def connect(self):
		if self.connected: return
		
		log.info("Connecting to SMTP server %s." % self.server)
		self.connection.connect(self.server)

		try:
			self.connection.ehlo()
			self.connection.starttls()
			self.connection.ehlo()
			log.debug("TLS enabled on SMTP server.")

		except:
			log.warn("TLS not available on SMTP server.")

		if self.username and self.password:
			log.debug("Authenticating as %s." % self.username)
			self.connection.login(self.username, self.password)
	
	def disconnect(self):
		if not self.connected: return
		
		log.debug("Closing SMTP connection.")
		self.connection.quit()
	
	def __call__(self, message, bulk=False):
		self.connect()
		
		pack = message()
		
		log.info("\"%s\" >> \"%s\" :: \"%s\"" % (pack[0], pack[1], message.message['Subject']))
		self.connection.sendmail(*pack)
		
		if self.debug: self.disconnect()
