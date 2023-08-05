
# GZWriter.py
# billy_bob_ming@yahoo.com

# Copyright (C) 2005 by Richard Harris
# Released under the GNU General Public License
# (See the included COPYING file)

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

# Hack History
# Compression code taken from cgi_buffer.py
# Written by Mark Nottingham (c) 2000

import sys, cStringIO, gzip, time

class GZWriter:
	NAME = "GZWriter"

	def __init__(self, debug, header):
		self.debug = debug
		self.header = header
		return

	def write(self, page):
		i = "\n".join(page)

		# Headers
		print "Content-Type: text/html"
		if "x-gzip" in self.header:
			print "Content-Encoding: x-gzip"
		elif "gzip" in self.header:
			print "Content-Encoding: gzip"
		print
		
		# Body
		tmptime = time.time
		time.time = lambda a=None:0
		sb = cStringIO.StringIO()
		gb = gzip.GzipFile(mode='wb', fileobj=sb, compresslevel=2)
		gb.write(i)
		gb.close()
		time.time = tmptime
		sb.seek(0)
		o = sb.read()
		sb.close()
		sys.stdout.write(o)

