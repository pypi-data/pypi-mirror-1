# encoding: utf-8

"""Generic Pool and MailPool class definitions."""

import logging
log = logging.getLogger("turbomail.pool")

import math
from Queue import Queue, Empty
from threading import Event, Thread
from turbomail.dispatch import Dispatch


__all__ = ['Pool', 'MailPool']


class Pool(Thread):
	"""A threadpool which checks regularily for new jobs and spawns processes
	as needed.
	
	Do not use this class directly.  Always subclass and override the worker
	method.
	"""
	
	def __init__(self, interval=10, threads=4, jobs=10, timeout=60, **kw):
		"""Initialize the threadpool.
		
		@param interval: A delay, in seconds, between spawn runs.
		@type interval: int
		
		@param threads: The maximum number of concurrent threads.
		@type threads: int
		
		@param jobs: The maximum number of jobs a single thread is
		             allowed to handle before dying of old age.
		@type jobs: int
		
		@param timeout: The amount of time, in seconds, a thread is
		                allowed to sit idle before dying of starvation.
		@type timeout: int
		"""
		
		super(Pool, self).__init__()
		
		self._pool = 0
		self._queue = Queue()
		self._finished = Event()
		self._interval = interval
		self._threads = threads
		self._jobs = jobs
		self._timeout = timeout
		self._kw = kw
		
		log.debug("Thread pool created.")
	
	def enqueue(self, work):
		"""Enqueue a Message instance.
		
		@param work: The unit of work can be any callable that returns a
		             three-item tuple containing the sender and
		             recipient addresses and a properly formatted MIME
		             message, in that order.  The preferred type is an
		             instance of the Message class or subclass.
		@type work: callable
		"""
		
		log.debug("Work enqueued.")
		self._queue.put(work)
	
	def shutdown(self):
		"""Quit the management thread and shutdown the queue."""
		
		log.debug("Shutdown requested.")
		self._finished.set()

	def spawn(self):
		thread = Thread(target=self.wrapper)
		thread.start()
		self._pool += 1

	def run(self):
		"""The management thread.
		
		Do not call directly.  Instead, use the I{start} method.
		"""
		
		log.debug("Beginning thread pool main loop.")
		
		while True:
			if self._finished.isSet():
				log.debug("Shutdown request acknowledged.")
				break
			
			if not self._queue.empty():
				log.debug("Estimate %d work units in the queue." % self._queue.qsize())
				
			optimum_threads = min(self._threads, math.ceil(self._queue.qsize() / float(self._jobs)))
			
			if not self._queue.empty() and self._pool < optimum_threads:
				log.debug("Creating %d threads." % (optimum_threads - self._pool))
				for i in xrange(int(optimum_threads - self._pool)):
					self.spawn()
					
			self._finished.wait(self._interval)
			
		log.debug("Thread pool main loop has ended.")
	
	def wrapper(self):
		"""Thread wrapper to log and keep track of the active thread count."""
		
		log.debug("Thread pool worker starting up.")
		
		self.worker()
		
		self._pool -= 1
		log.debug("Thread pool worker finished.")

	def worker(self):
		"""This method must be overridden in a subclass and is used to
		perform the work of the threadpool.
		
		Will raise a NotImplementedError exception if not subclassed."""
		
		raise NotImplementedError


class MailPool(Pool):
	"""Mail delivery threadpool.
	
	This class delivers messages from a queue using the Dispatch class.

	Example usage::
	
		import turbomail
		pool = turbomail.MailPool()
		message = turbomail.Message(
				"from@localhost",
				"to@localhost",
				"Subject"
			)
		message.plain = "Hello world!"
		pool.enqueue(message)

	"""
	
	def worker(self):
		"""Deliver up to I{jobs} messages per queue.
		
		If there are no messages available in the queue, the worker
		will wait up to I{timeout} seconds for data.  If the timeout
		expires, the thread will exit gracefully."""
		
		count = 0
		dispatch = Dispatch(**self._kw)
		
		log.debug("Worker starting work.")
		
		while True:
			if not count < self._jobs:
				log.debug("Worker death from old age - spawning child.")
				self.spawn()
				break
			
			try:
				unit = self._queue.get(True, self._timeout)
				dispatch(unit)

			except Empty:
				log.debug("Worker death from starvation.")
				break
			
			count += 1
