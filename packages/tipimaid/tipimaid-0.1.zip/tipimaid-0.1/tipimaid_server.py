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


import sys, socket, select

def intify(s, defaultint=0):
	"""
	Take something, convert it to int, return defaultint if bad things happen.
	"""
	try:
		return int(s)
	except ValueError, exc:
		return defaultint

def run(port=40000, netcat_compatible=False):
	"""
	Starts the server at port port. If netcat_compatible is True the server does
	not notify the sender that it received something. Thus a connection loss
	might be noticed later than when tipimaid_sender is used which is the
	recommended setup here. Actually this switch only exists for paranoid admins
	who don't speak python and don't trust tipimaid_sender (but trust netctat
	instead).
	"""
	backlog = 5
	size = 8192
	input = []
	sockets = []
	for (af, socktype, proto, canonname, sa) in socket.getaddrinfo(None, port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
		try:
			s = socket.socket(af, socktype, proto)
		except socket.error, msg:
			s = None
			continue
		try:
			s.setblocking(0)
			s.bind(sa)
			s.listen(backlog)
			sockets.append(s)
		except socket.error, msg:
			s.close()
			s = None
			continue

	input = sockets[:]
	inputs = {}

	while True:
		(inputready, outputready, exceptready) = select.select(input, [], [], 60)
		for s in inputready:
			if s in sockets:
				# handle the server sockets
				client, address = s.accept()
				input.append(client)
				inputs[client] = ""
			else:
				# handle all other sockets
				try:
					data = s.recv(size)
					if data:
						if not netcat_compatible:
							s.send("1") # notify the sender that we got something
						inputs[s] += data
						pos = inputs[s].rfind("\n")
						if pos >= 0:
							sys.stdout.write(inputs[s][:pos+1])
							sys.stdout.flush()
							inputs[s] = inputs[s][pos+1:]
					else:
						raise socket.error
				except socket.error, exc:
					s.close()
					del inputs[s]
					input.remove(s)
					continue

def main(args=None):
	import optparse
	p = optparse.OptionParser(usage="usage: %prog port")
	p.add_option("-n", "--netcat-compatible", dest="netcat", action="store_true", help="If set, %s switches to netcat-compatible mode. Otherwise %s assumes that it talks to its own sender which has better recovery in case of a broken connection.\nDo NOT use this switch if you use tipimaid_sender!" % (sys.argv[0], sys.argv[0]), default=None)
	(options, args) = p.parse_args()
	if len(args) != 1 or intify(args[0], None) is None:
		p.print_usage(sys.stderr)
		sys.stderr.flush()
		return 1
	run(port=intify(args[0], 40000), netcat_compatible=options.netcat)

if __name__ == "__main__":
	sys.exit(main())
