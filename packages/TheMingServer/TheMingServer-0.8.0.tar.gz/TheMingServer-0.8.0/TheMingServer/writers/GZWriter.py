
# GZWriter.py is part of The Ming Server
# billy-bob@billy-bob-ming.com

# Copyright (C) 2005, 2006  Richard Harris, Marco Rimoldi
# Released under the GNU General Public License
# (See the included COPYING file)

# The Ming Server is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# The Ming Server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with The Ming Server; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import struct, zlib

class GZWriter:
	NAME = "GZWriter"
	COMPR_LEVEL = 2

	def __init__(self, header):
		self.header = header

	def write(self, page):
		data = "\037\213\010\000\000\000\000\000\002\377"
		html = page

		print "Content-Type: text/html"
		if "x-gzip" in self.header:
			print "Content-Encoding: x-gzip"
		elif "gzip" in self.header:
			print "Content-Encoding: gzip"
		print

		# this strips header and *adler32* checksum
		data += zlib.compress(html, self.COMPR_LEVEL)[2:-4]

		# let's append a *CRC* checksum
		crc = zlib.crc32(html)
		data += struct.pack("<l", crc)

		# 4 bytes for html length
		data += struct.pack("<L", len(html))

		print data,

		# if we want to taste the cake...
		#f = open("eatme.gz", "wb")
		#f.write(data)
		#f.close()