
# Incoming.py
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

import os, time
import Lib3

class Incoming:
	NAME = "Incoming"
	
	def __init__(self, lib, consts, debug):
		self.lib = lib
		self.debug = debug
		self.INCOMING_MAX = consts.INCOMING_MAX
		return

	def store(self, form, file):
		# check incoming sizes and generate sum
		sum = 0
		new = {}
		now = time.time()
		new["stamp"] = `now`
		new["id"] = self.lib.form_token()
		for key in form.keys():
			if (key not in ["page", "file", "debug", "incoming", "submit", "params"]):
				text = "text" in key
				length = len(form[key].value)
				if (((text) and (length > self.INCOMING_MAX )) or 
					((not text) and length > 128 )):
					return "Submission contains fields which exceed acceptable size."
				new[key] = form[key].value
				sum += length
		new["sum"] = `sum`	
		# get remote_addr
		try:
			address = os.environ["REMOTE_ADDR"]
		except:
			address = `time.time()`
		new["address"] = address	
		# get old by stamp
		old = self.lib.get_dict(file)
		# check for uniqueness
		for key in old.keys():
			try:
				sum2 = old[key]["sum"]
			except:
				sum2 = `time.time()`
			try:
				address2 = old[key]["address"]
			except:
				address2 = `time.time()`
			if ((address == address2) and
				(`sum` == sum2)):
				return "Duplicate submission"
		# if unique write to file_max
		old[`now`] = new
		self.lib.write_data(old, file)
		if (old == {}):
			os.chmod(file, 0666)
		return ""
