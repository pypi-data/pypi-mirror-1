# encoding: utf-8

"""This module contains only the primary SMTP Dispatch class."""

import logging
log = logging.getLogger("turbomail.dispatch")

from smtplib import SMTP


__all__ = ['Dispatch']


class Dispatch(object):
	"""SMTP message dispatch class.
	
	An instance of the Dispatch class is created for each SMTP
	connection.  Usually, this means one Dispatch instance per
	running thread.
	
	Example usage::
	
		import turbomail
		dispatch = turbomail.Dispatch("localhost")
		message = turbomail.Message(
				"from@localhost",
				"to@localhost",
				"Subject",
				plain="Hello world!"
			)
		dispatch(message)
	"""

	def __init__(self, server, username=None, password=None, tls=None, debug=False):
		"""Initialize the Dispatch class.
		
		Authentication is only performed if both I{username} and
		I{password} are not None.  An instance of Dispatch is callable.
		
		@param server: The server (with optional port number) to
		               connect this instance to.
		@type server: string
		
		@param username: The username to use during authentication.
		                 I{Optional.}
		@type username: string
		
		@param password: The password to use during authentaction.
                         I{Optional.}
		@type password: string
		
		@param debug: Enable SMTP verbose logging.  This outputs all
		              communications between the client and server.
		@type debug: bool
		"""
		
		super(Dispatch, self).__init__()
		
		self.server = server
		self.username = username
		self.password = password
		self.tls = tls
		self.debug = debug
		self.log = None
		
		log.debug("Creating SMTP object.")
		self.connection = SMTP()
		self.connection.set_debuglevel(debug)

	@property
	def connected(self):
		"""Return the current SMTP connection status."""
		
		return getattr(self.connection, 'sock', None) is not None

	def connect(self):
		"""Connect to the SMTP server if not already connected.
		
		This process also automatically enables TLS, if available, and
		authenticates against the username and password previousally
		provided.
		"""
		
		if self.connected: return
		
		log.debug("Connecting to SMTP server %s." % self.server)
		self.connection.connect(self.server)

		if self.tls or self.tls is None:
			self.connection.ehlo()
			
			if self.connection.has_extn('STARTTLS') or self.tls:
				self.connection.starttls()
				self.connection.ehlo()
				log.debug("TLS enabled on SMTP server.")
				self.tls = True
			
			else:
				log.debug("TLS not available on SMTP server.")
				self.tls = False

		if self.username and self.password:
			log.debug("Authenticating as %s." % self.username)
			self.connection.login(self.username, self.password)
	
	def disconnect(self):
		"""Disconnect from the SMTP server if connected."""
		
		if not self.connected: return
		
		log.debug("Closing SMTP connection.")
		self.connection.quit()
	
	def __call__(self, message):
		"""Deliver a message via the current SMTP connection.
		
		Calling an instance of the Dispatch class will automatically
		connect, if needed, and will also automatically disconnect if
		debug mode has been enabled.
		
		@param message: This paramater must be a callable which returns
		                a tuple of (from, to, message), where all three
		                are strings, and message is valid content for an
		                e-mail message.
		@type message: callable
		"""
		
		self.connect()
		
		if callable(message):
			pack = message()
		else:
			pack = message

		pack.update(dict(
				user="",
				server=self.server,
				size=len(pack['message']),
			))
		if self.username: pack['user'] = self.username + "@"
		
		if isinstance(pack['sender'], tuple):
			pack.update(dict(addrfrom='"%s" %s' % pack['sender'], smtpfrom=pack['sender'][1]))
		else:
			pack.update(dict(addrfrom='- %s' % pack['sender'], smtpfrom=pack['sender']))
		
		if len(pack['to']) > 1:
			pack.update(dict(addrto="- (%d)" % len(pack['to'])))
		else:
			if isinstance(pack['to'][0], tuple):
				pack.update(dict(addrto='"%s" %s' % pack['to'][0]))
			else:
				pack.update(dict(addrto='- %s' % pack['to'][0]))

		log.info(
				"%(user)s%(server)s %(size)d %(addrfrom)s %(addrto)s - %(subject)s" % pack
			)
		self.connection.sendmail(pack['smtpfrom'], pack['recipients'], pack['message'])
		
		if self.debug: self.disconnect()
