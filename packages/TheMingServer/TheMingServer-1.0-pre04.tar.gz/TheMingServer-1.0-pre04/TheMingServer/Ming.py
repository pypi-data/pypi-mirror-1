
# Ming.py is part of The Ming Server
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
from TheMingServer import *

lib.prn(__name__, "init")

class Ming:

	def __init__(self):
		if not os.path.exists(consts.FILES_DIR):
			lib.prn("the directory '%s' does not exist: creating it" % \
					consts.FILES_DIR, "WARNING")
			os.makedirs(consts.FILES_DIR)
			os.chmod(consts.FILES_DIR, 0777)
		os.chdir(consts.DATA)

	def __log(self):
		l = Logger()
		l.run()

	def __make_page(self, page):
		#os.chdir(consts.DATA)
		pm = PageMaker()
		if page in ("prepal", "postpal"):
			getattr(pm, page)()
		else:
			pm.make(page.replace("/", os.sep))

	def __incoming(self):
		file = form["file"].value
		files = lib.get_lines(consts.FILES, 0, lock=True)
		if file not in files:
			raise exceptions.ForbiddenError, "You do not have write-access to that file."
		file = consts.FILES_DIR + os.sep + file
		handler = Incoming()
		handler.store(form, file)
		self.__make_page(form["page"].value)

	def __blog(self):
		if "type" in form.keys():
			if form["type"].value == "ByTitle":
				from TheMingBlogger import ByTitle
				obj = ByTitle.ByTitle()
			elif form["type"].value == "ByCategory":
				from TheMingBlogger import ByCategory
				obj = ByCategory.ByCategory()
			if form["type"].value == "ByDate":
				from TheMingBlogger import ByDate
				obj = ByDate.ByDate()
			obj.print_page()

		else:
			from TheMingBlogger import LibBlog
			self.lb = LibBlog.LibBlog(form)
			try:
				dir = self.lb.get_dir()
			except:
				raise exceptions.NotFoundError
			author, email, title, tagline = self.lb.get_text(dir)
			intro = self.lb.get_lines(dir,"intro")
			footer = self.lb.get_lines(dir,"footer")
			links = self.lb.get_lines(dir,"links")
			content = self.lb.content(dir, author, email)
			page = self.lb.do_page(dir, title, tagline, intro, footer, links, content)
			self.lb.give_headers()
			print page

	def start(self):
		lib.prn("\n--------------- SERVER STARTED ---------------\n")
		if "log" in form.keys():
			self.__log()
		elif "blog" in form.keys():
			self.__blog()
		elif "incoming" in form.keys():
			self.__incoming()
		elif "business" in form.keys(): # postpal
			self.__make_page("postpal")
		elif "type" in form.keys():	# prepal
			self.__make_page("prepal")
		elif "page" in form.keys():	# normal page
			self.__make_page(form["page"].value)
		else:
			raise exceptions.NotFoundError
