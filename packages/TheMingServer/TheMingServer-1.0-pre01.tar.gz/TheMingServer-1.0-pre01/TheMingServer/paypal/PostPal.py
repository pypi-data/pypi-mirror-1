
# PostPal.py is part of The Ming Mods
# billy-bob@billy-bob-ming.com

# Copyright (C) 2005, 2006  Richard Harris, Marco Rimoldi
# Released under the GNU General Public License
# (See the included COPYING file)

# The Ming Mods are free software; you can redistribute them and/or
# modify them under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# The Ming Mods are distributed in the hope that they will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with The Ming Mods; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os, time
from TheMingServer import consts, lib, form

class PostPal:
	NAME = "PostPal"
	LOG = "paid.log"
	INVALID = [
		"""<h3>Validation Error</h3>
		If your purchase is a valid one,
		email us your PayPal receipt and
		we will email you the page you have
		requested.
		<p>Our email: %s </p>""" % consts.EMAIL
		]

	def __init__(self):
		module = form["custom"].value + "PostPal"
		exec "from %s import %s as ppclass" % (module, module)
		self.maker = ppclass()

	def __form_is_good(self):
		# sale must be complete on PayPal
		if form["payment_status"].value != "Completed": return 0
		# return from PayPal within SPAN time-span if USE_SPAN
		if consts.USE_SPAN:
			then = form["item_number"].value
			then = int(then, 16)
			now = int(time.time())
			if (then + consts.SPAN*60) > now:
				return 0
		return 1

	def __parse_item(self, item):
		item = item.replace(" by ","|")
		tokens = item.split("|")
		return tokens[0], tokens[1]

	def __log_paid(self):
		item = form["item_name"].value
		path = consts.FILES_DIR + os.sep + self.LOG
		lines = lib.get_lines(path)
		f = open(path, "wb")
		found = 0
		for line in lines:
			tmp = line
			if tmp.startswith(item):
				tokens = line.split("|")
				count = int(tokens[1]) + 1
				tmp = tokens[0] + "|" + `count` + "\n"
				found = 1
			f.write(tmp + "\n")
		if not found:
			f.write(item + "|1\n")
		f.close()

	def deliver(self):
		if self.__form_is_good():
			if consts.TITHE:
				self.__log_paid()
			page = self.maker.make_page()
			return page
		else:
			return self.INVALID