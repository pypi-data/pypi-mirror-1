# encoding: utf-8

"""MIME-encoded electronic mail message classes."""

from turbomail import release

import turbogears, re, os, email

import email.Message
from email import Encoders, Charset
from email.Message import Message as MIMEMessage
from email.Utils import formatdate
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Header import Header


__all__ = ['Message', 'KIDMessage']
_rich_to_plain = re.compile(r"(<[^>]+>)")


class Message(object):
	"""Simple e-mail message class.
	
	Message provides a means to easily create e-mail messages to be
	sent through the Dispatch mechanism or MailPool.  Message provides
	various helper functions to correctly format plain text, dual plain
	text and rich text MIME encoded messages, as well as handle
	embedded and external attachments.
	
	All properties can be set from the constructor.
	
	Example usage::
	
		import turbomail
		message = turbomail.Message(
				"from@host.com",
				"to@host.com",
				"Subject",
				plain="This is a plain message."
			)
	
	E-mail addresses can be represented as any of the following:
	 - A string.
	 - A 2-tuple of ("Full Name", "name@host.tld")
	
	Encoding can be overridden on a per-message basis, but note that
	'utf-8-qp' modifies the default 'utf-8' behaviour to output
	quoted-printable, and you will have to change it back yourself if
	you want base64 encoding.
		
	@ivar _processed: Has the MIME-encoded message been generated?
	@type _processed: bool
	@ivar _dirty: Has there been changes since the MIME message was last
	              generated?
	@type _dirty: bool
	@ivar date: The Date header.  Must be correctly formatted.
	@type date: string
	@ivar recipient: The To header.  A string, 2-tuple, or list of
	                 strings or 2-tuples.
	@ivar sender: The From header.  A string or 2-tuple.
	@ivar organization: The Organization header.  I{Optional.}
	@type organization: string
	@ivar replyto: The X-Reply-To header.  A string or 2-tuple.
	               I{Optional.}
	@ivar disposition: The Disposition-Notification-To header.  A string
	                   or 2-tuple.  I{Optional.}
	@ivar cc: The CC header.  As per the recipient property.
	          I{Optional.}
	@ivar bcc: The BCC header.  As per the recipient property.
	           I{Optional.}
	@ivar encoding: Content encoding.  Pulled from I{mail.encoding},
	                defaults to 'us-ascii'.
	@type encoding: string
	@ivar priority: The X-Priority header, a number ranging from 1-5.
	                I{Optional.}  Default: B{3}
	@type priority: int
	@ivar subject: The Subject header.
	@type subject: string
	@ivar plain: The plain text content of the message.
	@type plain: string
	@ivar rich: The rich text (HTML) content of the message.  Plain text
	            content B{must} be available as well.
	@type rich: string
	@ivar attachments: A list of MIME-encoded attachments.
	@type attachments: list
	@ivar embedded: A list of MIME-encoded embedded obejects for use in
	                the text/html part.
	@type embedded: list
	@ivar headers: A list of additional headers.  Can be added in a wide
	               variety of formats: a list of strings, list of
	               tuples, a dictionary, etc.  Look at the code.
	@ivar smtpfrom: The envelope address, if different than the sender.
	"""
	
	def __init__(self, sender=None, recipient=None, subject=None, **kw):
		"""Instantiate a new Message object.
		
		No arguments are required, as everything can be set using class
		properties.  Alternatively, I{everything} can be set using the
		constructor, using named arguments.  The first three positional
		arguments can be used to quickly prepare a simple message.
		
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
		
		self._processed = False
		self._dirty = False
		
		self.date = formatdate(localtime=True)
		self.recipient = recipient
		self.sender = sender
		self.organization = None
		self.replyto = None
		self.disposition = None
		self.cc = []
		self.bcc = []
		self.encoding = turbogears.config.get("mail.encoding", 'us-ascii')
		self.priority = 3
		self.subject = subject
		self.plain = None
		self.rich = None
		self.attachments = []
		self.embedded = []
		self.headers = []
		self.smtpfrom = None
		
		for i, j in kw.iteritems():
			if i in self.__dict__:
				self.__dict__[i] = j
			
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

		part.add_header('Content-Disposition', 'attachment', filename=os.path.basename([name, file][name is None]))
			
		self.attachments.append(part)
	
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
		
		self.embedded.append(part)
	
	def _normalize(self, addresslist):
		"""A utility function to return a list of addresses as a string."""
		
		addresses = []
		for i in [[addresslist], addresslist][type(addresslist) == type([])]:
			if type(i) == type(()):
				addresses.append('"%s" <%s>' % (i[0], i[1]))
			else: addresses.append(i)
		
		return ",\n ".join(addresses)
	
	def _process(self):
		"""Produce the final MIME message.
		
		Additinoally, if only a rich text part exits, strip the HTML to
		produce the plain text part.  (This produces identical output as
		KID, although lacks reverse entity conversion -- &amp;, etc.)
		"""
		
		if self.encoding == 'utf-8-qp':
			Charset.add_charset('utf-8', Charset.SHORTEST, Charset.QP, 'utf-8')
			self.encoding = 'utf-8'
		
		if self.rich and not self.plain:
			self.plain = _rich_to_plain.sub('', self.rich)
		
		if not self.rich:
			if not self.attachments:
				message = MIMEText(self.plain.encode(self.encoding), 'plain', self.encoding)
				
			else:
				message = MIMEMultipart()
				message.attach(MIMEText(self.plain.encode(self.encoding), 'plain', self.encoding))
				
		else:
			if not self.attachments:
				message = MIMEMultipart('alternative')
				message.attach(MIMEText(self.plain.encode(self.encoding), 'plain', self.encoding))
				
				if not self.embedded:
					message.attach(MIMEText(self.rich.encode(self.encoding), 'html', self.encoding))
				else:
					related = MIMEMultipart('related')
					message.attach(related)
					related.attach(MIMEText(self.rich.encode(self.encoding), 'html', self.encoding))
					
					for attachment in self.embedded:
						related.attach(attachment)
			
			else:
				message = MIMEMultipart()
				alternative = MIMEMultipart('alternative')
				message.attach(alternative)

				alternative.attach(MIMEText(self.plain.encode(self.encoding), 'plain', self.encoding))
				
				if not self.embedded:
					alternative.attach(MIMEText(self.rich.encode(self.encoding), 'html', self.encoding))
				else:
					related = MIMEMultipart('related')
					alternative.attach(related)
					related.attach(MIMEText(self.rich.encode(self.encoding), 'html', self.encoding))
					
					for attachment in self.embedded:
						related.attach(attachment)
			
		for attachment in self.attachments:
			message.attach(attachment)

		message.add_header('From', self._normalize(self.sender))
		message.add_header('Subject', self.subject)
		message.add_header('Date', formatdate(localtime=True))
		message.add_header('To', self._normalize(self.recipient))
		if self.replyto: message.add_header('Reply-To', self._normalize(self.replyto))
		if self.cc: message.add_header('Cc', self._normalize(self.cc))
		if self.disposition: message.add_header('Disposition-Notification-To', self._normalize(self.disposition))
		if self.organization: message.add_header('Organization', self.organization)
		if self.priority != 3: message.add_header('X-Priority', self.priority)

		if not self.smtpfrom:
			if type(self.sender) == type([]) and len(self.sender) > 1:
				message.add_header('Sender', self._normalize(self.sender[0]))
				message.add_header('Return-Path', self._normalize(self.sender[0]))
			else:
				message.add_header('Return-Path', self._normalize(self.sender))
		else:
			message.add_header('Return-Path', self._normalize(self.sender))
			message.add_header('Sender', self._normalize(self.smtpfrom))
			message.add_header('Return-Path', self._normalize(self.smtpfrom))
			message.add_header('Old-Return-Path', self._normalize(self.smtpfrom))

		message.add_header('X-Mailer', "TurboMail TurboGears Extension v.%s" % release.version)
		
		if type(self.headers) == type(()):
			for header in self.headers:
				if type(header) in [type(()), type([])]:
					message.add_header(*header)
				elif type(header) == type({}):
					message.add_header(**header)
		
		if type(self.headers) == type({}):
			for name, header in self.headers.iteritems():
				if type(header) in [type(()), type([])]:
					message.add_header(name, *header)
				elif type(header) == type({}):
					message.add_header(name, **header)
				else:
					message.add_header(name, header)
		
		self._message = message
		self._processed = True
		self._dirty = False
	
	def __setattr__(self, name, value):
		"""Set the dirty flag as properties are updated."""
		
		self.__dict__[name] = value
		if name != '_dirty': self.__dict__['_dirty'] = True
	
	def __call__(self):
		"""Produce a valid MIME-encoded message and return valid input
		for the Dispatch class to process.

		@return: Returns a tuple containing sender and recipient e-mail
		         addresses and the string output of MIMEMultipart.
		@rtype: tuple
		"""
		
		if not self._processed or self._dirty:
			self._process()
		
		recipients = []
		
		if isinstance(self.recipient, list):
			recipients.extend(self.recipient)
		else: recipients.append(self.recipient)
		
		if isinstance(self.cc, list):
			recipients.extend(self.cc)
		else: recipients.append(self.cc)
		
		if isinstance(self.bcc, list):
			recipients.extend(self.bcc)
		else: recipients.append(self.bcc)
		
		return dict(
				sender=self.sender,
				to=[[self.recipient], self.recipient][isinstance(self.recipient, list)],
				recipients=[i[1] for i in recipients if isinstance(i, tuple)] + [i for i in recipients if not isinstance(i, tuple)],
				subject=self.subject,
				message=self._message.as_string(),
			)


class KIDMessage(Message):
	"""A template which accepts a named template with arguments.
	
	Example usage::
	
		import turbomail
		message = turbomail.KIDMessage(
				"from@host.com",
				"to@host.com",
				"Subject",
				"app.templates.mail",
				dict()
			)
	
	Do not specify message.plain or message.rich content - the template
	will override what you set.  If you wish to hand-produce content,
	use the Message class.
	"""
	
	def __init__(self, sender, recipient, subject, template, variables={}, **kw):
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
				
		super(KIDMessage, self).__init__(sender, recipient, subject, **kw)
	
	def _process(self):
		"""Automatically generate the plain and rich text content."""
		
		turbogears.view.base._load_engines()
		
		data = dict()
		
		for (i, j) in self._variables.iteritems():
			if callable(j): data[i] = j()
			else: data[i] = j
		
		self.plain = turbogears.view.engines.get('kid').render(data, format="plain", template=self._template)
		self.rich = turbogears.view.engines.get('kid').render(data, template=self._template)
		
		return super(KIDMessage, self)._process()
