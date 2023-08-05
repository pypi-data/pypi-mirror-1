# encoding: utf-8

import turbogears

from email.Utils import formatdate
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Encoders import encode_base64


__all__ = ['Message', 'TemplateMessage']


class Message(object):

	def __init__(self, sender, recipient, subject):
		self.message = MIMEMultipart() # ('related')
		self.plain = None
		self.rich = None
		self.attachments = []
		self.processed = False

		self.message['From'] = sender
		self.message['To'] = recipient
		self.message['Date'] = formatdate(localtime=True)
		self.message['Subject'] = subject
	
	def attach(self, file, name=None):
		part = MIMEBase('application', "octet-stream")

		fp = open(file, "rb")
		part.set_payload(fp.read())
		Encoders.encode_base64(part)

		if name:
			part.add_header('Content-Disposition', 'attachment; filename="%s"' % name)
		else:
			part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
			
		self.attachments.append(part)
	
	def embed(self, file, name):
		from email.MIMEImage import MIMEImage
		
		fp = open(file, 'rb')
		part = MIMEImage(fp.read())
		fp.close()
		
		part.add_header('Content-ID', '<%s>' % name)
		
		self.attachments.append(part)

	def process(self):
		if self.plain and self.rich:
			alternative = MIMEMultipart('alternative')
			self.message.attach(alternative)
			
			alternative.attach(MIMEText(self.plain))
			alternative.attach(MIMEText(self.rich, 'html'))
		
		else:
			self.message.attach(MIMEText(self.plain))
		
		for attachment in self.attachments:
			self.message.attach(attachment)
		
		self.processed = True 
	
	def __call__(self):
		if not self.processed:
			self.process()
		
		return (self.message['From'], self.message['To'], self.message.as_string())


class TemplateMessage(Message):
	
	def __init__(self, sender, recipient, subject, template, variables):
		self.template = template
		self.variables = dict(sender=sender, recipient=recipient, subject=subject)
		self.variables.update(variables)
				
		super(TemplateMessage, self).__init__(sender, recipient, subject)
	
	def process(self):
		turbogears.view.base._load_engines()
		
		localvars = dict()
		
		for (i, j) in self.variables.iteritems():
			if callable(j):
				localvars[i] = j()
			else:
				localvars[i] = j
		
		render = turbogears.view.engines.get('kid').transform(localvars, self.template)
		render = turbogears.widgets.base.PlainHTML(elements=render)
		
		self.plain = render.serialize(output="plain")			
		self.rich = render.serialize(output="html")
		
		return super(TemplateMessage, self).process()
