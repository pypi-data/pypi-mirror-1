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
	
	Benchmarking
	------------
	
		Throughput using the default options is sufficient for most use:
		100 messages in 45 seconds; just over 2 messages a second. Using
		a greater number of threads, 10 vs. 4, 100 messags take 30
		seconds; just over 3 messages a second.  YMMV.  Note that if a
		thread is idle, it will immediately deliver requests added to
		the queue, thus increasing the idle time will increase sparse
		performance.
	
	TurboMail is heavily inspired by PHPMailer, a very, very handy class
	for PHP 4 & 5 by Brent R. Matzelle.
	

Installation
============

	Simply easy_install the package::

		easy_install TurboMail

	TurboMail installs no external scripts.

Upgrade
=======

	Upgrading also uses easy_install::
	
		easy_install -U TurboMail

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
		 - I{mail.tls} (Defalut: None) Enable or disable TLS, None will
		   attempt to auto-detect TLS.  This will not always work.
		 - I{mail.encoding} (Default: B{'us-ascii'}) Set the character
		   set and encoding on the MIMEText parts of the message.
		   Common character sets include:
		    - us-ascii - I{Performs no encoding, but is 7bit only.}
		    - iso-8859-1 - I{Uses quoted-printable encoding.}
		    - utf-8 - I{Uses base64 encoding.}
		   Due to the way Python's email package handles character sets,
		   the following additional virtual character sets are provided
		   by TurboMail, and will override the global defaults:
		    - utf-8-qp - I{Sets utf-8 to use quoted-printable encoding.}
		   Headers are not encoded.  DIY.
		 - I{mail.polling} (Defaut: B{False}) If enabled, configures the
		   thread pool to poll every I{mail.interval} seconds for new
		   jobs.  This may give performance benefits to the running
		   application.  The default behaviour is to create new threads
		   as soon as work is enqueued, resulting in faster delivery.
		
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
	
	 2. Create a L{Message} or L{KIDMessage} object::
	
	    	message = turbomail.Message(from, to, subject)
	
	 3. Set some content for your message::
	
	    	message.plain = "Hello world!"
	
	 4. Enqueue your message::
	
	    	turbomail.enqueue(message)
	
	Your message will now have been enqueued.  It will take at most
	I{mail.interval} seconds for a thread to be created to deliver it.
	The best case scenario is if there is an idle thread waiting, in
	which case delivery will be immediate.

Advanced Usage - Logging
========================

	Additionally, you can configure your application to log TurboMail
	events differently, in a more loggable and machine parsable way.
	You do so by adding the following lines to the formatters section
	of your log.cfg::
	
		[[[timed_message]]]
		format='*(asctime)s *(message)s'
	
	Add the following to the handlers section of log.cfg::
	
		[[[mail_out]]]
		class='StreamHandler'
		level='INFO'
		args='(sys.stdout,)'
		formatter='timed_message'
	
	And finally, add the following to your dev.cfg::
	
		[[[mail]]]
		level='INFO'
		qualname='turbomail.dispatch'
		handlers=['mail_out']
		propagate=0
	
	If you wish to log mail dispatch to a file, for example in your
	production configuration, use this instead of the above::
	
		[[handlers]]
		[[[mail_out]]]
		args="('mail.log',)"
		class='StreamHandler'
		level='INFO'
		formatter='timed_message'
		
		[[loggers]]
		[[[mail]]]
		level='INFO'
		qualname='turbomail.dispatch'
		handlers=['mail_out']
		propagate=0
	
	The format of turbomail.dispatch INFO log entries is::
	
		[user@]server size ("from_name") from_addr ("to_name") to_addr - subject
	
	Designed for easy parsing and tracking of statistics, the log
	format uses the following conventions:
	
	 - Entries between square brackets are optional and may be omitted.
	 - Entries between round brackets may be replaced with a dash if
	   unavailable.
	 - The size field is in bytes and represents the total size of the
	   MIME-encoded message including headers, after character set
	   conversion.
	 - When sending to multiple recipients, the to_addr field becomes
	   the number of recipients wrapped in round brackets.  E.g. "(3)"
	 - The subject field extends to the EOL - quotes, dashes, and other
	   symbols should be treated as part of the subject.

Changelog
=========

	Version 1.0
	-----------
		 - Initial release.
	
	Version 1.0.1
	-------------
		 - Minor updates to remove unneeded arguments.
		 - Complete source-level epydoc documentation.
	
	Version 1.0.4.1
	---------------
		 - Better auto-detection of TLS capability.
		 - A new configuration directive, mail.tls; True, False, or
		   None to auto-detect.
		 - Fixes a bug in KIDMessage which rendered it
		   non-functional.
		 - Changed the behavior of a worker dying from old age to spawn
		   a new process immediately.
		 - Minor fixes and updates to the documentation.
		 - Benchmark results in the documentation.
	
	Version 1.0.4.2
	---------------
		 - Added encoding configuration directive.
		 - Encoding can be passed to a Message constructor to override
		   the encoding on a message-by-message basis.
	
	Version 1.1
	-----------
		 - Cleaned up the log output.
		 - Added documentation for logging.
		 - KID i18n session bug fixed in TurboGears 1.0 and trunk SVN.
		 - Marked as stable for the Python Cheese Shop.
	
	Version 2.0
	-----------
		 - Default thread creation mechanism is on-demand, not polling.
		   You can change back to the (old) polling mechanism by
		   setting the following configuration option::
		   	mail.polling = True
		 - TemplateMessage has been renamed KIDMessage.
		 - Can now use 'utf-8-qp' to configure the 'utf-8' charset for
		   quoted-printable encoding.
		 - MIME-encoded message generation was re-written.  Now, simple
		   plain-text-only messages have almost zero overhead.
		   Complexity of the generated document increases with feature
		   use.
		 - It is now safe to import enqueue from TurboMail - it no
		   longer polymorphs after TurboGears start-up and shutdown.
		 - Enhanced logging output - see above.
		 - Better tracking of when to rebuild the MIME message by using
		   a dirty flag.
		 - Many, many additional headers.  Look at the documentation for
		   the message class for more information.
		 - Multiple recipients.
		
		There is, however, an outstanding bug in KIDMessage.  When
		generating the plain-text alternative KID seems to default
		to ascii encoding, which bombs out if you use any extended
		characters in the template, or variables passed to the template.
		
	Version 2.0.1
	-------------
		 - Applied patch submitted by Jason Chu to allow overriding of
		   the Sender and Return-Path headers.
		 - Applied patch submitted by Jason Chu to correct the MIME
		   type of dual text & html messages with attachments.

	Version 2.0.2
	-------------
		 - Added a generic ControllerMessage which uses the output of
		   any function or method that returns HTML.
		 - Changed the behaviour of the attach and embed methods to
		   pull content from an existing file-like object or open an
		   on-disk file.
		 - Corrected a conditional testing for the presense of
		   smptfrom as a message property.  Thanks James!
		
		More patches are welcome!

@var _queue: After TurboGears startup within an application which has
            enabled TurboMail, I{queue} is an instance of a MailPool
            object.

"""

from turbomail.release import \
		version as __version__, \
		author as __author__, \
		email as __email__, \
		license as __license__, \
		copyright as __copyright__

import logging
log = logging.getLogger("turbomail")

from turbomail.startup import start_extension, shutdown_extension
from turbomail.exceptions import *
from turbomail.message import Message, KIDMessage


__all__ = ['MailException', 'MailNotEnabledException', 'MailConfigurationException', 'Message', 'KIDMessage', 'enqueue', 'dispatch', 'exceptions', 'message', 'pool', 'startup']


_queue = None

def enqueue(work):
	"""Enqueue a message in the message thread-pool queue."""
	
	if _queue is None:
		raise MailNotEnabledException
	
	else:
		_queue.enqueue(work)
