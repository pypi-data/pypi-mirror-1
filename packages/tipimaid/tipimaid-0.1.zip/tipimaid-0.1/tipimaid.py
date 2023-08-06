#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2008, 2009
#      Nik Tautenhahn (nik@livinglogic.de)
#      Walter Dörwald (walter@livinglogic.de)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (see the file COPYING); if not, see
# <http://www.gnu.org/licenses/>.


import sys, os, datetime, errno, bisect, re, gzip, signal, time
try:
	import threading
except ImportError:
	import dummy_threading as threading
from collections import deque
from Queue import *

subprocessworks = False

try:
	import subprocess # only python >= 2.6
	subprocessworks = True
except ImportError:
	pass

if not hasattr(Queue, "task_done"): # We need a newer implementation of Queue, this one is taken from 2.6 and slightly modified to use old Python-API syntax (notifyAll (old) instead of notify_all (new))
	class Empty(Exception):
		"Exception raised by Queue.get(block=0)/get_nowait()."
		pass

	class Full(Exception):
		"Exception raised by Queue.put(block=0)/put_nowait()."
		pass

	class Queue:
		"""Create a queue object with a given maximum size.

		If maxsize is <= 0, the queue size is infinite.
		"""
		def __init__(self, maxsize=0):
			self.maxsize = maxsize
			self._init(maxsize)
			# mutex must be held whenever the queue is mutating.  All methods
			# that acquire mutex must release it before returning.  mutex
			# is shared between the three conditions, so acquiring and
			# releasing the conditions also acquires and releases mutex.
			self.mutex = threading.Lock()
			# Notify not_empty whenever an item is added to the queue; a
			# thread waiting to get is notified then.
			self.not_empty = threading.Condition(self.mutex)
			# Notify not_full whenever an item is removed from the queue;
			# a thread waiting to put is notified then.
			self.not_full = threading.Condition(self.mutex)
			# Notify all_tasks_done whenever the number of unfinished tasks
			# drops to zero; thread waiting to join() is notified to resume
			self.all_tasks_done = threading.Condition(self.mutex)
			self.unfinished_tasks = 0

		def task_done(self):
			"""Indicate that a formerly enqueued task is complete.

			Used by Queue consumer threads.  For each get() used to fetch a task,
			a subsequent call to task_done() tells the queue that the processing
			on the task is complete.

			If a join() is currently blocking, it will resume when all items
			have been processed (meaning that a task_done() call was received
			for every item that had been put() into the queue).

			Raises a ValueError if called more times than there were items
			placed in the queue.
			"""
			self.all_tasks_done.acquire()
			try:
				unfinished = self.unfinished_tasks - 1
				if unfinished <= 0:
					if unfinished < 0:
						raise ValueError('task_done() called too many times')
					self.all_tasks_done.notifyAll() # old API, in 2.6: notify_all
				self.unfinished_tasks = unfinished
			finally:
				self.all_tasks_done.release()

		def join(self):
			"""Blocks until all items in the Queue have been gotten and processed.

			The count of unfinished tasks goes up whenever an item is added to the
			queue. The count goes down whenever a consumer thread calls task_done()
			to indicate the item was retrieved and all work on it is complete.

			When the count of unfinished tasks drops to zero, join() unblocks.
			"""
			self.all_tasks_done.acquire()
			try:
				while self.unfinished_tasks:
					self.all_tasks_done.wait()
			finally:
				self.all_tasks_done.release()

		def qsize(self):
			"""Return the approximate size of the queue (not reliable!)."""
			self.mutex.acquire()
			n = self._qsize()
			self.mutex.release()
			return n

		def empty(self):
			"""Return True if the queue is empty, False otherwise (not reliable!)."""
			self.mutex.acquire()
			n = not self._qsize()
			self.mutex.release()
			return n

		def full(self):
			"""Return True if the queue is full, False otherwise (not reliable!)."""
			self.mutex.acquire()
			n = 0 < self.maxsize == self._qsize()
			self.mutex.release()
			return n

		def put(self, item, block=True, timeout=None):
			"""Put an item into the queue.

			If optional args 'block' is true and 'timeout' is None (the default),
			block if necessary until a free slot is available. If 'timeout' is
			a positive number, it blocks at most 'timeout' seconds and raises
			the Full exception if no free slot was available within that time.
			Otherwise ('block' is false), put an item on the queue if a free slot
			is immediately available, else raise the Full exception ('timeout'
			is ignored in that case).
			"""
			self.not_full.acquire()
			try:
				if self.maxsize > 0:
					if not block:
						if self._qsize() == self.maxsize:
							raise Full
					elif timeout is None:
						while self._qsize() == self.maxsize:
							self.not_full.wait()
					elif timeout < 0:
						raise ValueError("'timeout' must be a positive number")
					else:
						endtime = _time() + timeout
						while self._qsize() == self.maxsize:
							remaining = endtime - _time()
							if remaining <= 0.0:
								raise Full
							self.not_full.wait(remaining)
				self._put(item)
				self.unfinished_tasks += 1
				self.not_empty.notify()
			finally:
				self.not_full.release()

		def put_nowait(self, item):
			"""Put an item into the queue without blocking.

			Only enqueue the item if a free slot is immediately available.
			Otherwise raise the Full exception.
			"""
			return self.put(item, False)

		def get(self, block=True, timeout=None):
			"""Remove and return an item from the queue.

			If optional args 'block' is true and 'timeout' is None (the default),
			block if necessary until an item is available. If 'timeout' is
			a positive number, it blocks at most 'timeout' seconds and raises
			the Empty exception if no item was available within that time.
			Otherwise ('block' is false), return an item if one is immediately
			available, else raise the Empty exception ('timeout' is ignored
			in that case).
			"""
			self.not_empty.acquire()
			try:
				if not block:
					if not self._qsize():
						raise Empty
				elif timeout is None:
					while not self._qsize():
						self.not_empty.wait()
				elif timeout < 0:
					raise ValueError("'timeout' must be a positive number")
				else:
					endtime = _time() + timeout
					while not self._qsize():
						remaining = endtime - _time()
						if remaining <= 0.0:
							raise Empty
						self.not_empty.wait(remaining)
				item = self._get()
				self.not_full.notify()
				return item
			finally:
				self.not_empty.release()

		def get_nowait(self):
			"""Remove and return an item from the queue without blocking.

			Only get an item if one is immediately available. Otherwise
			raise the Empty exception.
			"""
			return self.get(False)

		# Override these methods to implement other queue organizations
		# (e.g. stack or priority queue).
		# These will only be called with appropriate locks held

		# Initialize the queue representation
		def _init(self, maxsize):
			self.queue = deque()

		def _qsize(self, len=len):
			return len(self.queue)

		# Put a new item in the queue
		def _put(self, item):
			self.queue.append(item)

		# Get an item from the queue
		def _get(self):
			return self.queue.popleft()


class WorkerThread(threading.Thread):
	workqueue = Queue(0)

	def __init__(self, do_something):
		threading.Thread.__init__(self)
		self.do_something = do_something

	def run(self):
		while True:
			args = WorkerThread.workqueue.get()
			self.do_something(args)
			WorkerThread.workqueue.task_done()


class LogLine(tuple):
	"""
	Helper Class which overwrites "<" and "<=" to do the right things for
	tipimaid-loglines - it should only be sorted according to the datetime
	of the logline.
	"""
	def __lt__(self, other):
		return self[0] < other[0]

	def __le__(self, other):
		return self[0] <= other[0]


class Buffer(object):
	"""
	The main class of tipimaid
	"""
	def __init__(self, pattern='', gzip_logs=None, buffertime=0, stream=sys.stdin, utcrotate=False, symlinkpattern=None, execute=None, progname="tipimaid", num_threads=3):
		self.pattern = pattern
		self.gzip_logs = gzip_logs
		self.data = []
		self.servers = {}
		self.buffertime = datetime.timedelta(seconds=buffertime)
		self.stream = stream
		self.re_find_date = re.compile(" \[(.*?)\] ")
		if gzip_logs is not None and not pattern.endswith(".gz"):
			self.pattern = "%s.gz" % self.pattern
		self.utcrotate = utcrotate
		self.execute = execute
		self.updateutcoffset()
		self.handlevirtualhost = "%v" in pattern
		self.symlinkpattern = symlinkpattern
		self.progname = progname
		self.num_threads = num_threads
		if buffertime > 0:
			self.run = self.run_buffered
		else:
			self.run = self.run_unbuffered

	def set_up_threads(self):
		self.threads = [WorkerThread(do_something=self.do_something) for i in xrange(self.num_threads)]
		for thr in self.threads:
			thr.setDaemon(True)
			thr.start()

	def openfile(self, filename, server):
		"""
		opens a file filename for server server which may be continuously gzipped. Closes old files, creates directories, if necessary
		"""
		try:
			f = open(filename, "a", 1)
		except IOError, exc:
			if exc.errno == errno.ENOENT:
				os.makedirs(os.path.dirname(filename))
				f = open(filename, "a", 1)
			else:
				raise
		if self.symlinkpattern:
			symlinkname = self.symlinkpattern.replace("%v", server)
			try:
				os.symlink(os.path.abspath(filename), symlinkname)
			except OSError, exc:
				if exc.errno == errno.ENOENT:
					os.makedirs(os.path.dirname(symlinkname))
					os.symlink(os.path.abspath(filename), symlinkname)
				elif exc.errno == errno.EEXIST:
					os.remove(symlinkname)
					os.symlink(os.path.abspath(filename), symlinkname)
				else:
					raise
		if self.gzip_logs is not None:
			f = gzip.GzipFile(fileobj=f, compresslevel=self.gzip_logs)
			f.name = f.fileobj.name # gzip-fileobjects don't have a name attribute
		return f

	def readlines(self):
		"""
		Gets lines from stdin and splits the virtual host from the rest of the
		line if virtual hosts are used.
		"""
		while True:
			try:
				line = self.stream.readline()
			except IOError, exc:
				if exc[0] == errno.EINTR:
					continue
				else:
					raise
			if not line:
				break
			if self.handlevirtualhost:
				ret = line.split(None, 1)
				if ret == []:
					ret = [None, None]
				yield ret
			else:
				yield (None, line)

	def writeline(self, utclogdate, server, line):
		"""
		Writes the logline ``line`` for server ``server`` which has the date
		``utcdate`` to the right logfile (i.e. it checks if an already opened
		logfile is still correct or if it has to be rotated).

		This method also triggers the execution of external scripts after a
		logfile has been rotated.
		"""
		if not self.utcrotate:
			utclogdate += self.localutcoffset
		filename = utclogdate.strftime(self.pattern)
		if self.handlevirtualhost:
			filename = filename.replace("%v", server)
		if server in self.servers:
			f = self.servers[server]
			if f.name != filename:
				f.flush()
				f.close()
				if self.execute is not None:
					WorkerThread.workqueue.put(os.path.abspath(f.name))
#					thr = threading.Thread(target=self.do_something, args=[os.path.abspath(f.name)])
#					thr.start()
				self.updateutcoffset()
				self.servers[server] = f = self.openfile(filename, server)
		else:
			self.servers[server] = f = self.openfile(filename, server)
		f.write(line)
		f.flush()

	def run_unbuffered(self):
		"""
		Tries to find the date/time of a logline. This is the unbuffered case.
		"""
		if self.execute:
			self.set_up_threads()
		signal.signal(signal.SIGHUP, self.sighandler)
		signal.signal(signal.SIGTERM, self.sighandler)
		signal.signal(signal.SIGINT, self.sighandler)
		signal.signal(signal.SIGQUIT, self.sighandler)
		try:
			for (server, data) in self.readlines():
				try:
					if server is None and data is None: # got an empty line
						continue
					datestring = self.re_find_date.findall(data)[0]
					utclogdate = self.apachedate2utc(datestring)
					self.writeline(utclogdate, server, data)
				except IndexError, exc: # index error because we didn't find an apache date -> malformed logline
					continue # ignore it
		except Exception, exc:
			self.flushall()
			raise

	def run_buffered(self):
		"""
		Tries to find the date/time of a logline. This is the buffered case.
		"""
		if self.execute:
			self.set_up_threads()
		signal.signal(signal.SIGHUP, self.sighandler)
		signal.signal(signal.SIGTERM, self.sighandler)
		signal.signal(signal.SIGINT, self.sighandler)
		signal.signal(signal.SIGQUIT, self.sighandler)
		try:
			for (server, data) in self.readlines():
				try:
					if server is None and data is None: # got an empty line
						continue
					datestring = self.re_find_date.findall(data)[0]
					utclogdate = self.apachedate2utc(datestring)
					self.add(LogLine((utclogdate, server, data)))
				except IndexError, exc: # index error because we didn't find an apache date -> malformed logline
					continue # ignore it
				except Exception, exc:
					sys.stderr.write("[%s] [%s] Exception encountered: %r\nVhost was: %s\nData was: %r\n" % (datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), self.progname, exc, server, data))
					sys.stderr.flush()
					raise
		except Exception, exc:
			self.flushall()
			raise

	def do_something(self, filename):
		"""
		Execute the command which was given with the --execute option
		"""
		try:
			if subprocessworks:
				retcode = subprocess.call("%s %s" % (self.execute, filename), shell=True)
			else:
				retcode = os.system("%s %s" % (self.execute, filename))
			if retcode != 0:
				sys.stderr.write("[%s] [%s] Subprocess \"%s %s\" returned error code %s\n" % (datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), self.progname, self.execute, filename, retcode))
				sys.stderr.flush()
		except OSError, exc:
			sys.stderr.write("[%s] [%s] Subprocess \"%s %s\" caused exception %r\n" % (datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), self.progname, self.execute, filename, retcode))
			sys.stderr.flush()

	def add(self, logline):
		"""
		Keeps entries in the buffer sorted.
		"""
		if not self.data or self.data[-1] <= logline:
			self.data.append(logline)
		else:
			bisect.insort_right(self.data, logline)
		self.flush()

	def flushall(self):
		"""
		Write all loglines content to their files.
		"""
		for (utclogdate, server, logdata) in self.data:
			self.writeline(utclogdate, server, logdata)
		self.data = []

	def flush(self):
		"""
		Write buffered loglines to their files if they have been in the buffer
		for ``buffertime`` seconds.
		"""
		while self.data:
			line = self.data[0]
			(utclogdate, server, logdata) = line
			if datetime.datetime.utcnow() - utclogdate < self.buffertime:
				return
			self.writeline(utclogdate, server, logdata)
			self.data.pop(0)

	def apachedate2utc(self, d):
		"""
		Converts an "apachedate", i.e. a string like
		"01/Jan/2009:01:02:03 +0100"
		to a (UTC) datetime object.
		"""
		temp = d.split()
		utcdate = datetime.datetime(*(time.strptime(temp[0], "%d/%b/%Y:%H:%M:%S")[0:6])) # support ancient distributions with python < 2.5
		minsoff = int("%s%s" % (temp[1][0], temp[1][-2:]))
		hrsoff = int("%s%s" % (temp[1][0], temp[1][1:3]))
		utcdate -= datetime.timedelta(hours=hrsoff, minutes=minsoff)
		return utcdate

	def updateutcoffset(self):
		"""
		Updates the offset of the local system clock to UTC time. (Daylight
		savings time might have changed... or you managed to move your
		server across a timezone without switching it off or...)
		"""
		temp = datetime.datetime.now() - datetime.datetime.utcnow()
		self.localutcoffset = datetime.timedelta(days=temp.days, seconds=temp.seconds+1, microseconds=0)

	def sighandler(self, signum, frame):
		"""
		Signal handler which specifies what to do if someone wants to quit,
		term or interrupt us. (If someone wants to kill us, we can't react...)
		"""
		self.flushall()
		if signum in (signal.SIGQUIT, signal.SIGTERM, signal.SIGINT):
			WorkerThread.workqueue.join() # execute everything which is scheduled to be executed by now
			sys.exit(signum)
		self.flushall() # finishing workers might take some time...

def main(args=None):
	import optparse
	p = optparse.OptionParser(usage="usage: %prog filename-pattern [options]\nIf you use virtual hosts please note that the virtual host column (%v) has to be the first column in every logfile!")
	p.add_option("-b", "--buffertime", dest="buffertime", metavar="SECONDS", type="int", action="store", help="Time in seconds for which log entries are buffered, default=0. Set to 0 to disable buffering.", default=0)
	p.add_option("-z", "--continuous-gzip", dest="gzip", metavar="COMPRESSIONLEVEL", type="int", action="store", help="If set, logs are (continuously!) gzipped with this compression level (lowest: 1, highest: 9).", default=None)
	p.add_option("-u", "--utcrotate", dest="utcrotate", action="store_true", help="If set, UTC time determines the time for filenames and rotation. Otherwise local time is used.", default=False)
	p.add_option("-s", "--symlink", dest="symlinkpattern", metavar="FILEPATTERN", action="store", help="""Create a symlink pointing to the most recent log file (of each virtual host if you use %v). Needs a filename pattern for the symlink (e.g. %v/access.log or symlinks/access-%v.log). Only "%v" is allowed in the pattern as symlinks which include time/date data are useless.""", default=None)
	p.add_option("-x", "--execute", dest="execute", metavar="COMMAND", type="string", action="store", help="""After writing to a logfile is finished and a new one is created (e.g. after rotating the logs), the given executable (given without parameters!) is started with the finished logfile as its (only) parameter. You could use gzip, bzip2, a self-written bash-script or even rm here. """, default=None)
	p.add_option("-t", "--threads", dest="num_threads", metavar="NUMBER_OF_THREADS", type="int", action="store", help="Specifies the number of allowed worker threads for -x/--execute, default is 3", default=3)
	(options, args) = p.parse_args()
	if options.gzip is not None:
		if options.gzip < 1:
			options.gzip = 1
		elif options.gzip > 9:
			options.gzip = 9
	if len(args) != 1:
		p.print_usage(sys.stderr)
		sys.stderr.write("%s: We need a filename-pattern\n" % p.get_prog_name())
		sys.stderr.flush()
		return 1
	if options.symlinkpattern is not None and ("%v" in args[0] and ("%v" in options.symlinkpattern and options.symlinkpattern.count("%") > 1) or ("%v" not in options.symlinkpattern)):
		p.print_usage(sys.stderr)
		sys.stderr.write("%s: If you split logfiles by virtual hosts you should use virtual hosts (%v) in the symlink-pattern as well. But you shouldn't use any patterns for time/date data.\n" % p.get_prog_name())
		sys.stderr.flush()
		return 1

	buf = Buffer(pattern=args[0], gzip_logs=options.gzip, buffertime=options.buffertime, utcrotate=options.utcrotate, symlinkpattern=options.symlinkpattern, execute=options.execute, progname=p.get_prog_name(), num_threads=options.num_threads)
	buf.run()


if __name__ == "__main__":
	sys.exit(main())
