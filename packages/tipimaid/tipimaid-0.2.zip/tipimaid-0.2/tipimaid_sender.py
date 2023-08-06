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


import sys, socket, select, signal, datetime, os, errno

def intify(s, defaultint=0):
	"""
	Take something, convert it to int, return defaultint if bad things happen.
	"""
	try:
		return int(s)
	except ValueError, exc:
		return defaultint

class Sender(object):
	"""
	The main class for the sender... yadda yadda
	""" # TODO: Write more stuff
	def __init__(self, ip, port, buffertime=0, backuppath=None, stream=sys.stdin, progname="tipimaid_sender"): # TODO: Put the right name in here
		self.ip = ip
		self.port = port
		self.stream = stream
		self.progname = progname
		self.check_every = datetime.timedelta(seconds=10)
		if buffertime > 3:
			self.buffertime = datetime.timedelta(seconds=buffertime - 3) # just to be sure...
		else:
			self.buffertime = datetime.timedelta(seconds=0)
		self.buffer = []
		self.startedbuffering = datetime.datetime.now()
		self.s = None
		self.f = None
		if backuppath: # test if we may write to the backuppath-directory
			backuppath = backuppath.rstrip(os.path.sep)
			try:
				os.chdir(backuppath)
			except OSError, exc:
				sys.stderr.write("Unable to enter directory %s\n" % backuppath)
				raise
			try:
				filename = str(hash(datetime.datetime.now()))
				f = open(os.path.join(backuppath, filename), "a")
				f.close()
				os.remove(os.path.join(backuppath, filename))
			except IOError, exc:
				sys.stderr.write("No write permissions for directory %s\n" % backuppath)
				raise
			self.backuppath = backuppath
		socket.setdefaulttimeout(5) # applies only to *new* sockets so we have to set it here
		self.create_socket()
		self.last_check_connection = datetime.datetime.now()
		signal.signal(signal.SIGHUP, self.sighandler)
		signal.signal(signal.SIGTERM, self.sighandler)
		signal.signal(signal.SIGINT, self.sighandler)
		signal.signal(signal.SIGQUIT, self.sighandler)

	def readlines(self):
		"""
		Gets input from stdin.
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
			yield line

	def create_socket(self):
		"""
		Creates a new socket connection.
		"""
		if self.s is None:
			for (af, socktype, proto, canonname, sa) in socket.getaddrinfo(self.ip, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM):
				try:
					s = socket.socket(af, socktype, proto)
				except socket.error, msg:
					s = None
					continue
				try:
					s.connect(sa)
				except socket.error, exc:
					s.close()
					s = None
					continue
				break
			self.s = s

	def send_socket(self, line):
		"""
		Sends line over socket, sees if this works. If not buffer it and try again later or write it to a tempfile.
		"""
		(l, t) = (len(line), 0)
		while t < l: # it might be that only a part of line gets transmitted
			try:
				t += self.s.send(line[t:])
				ret = self.s.recv(1024)
				if ret == "":
					raise socket.timeout
			except (socket.timeout, socket.error), exc:
				self.s.close()
				self.s = None
				self.last_check_connection = self.startedbuffering = datetime.datetime.now()
				sys.stderr.write("[%s] [%s]: Socket connection lost, starting to log to buffer and/or recovery file\n" % (self.startedbuffering.strftime("%a %b %d %H:%M:%S %Y"), self.progname))
				sys.stderr.flush()
				self.send_tempfile(line)

	def send_tempfile(self, line):
		"""
		Puts line into the local buffer if they are not too old for the server
		to be ordered in correctly. Otherwise line is dumped to a local
		tempfile. This method also checks periodically if a new socket
		connection can be established and, if yes and the buffered data is not
		too old, it is transmitted to the server.
		"""
		if datetime.datetime.now() - self.startedbuffering < self.buffertime:
			self.buffer.append(line)
		else: # this entry is too late - write it to a tempfile
			filename = os.path.join(self.backuppath, datetime.datetime.now().strftime("%Y%m%d_recovery.log"))
			if self.f:
				if self.f.name != filename:
					self.f.close()
					self.f = open(filename, "a", 1)
			else:
				self.f = open(filename, "a", 1)
			if self.buffer: # if we have buffered entries these must be handled before "line"
				sys.stderr.write("[%s] [%s]: Dumping buffered data to local recovery file\n" % (self.startedbuffering.strftime("%a %b %d %H:%M:%S %Y"), self.progname))
				for oldline in self.buffer:
					self.f.write(oldline)
				self.buffer = []
			self.f.write(line)
		td = datetime.datetime.now() - self.last_check_connection
		if td > self.check_every:
			self.create_socket()
			self.last_check_connection = datetime.datetime.now()
			if self.s:
				if self.f:
					self.f.close()
					self.f = None
				if self.buffer: #  the good case: we have buffered entries and got our connection back before the buffertime was over
					for (i, oldline) in enumerate(self.buffer):
						if datetime.datetime.now() - self.startedbuffering < self.buffertime: # make sure we are still in buffertime
							(l, t) = (len(oldline), 0)
							while t < l: # it might be that only a part of line gets transmitted
								try:
									t += self.s.send(oldline[t:])
									ret = self.s.recv(1024)
									if ret == "":
										raise socket.timeout
								except (socket.timeout, socket.error), exc:
									self.s.close()
									self.s = None
									self.buffer = self.buffer[i:] # the first i items were transmitted successfully
									sys.stderr.write("[%s] [tipimaid_sender]: Socket connection died again, while sending buffered data\n" % (datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), self.progname))
									return # our socket died while we were transmitting buffered items - go back to "normal" behaviour
						else: # some buffered entries come too late, maybe because it took so long to wait for the server's response.
							self.s.close() # make sure that we go to this method again to write away all buffered content which is too old
							self.s = None # that's why we throw away our socket
							self.buffer = self.buffer[i:] # and the content which was transmitted to the server in time
							return
					sys.stderr.write("[%s] [%s]: Socket connection established again, all data could be sent to the server\n" % (datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), self.progname))
					self.buffer = [] # if we arrive here everything was sent successfully

	def flush_buffer(self):
		"""
		Flushes all local buffers - either via socket or to a tempfile
		"""
		if not self.s:
			self.create_socket()
			self.last_check_connection = datetime.datetime.now()
		if self.s:
			for (i, oldline) in enumerate(self.buffer):
				if datetime.datetime.now() - self.startedbuffering < self.buffertime: # make sure we are still in buffertime
					(l, t) = (len(oldline), 0)
					while t < l: # it might be that only a part of line gets transmitted
						try:
							t += self.s.send(oldline[t:])
							ret = self.s.recv(1024)
							if ret == "":
								raise socket.timeout
						except (socket.timeout, socket.error), exc:
							self.s.close()
							self.s = None
							self.buffer = self.buffer[i:] # the first i items were transmitted successfully
							break
					else:
						continue # if we didn't break in the while loop, continue for loop
					break # otherwise break the for loop, too
				else: # some buffered entries come too late, maybe because it took so long to wait for the server's response.
					self.buffer = self.buffer[i:]
					break
			else: # we didn't break the for loop so all data was transmitted successfully
				self.buffer = []
				if self.f:
					self.f.close()
					self.f = None
				return
		if self.buffer:
			filename = os.path.join(self.backuppath, datetime.datetime.now().strftime("%Y%m%d_recovery.log"))
			if self.f:
				if self.f.name != filename:
					self.f.close()
					self.f = open(filename, "a", 1)
			else:
				self.f = open(filename, "a", 1)
			for oldline in self.buffer:
				self.f.write(oldline)
			self.buffer = []
			self.f.close()
			self.f = None

	def send(self):
		"""
		Sends loglines - and decides if they are sent via socket or to a tempfile.
		"""
		try:
			for line in self.readlines():
				if self.s:
					self.send_socket(line)
				else:
					self.send_tempfile(line)
			if self.s:
				self.s.close()
		except Exception, exc:
			if self.buffer:
				self.flush_buffer()
			raise

	def sighandler(self, signum, frame):
		"""
		Signal handler which specifies what to do if someone wants to quit, term or interrupt us. (If someone wants to kill us, we can't react...)
		"""
		self.flush_buffer()
		if signum in (signal.SIGQUIT, signal.SIGTERM, signal.SIGINT):
			sys.exit(0)


def main(args=None):
	import optparse
	p = optparse.OptionParser(usage="usage: %prog ip port [options]")
	p.add_option("-b", "--buffertime", dest="buffertime", type="int", action="store", help="Time in seconds for which log entries are buffered, default=0. Set to 0 to disable buffering; for buffering it should be set to at least 10.", default=0)
	p.add_option("-p", "--backuppath", dest="backuppath", type="string", action="store", help="Directory where recovery logs should be stored if the network connection dies", default=None)
	(options, args) = p.parse_args()
	if len(args) != 2 or intify(args[1], None) is None or options.buffertime == 0 or options.backuppath is None:
		p.print_usage(sys.stderr)
		sys.stderr.write("%s: Please specify ip, port, a buffertime and a path for local backups!\n" % p.get_prog_name()) # required options... not so nice but necessary
		sys.stderr.flush()
		return 1
	S = Sender(args[0], intify(args[1], None), intify(options.buffertime, 0), options.backuppath, sys.stdin, p.get_prog_name())
	S.send()


if __name__ == "__main__":
	sys.exit(main())
