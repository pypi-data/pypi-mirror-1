# encoding: utf-8

"""
Introduction
============

	TurboMail is a TurboGears extension - meaning that it starts up and
	shuts down alongside TurboGears applications you write in the same
	way that visit tracking and identity do.  TurboMail uses built-in
	Python modules for SMTP communication and MIME e-mail creation, but
	greatly simplifies these tasks by performing the grunt-work for you.
	
	Being multi-threaded, TurboMail allows you to enqueue messages to be
	sent and then immediately continue with processing, resulting in a
	much more fluid user experience.  Threads are handled intelligently
	(increasing the number of threads as demand increases) and they are
	automatically recycled.  There is only ever one SMTP connection per
	thread.

Installation
============

	Simply easy_install the package::

		easy_install TurboMail

	TurboMail installs no external scripts.

Configuration
=============

	TurboMail understands a large number of configuration options, all
	piggy-backed from your application's configuration.  Organized into
	two groups, the advanced set can be safely ignored in most
	applications.  Each option is listed with its default value.
	
	Simple Options
	--------------
	
		 - I{mail.on} (Default: B{False}) Enable TurboMail.  B{Required.}
		 - I{mail.server} (Default: B{None}) SMTP server address.
		   B{Required.}
		 - I{mail.username} (Default: B{None})
		 - I{mail.password} (Default: B{None})
	
		Both a username and password are required to enable
		authentication.
	
	Advanced Options
	----------------
	
		 - I{mail.debug} (Default: B{False}) Output all SMTP server
		   communications.
		 - I{mail.interval} (Default: B{10}) Polling delay between new
		   thread creation, in seconds.
		 - I{mail.threads} (Default: B{4}) Maximum number of concurrent
		   threads.
		 - I{mail.jobs} (Default: B{10}) Maximum number of job units per
		   thread.
		 - I{mail.timeout} (Default: B{60}) Maximum time a worker thread
		   will wait for additional jobs, in seconds.
		
		In debug mode using a single thread with a maximum of one job
		can be advantageous.  Having a single thread with a maximum of a
		single job limits TurboMail to a single SMTP connection at a
		time and automatically disconnects for I{each message}.

Basic Usage
===========

	To use TurboMail in your TurboGears application, after adding the
	appropriate configuration options to your application, perform the
	following steps:
	
	 1. Import TurboMail::
	
	    	import turbomail
	
	 2. Create a L{Message} or L{TemplateMessage} object::
	
	    	message = turbomail.Message(from, to, subject)
	
	 3. Set some content for your message::
	
	    	message.plain = "Hello world!"
	
	 4. Enqueue your message::
	
	    	turbomail.enqueue(message)
	
	Your message will now have been enqueued.  It will take at most
	I{mail.interval} seconds for a thread to be created to deliver it.
	The best case scenario is if there is an idle thread waiting, in
	which case delivery will be immediate.

@var queue: After TurboGears startup within an application which has
            enabled TurboMail, I{queue} is an instance of a MailPool
            object.

@var enqueue: After TurboGears startup within an application which has
              enabled TurboMail, I{enqueue} becomes a bound reference to
              the L{enqueue} method of the I{queue} object.
		
"""

import logging
log = logging.getLogger("turbomail")

from turbomail.startup import start_extension, shutdown_extension
from turbomail.exceptions import *
from turbomail.message import Message, TemplateMessage


__all__ = ['MailException', 'MailNotEnabledException', 'MailConfigurationException', 'Message', 'TemplateMessage', 'enqueue', 'dispatch', 'exceptions', 'message', 'pool', 'release', 'startup']


queue = None

def enqueue():
	"""Enqueue a message in the message thread-pool queue.
	
	After TurboGears startup within an application which has enabled
	TurboMail, I{enqueue} becomes a bound reference to the L{enqueue}
	method of the I{queue} object."""
	
	raise MailNotEnabledException
