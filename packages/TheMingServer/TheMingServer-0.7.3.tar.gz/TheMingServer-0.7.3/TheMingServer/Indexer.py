
# Indexer.py
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

import os

class Indexer:
	NAME = "Indexer"
	ORDER = "_order"
	MENU_BEGIN = "<ul>\n"
	MENU_END = "</ul>\n"
	
	def __init__(self, consts, lib, static, debug):
		self.consts = consts
		self.static = static
		self.lib = lib
		self.debug = debug
		self.SCRIPT = consts.CGI_NAME		
		return

	def __get_files(self, dirname):
		do_menu = 1
		lines = self.lib.get_lines(dirname+os.sep+"key")
		if (lines == []):
			lines = self.lib.get_lines(dirname+os.sep+"set.key")
			do_menu = 0
		files = self.lib.parse_key(lines)	
		if (self.debug): print "<p>"+ self.NAME+" files: "+`files`
		return files, do_menu

	#
	# __get_menu
	def __head_key(self, key):
		lines = self.lib.get_lines(key)[:2]
		file = lines[0].strip()
		title = lines[1].strip()
		return file, title

	def __add_directories(self, dirname, menu, source):
		# parent directory
		key = os.path.dirname(dirname)+os.sep+"key"
		if (os.path.isfile(key)):
			file, title = self.__head_key(key)
			if (self.static):
				link = '<li>+ <a href="../'+file+'.html">'+title+'</a>\n'
			else:
				path = dirname.replace(os.sep, "/")
				path = path.replace(source+"/", "")
				path = path.replace(os.path.basename(dirname), "")
				path = self.SCRIPT + "?page=" + path + file
				link = '<li>+ <a href="'+path+'">'+title+'</a>\n'
			menu = link + menu
		# child directories	
		dlist = os.listdir(dirname)
		dlist.sort()
		for entry in dlist:
			name = dirname+os.sep+entry
			key = name+os.sep+"key"
			if ((os.path.isdir(name)) and
				(os.path.isfile(key))):
				file, title = self.__head_key(key)
				if (self.static):
					link = '<li>- <a href="'+entry+'/'+file+'.html">'+title+'</a>\n'
				else:
					path = dirname.replace(source, "")
					path = path.replace(os.sep, "/")
					if (path != ""): path = path + "/"
					path = path.lstrip("/")
					path = self.SCRIPT + "?page=" + path + entry + "/" + file
					link = '<li>- <a href="'+path+'">'+title+'</a>\n'
				menu = menu +link
		return menu

	def __get_menu(self, files, dirname, name, source):
		menu = ""
		for entry in files[self.ORDER]:
			if (entry != name):
				if (self.static):
					link = '<li><a href="'+entry+'.html">'+files[entry][0][:-1]+'</a>'
				else:
					path = dirname.replace(os.sep, "/")
					path = path.replace(source, "")
					if (path != ""): path = path + "/"
					path = path.lstrip("/")
					path = self.SCRIPT + "?page=" + path + entry
					link = '<li><a href="'+path+'">'+files[entry][0][:-1]+'</a>'
				if (files[entry][1] != ""):
					link = link + " "+files[entry][1]
				link = link+'\n'
				menu = menu+link
		menu = self.__add_directories(dirname, menu, source)	
		menu = self.MENU_BEGIN + menu + self.MENU_END
		if (self.debug): print "<p>"+ self.NAME+" menu:\n"+menu
		return menu
	# end get_menu
	#

	def index(self, dirname, name, source):
		if (self.debug): print "<p>"+ self.NAME+" dirname: "+dirname
		try:
			files, do_menu = self.__get_files(dirname)
			if (do_menu):
				menu = self.__get_menu(files, dirname, name, source)
				if "href" not in menu: menu = ""
			else:
				menu = ""
		except:
			if (self.debug): raise
			files = menu = None
		return files, menu
