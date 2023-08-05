
# Indexer.py is part of The Ming Server
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

import os
from TheMingServer import consts, lib

lib.prn(__name__, "init")

class Indexer:
	NAME = "Indexer"
	ORDER = "_order"
	MENU_BEGIN = '<div id="menu">\n  <ul>'
	MENU_DOWN = '    <li class="down"><a href="%(href)s"> %(text)s </a></li>'
	MENU_SIBLING = '    <li><a href="%(href)s"> %(text)s </a> %(desc)s </li>'
	MENU_UP = '    <li class="up"><a href="%(href)s"> %(text)s </a></li>'
	MENU_END = '  </ul>\n</div>'

	def __init__(self):
		self.SCRIPT = consts.CGI_NAME

	def __get_files(self, dirname):
		do_menu = 1
		lines = lib.get_lines(dirname + os.sep + "key")
		if lines == []:
			lines = lib.get_lines(dirname + os.sep + "set.key")
			do_menu = 0
		files = lib.parse_key(lines)
		return files, do_menu

	#
	# __get_menu
	def __head_key(self, key):
		lines = lib.get_lines(key)[:2]
		file = lines[0].strip()
		title = lines[1].strip()
		return file, title

	def __add_directories(self, dirname, menu):

		def make_link(type, dirname):
			key =  dirname + "key"
			if os.path.isfile(key):
				file, title = self.__head_key(key)
				path = dirname.replace(os.sep, "/")
				href = self.SCRIPT + "?page=" + path + file
				link = type % {'href': href, 'text': title}
				return link
			return ""

		  # parent directory
		parent = os.path.dirname(dirname) + os.sep
		link = make_link(self.MENU_DOWN, parent)
		if link: menu.insert(1, link)

		  # child directories
		children = os.listdir(dirname)
		children.sort()
		for child in children:
			child = os.sep.join((dirname, child, ""))
			link = make_link(self.MENU_UP, child)
			if link: menu.append(link)

	def __get_menu(self, files, dirname, name):
		template = lib.get_plate("menu.html", dirname)
		if len(template) > 4:  # is there everything that's needed?
			self.MENU_BEGIN = template[0]
			self.MENU_DOWN = template[1]
			self.MENU_SIBLING = template[2]
			self.MENU_UP = template[3]
			self.MENU_END = template[4]
		elif template:
			lib.prn("this is not a valid menu template... using default", "WARNING")
		menu = [self.MENU_BEGIN]
		for entry in files[self.ORDER]:
			if entry != name:
				path = dirname.replace(os.sep, "/")
				if path: path += "/"
				path = self.SCRIPT + "?page=" + path + entry
				link = self.MENU_SIBLING % {'href': path,
				                            'desc': files[entry][1],
				                            'text': files[entry][0]}
				menu.append(link)
		self.__add_directories(dirname, menu)
		menu.append(self.MENU_END)
		return menu

	def index(self, dirname, name):
		lib.prn("indexing directory '%s'" % dirname, "INFO")
		files, do_menu = self.__get_files(dirname)
		if do_menu:
			menu = self.__get_menu(files, dirname, name)
		else:
			menu = []
		return files, menu