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


import heapq, re, sys, datetime, time

re_find_date = re.compile(" \[(.*?)\] ")


def apachedate2utc(line):
	d = re_find_date.findall(line)[0]
	temp = d.split()
	utcdate = datetime.datetime(*(time.strptime(temp[0], "%d/%b/%Y:%H:%M:%S")[0:6])) # support ancient distributions with python < 2.5
	minsoff = int("%s%s" % (temp[1][0], temp[1][-2:]))
	hrsoff = int("%s%s" % (temp[1][0], temp[1][1:3]))
	utcdate -= datetime.timedelta(hours=hrsoff, minutes=minsoff)
	return utcdate


def reallines(iter, key):
	for item in iter:
		try:
			keyitem = key(item)
		except Exception:
			sys.stderr.write("Skipping malformed line %s" % item)
			sys.stderr.flush()
		else:
			yield item


def mergesort(filelist, key):
	heap = []
	for (i, itr) in enumerate(iter(pl) for pl in filelist):
		try:
			item = itr.next()
			heap.append((key(item), i, item, itr))
		except StopIteration:
			pass
	heapq.heapify(heap)

	while heap:
		(_, idx, item, itr) = heap[0]
		yield item
		try:
			item = itr.next()
			heapq.heapreplace(heap, (key(item), idx, item, itr) )
		except StopIteration:
			heapq.heappop(heap)


openedfiles = [reallines(open(filename), apachedate2utc) for filename in sys.argv[1:]]

for line in mergesort(openedfiles, apachedate2utc):
	sys.stdout.write(line)
sys.stdout.flush()
