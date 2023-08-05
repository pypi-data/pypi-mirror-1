# encoding: utf-8

"""MIME-encoded electronic mail message classes."""

import turbogears

from email.Utils import formatdate
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Encoders import encode_base64


__all__ = ['Message', 'TemplateMessage']


class Message(object):
	"""Simple e-mail message class.
	
	Message provides a means to easily create e-mail messages to be
	sent through the Dispatch mechanism or MailPool.  Message provides
	various helper functions to correctly format plain text, dual plain
	text and rich text MIME encoded messages, as well as handle
	embedded and external attachments.
	
	Example usage::
	
		import turbomail
		message = turbomail.Message(
				"from@host.com",
				"to@host.com",
				"Subject"
			)
		message.plain = "This is a plain message."
	
	@ivar plain: The plain text content of the message.
	@type plain: string
	
	@ivar rich: The rich text (HTML) content of the message.  Plain text
	            content B{must} be available as well.
	@type rich: string
	"""
	
	
	def __init__(self, sender, recipient, subject):
		"""Instantiate a new Message object.
		
		An instance of Message is callable.
		
		@param sender: The e-mail address of the sender.  This is
					   encoded as the "From:" SMTP header.
		@type sender: string
		
		@param recipient: The recipient of the message.	 This gets
						  encoded as the "To:" SMTP header.
		@type recipient: string
		
		@param subject: The subject of the message.	 This gets encoded
						as the "Subject:" SMTP header.
		@type subject: string
		"""
		
		super(Message, self).__init__()
		
		self._message = MIMEMultipart() # ('related')
		self._processed = False
		self._attachments = []
		
		self.plain = None
		self.rich = None

		self._message['From'] = sender
		self._message['To'] = recipient
		self._message['Date'] = formatdate(localtime=True)
		self._message['Subject'] = subject
			
	def attach(self, file, name=None):
		"""Attach an on-disk file to this message.
		
		@param file: The path to the file you wish to attach.
		@type file: string
		
		@param name: You can optionally override the filename of the
		             attached file.  This name will appear in the
		             recipient's mail viewer.  B{Optional.}
		@type name: string
		"""
		
		part = MIMEBase('application', "octet-stream")

		fp = open(file, "rb")
		part.set_payload(fp.read())
		Encoders.encode_base64(part)

		if name:
			part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(name))
		else:
			part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
			
		self._attachments.append(part)
	
	def embed(self, file, name):
		"""Attach an on-disk image file and prepare for HTML embedding.
		
		This method should only be used to embed images.
		
		@param file: The path to the file you wish to attach.
		@type file: string
		
		@param name: The CID name to use for the embedded object.
		@type name: string
		"""
		
		from email.MIMEImage import MIMEImage
		
		fp = open(file, 'rb')
		part = MIMEImage(fp.read())
		fp.close()
		
		part.add_header('Content-ID', '<%s>' % name)
		
		self._attachments.append(part)

	def _process(self):
		"""Produce the final MIME message."""
		
		if self.plain and self.rich:
			alternative = MIMEMultipart('alternative')
			self._message.attach(alternative)
			
			alternative.attach(MIMEText(self.plain))
			alternative.attach(MIMEText(self.rich, 'html'))
		
		else:
			self._message.attach(MIMEText(self.plain))
		
		for attachment in self._attachments:
			self._message.attach(attachment)
		
		self._processed = True 
	
	def __call__(self):
		"""Produce a valid MIME-encoded message and return valid input
		for the Dispatch class to process.

		@return: Returns a tuple containing sender and recipient e-mail
		         addresses and the string output of MIMEMultipart.
		@rtype: tuple
		"""
		
		if not self._processed:
			self._process()
		
		return (self._message['From'], self._message['To'], self._message.as_string())


class TemplateMessage(Message):
	"""A template which accepts a named template with arguments.
	
	Example usage::
	
		import turbomail
		message = turbomail.TemplateMessage(
				"from@host.com",
				"to@host.com",
				"Subject",
				"app.templates.mail"
			)
		message.plain = "This is a plain message."
	"""
	
	def __init__(self, sender, recipient, subject, template, variables={}):
		"""Store the additonal template and variable information.
		
		@param template: A dot-path to a valid KID template.
		@type template: string
		
		@param variables: A dictionary containing named variables to
		                  pass to the template engine.
		@type variables: dict
		"""
		
		self._template = template
		self._variables = dict(sender=sender, recipient=recipient, subject=subject)
		self._variables.update(variables)
				
		super(TemplateMessage, self).__init__(sender, recipient, subject)
	
	def process(self):
		"""Automatically generate the plain and rich text content."""
		
		turbogears.view.base._load_engines()
		
		localvars = dict()
		
		for (i, j) in self._variables.iteritems():
			if callable(j):
				localvars[i] = j()
			else:
				localvars[i] = j
		
		render = turbogears.view.engines.get('kid').transform(localvars, self._template)
		render = turbogears.widgets.base.PlainHTML(elements=render)
		
		self.plain = render.serialize(output="plain")			
		self.rich = render.serialize(output="html")
		
		return super(TemplateMessage, self).process()
