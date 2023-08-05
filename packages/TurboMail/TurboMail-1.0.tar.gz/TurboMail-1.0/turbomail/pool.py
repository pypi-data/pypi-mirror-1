# encoding: utf-8

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
	
	interval is the delay, in seconds, between spawn runs
	threads is the maximum number of threads running at any given time
	jobs is the maximum number of jobs a single thread is allowed to handle
	timeout is the amount of time a thread is willing to wait for new data
	"""
	
	def __init__(self, interval=10.0, threads=4, jobs=10, timeout=60, **kw):
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
		log.debug("Work enqueued.")
		self._queue.put(work)
	
	def shutdown(self):
		log.debug("Shutdown requested.")
		self._finished.set()

	def run(self):
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
					thread = Thread(target=self.wrapper)
					thread.start()
					self._pool += 1
					
			self._finished.wait(self._interval)
			
		log.debug("Thread pool main loop has ended.")
	
	def wrapper(self):
		log.debug("Thread pool worker starting up.")
		
		self.worker()
		
		self._pool -= 1
		log.debug("Thread pool worker finished.")

	def worker(self):
		raise NotImplementedError


class MailPool(Pool):
	def worker(self):
		count = 0
		dispatch = Dispatch(**self._kw)
		
		log.debug("Worker starting work.")
		
		while True:
			if not count < self._jobs:
				log.debug("Worker death from old age.")
				break
			
			try:
				unit = self._queue.get(True, self._timeout)
				dispatch(unit)

			except Empty:
				log.debug("Worker death from starvation.")
				break
			
			count += 1			
