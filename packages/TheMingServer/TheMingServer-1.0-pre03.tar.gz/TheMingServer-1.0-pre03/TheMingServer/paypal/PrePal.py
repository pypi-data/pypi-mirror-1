
# PrePal.py is part of The Ming Mods
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

class PrePal:
	NAME = "PrePal"
	LOG = "paid.log"

	def __init__(self):
		self.TITHES = "tithes.txt"

	def __make_page(self, email):
		type = form["type"].value
		platename = type.startswith("Direct") and "direct.html" or "easy.html"
		lines = lib.get_lines(consts.DATA + os.sep + platename)
		property = form["property"].value
		author = form["author"].value
		fee = form["fee"].value
		item = hex(int(time.time()))[2:]
		for i in range(len(lines)):
			if "$" in lines[i]:
				lines[i] = lines[i].replace("$PROPERTY", property)
				lines[i] = lines[i].replace("$AUTHOR", author)
				lines[i] = lines[i].replace("$FEE", fee)
				lines[i] = lines[i].replace("$ITEM", item)
				lines[i] = lines[i].replace("$EMAIL", email)
				lines[i] = lines[i].replace("$TYPE", type)
				lines[i] = lines[i].replace("$SERVER", consts.SERVER + consts.CGI_NAME)
				lines[i] = lines[i].replace("$SITE_EMAIL", consts.EMAIL)
		return "\n".join(lines)

	def __get_site(self):
		property = form["property"].value
		lines = lib.get_subsite_file(property, "property_list", consts.DATA)
		lib.prn(lines)
		for line in lines:
			if line.startswith(property):
				line = line.strip()
				path = line.split("=")[1]
				break
		tokens = path.split("/")   #XXX
		return tokens[1]

	def __tithe(self):
		property = form["property"].value
		tithe = 0
		lines = lib.get_lines(consts.LOG_DIR+os.sep+self.LOG)
		for i in range(len(lines)):
			if lines[i].startswith(property):
				tokens = lines[i].strip().split("|")
				tithe = int(tokens[1]) % 10
				break
		site = self.__get_site()
		lines = lib.get_lines(consts.DATA+os.sep+"sites"+os.sep+site+os.sep+self.TITHES)
		if tithe > (len(lines)-1):
			email = form["email"].value
		else:
			tmp = lines[tithe].strip()
			tokens = tmp.split("|")
			email = tokens[0]
		return email

	def decision_page(self):
		if consts.TITHE:
			email = self.__tithe()
		else:
			email = form["email"].value
		lines = self.__make_page(email)
		return lines