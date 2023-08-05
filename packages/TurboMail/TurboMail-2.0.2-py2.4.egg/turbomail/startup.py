# encoding: utf-8

"""TurboGears extension startup and shutdown interface."""

import logging
log = logging.getLogger("turbomail.startup")

import turbogears

import turbomail
from turbomail.exceptions import *
from turbomail.pool import MailPool

from email import Charset


__all__ = ['start_extension', 'shutdown_extension', 'MailTemplate']


def start_extension():
	"""TurboGears extension startup.
	
	Exits immediately if TurboMail is not enabled and creates a MailPool
	instance if all is well.
	"""
	
	if not turbogears.config.get("mail.on", False):
		return
	
	if turbogears.config.get("mail.server", None) is None:
		raise MailConfigurationException("Outbound server must be specified.")
	
	log.info("Outbound mail queue manager starting.")
	
	if turbogears.config.get("mail.encoding", "us-ascii") == "utf-8-qp":
		Charset.add_charset('utf-8', Charset.SHORTEST, Charset.QP, 'utf-8')
		turbogears.config.update({"mail.encoding": "utf-8"})
	
	turbomail._queue = MailPool(
			interval=turbogears.config.get("mail.interval", 10),
			threads=turbogears.config.get("mail.threads", 4),
			jobs=turbogears.config.get("mail.jobs", 10),
			timeout=turbogears.config.get("mail.timeout", 60),
			server=turbogears.config.get("mail.server"),
			username=turbogears.config.get("mail.username", None),
			password=turbogears.config.get("mail.password", None),
			debug=turbogears.config.get("mail.debug", False),
			tls=turbogears.config.get("mail.tls", None),
			polling=turbogears.config.get("mail.polling", None)
		)
	
	if turbomail._queue._polling:
		turbomail.queue.start()


def shutdown_extension():
	"""TurboGears extension shutdown.
	
	Exits immediately if TurboMail is not enabled and shuts down the
	MailPool object safely.
	"""
	
	if not turbogears.config.get("mail.on", False):
		return

	log.info("Outbound mail queue manager shutting down.")
	
	# turbomail.queue.shutdown()
	turbomail.queue = None
