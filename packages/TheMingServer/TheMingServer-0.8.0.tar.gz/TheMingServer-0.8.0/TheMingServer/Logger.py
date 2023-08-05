
# Logger.py is part of The Ming Server
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

import os, pickle, time
from TheMingServer import consts, form, lib, exceptions

lib.prn(__name__, "init")

class Logger:
	RETRIES = 2
	LOG = consts.LOG_DIR + os.sep + "ming.log"

	def __get_log(self):
		try:
			f = open(self.LOG)
			dict = pickle.load(f)
			f.close()
			if "time" not in dict.keys(): # log not yet viewed
				dict["time"] = 0
		except:
			dict = {}
		return dict

	def __reset(self, dict):
		if "days" in form.keys():
			days = int(form["days"].value)
		else:
			days = 0
		then = dict["time"]
		if self.now > (then + ((days*24)-2)*60*60):
			last = 0
			dict["time"] = self.now
			for key in dict.keys():
				if isinstance(dict[key], list):
					diff  = dict[key][0] - dict[key][1]
					last += diff
					dict[key][1] = dict[key][0]
			dict["last"] = last

	def __view(self, dict):
		new = 0
		self.__write_hdr()
		keys = dict.keys()
		keys.sort()
		if len(keys) <= 1:
			print "<h4>No Data In Log</h4>"
		else:
			then = dict["time"]
			print "<p>Current Time:	%s </p>" % time.asctime(time.localtime(self.now))
			if then:
				print "<p>Last Reset: %s </p>" % time.asctime(time.localtime(then))
			print '<hr />\n<table border="1">'
			print '<tr> <th>New Hits</th> <th>Total </th> <th>Page Name </th> </tr>'
			for key in keys:
				if isinstance(dict[key], list):
					path  = dict[key][-1]
					if (not os.path.isfile(consts.DATA + os.sep + path) or
						(path.find(consts.PRIVATE) != -1) ):
						del dict[key]
					else:
						total = dict[key][0]
						diff  = dict[key][0] -	dict[key][1]
						print '<tr><td class="r">%d</td> <td class="r">%d</td> <td> \
<a href="%s?page=%s">%s</a></td> </tr>' % (diff, total, consts.CGI_NAME, path, key)
			print "</table>"
		print "</body>\n</html>"

	def __write_hdr(self):
		print consts.HDR_CONTENT
		print '''
<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <title>The Ming Server Log</title>
    <style type="text/css">
      body {text-align: center}
      table {margin: 2px auto}
      th, td {padding: 2px 4px; text-align: center}
      td.r {text-align: right}
    </style>
  </head>
  <body>
    <h3>The Ming Server Log</h3>
    <hr />'''

	def __write(self, dict):
		lib.prn("updating log file", "INFO")
		for i in range(self.RETRIES):
			try:
				if not os.path.isdir(consts.LOG_DIR):
					os.mkdir(consts.LOG_DIR)
				f = open(self.LOG, "wb")
				pickle.dump(dict, f)
				f.close()
				return
			except:
				continue
		raise exceptions.ServerError, "The log file cannot be updated."

	#
	#  Public methods
	#

	def log_entry(self, entry, path):
		log = self.__get_log()
		if log.has_key(entry):
			log[entry][0] = log[entry][0] + 1
		else:
			log[entry] = [ 1, 0 , path]
		self.__write(log)

	def authenticate(self):
		try:
			if form["pass"].value != consts.LOG_PASSWD:
				raise Exception
		except:
			raise exceptions.ForbiddenError, \
				"You do not have permission to perform this action."

	def run(self):
		log = self.__get_log()
		original = log.copy()
		self.now = time.time()
		action = form["log"].value

		if action == "reset":
			self.authenticate()
			self.__reset(log)
		elif action == "erase":
			self.authenticate()
			item = form["item"].value
			del log[item]
		elif consts.DEMO or [self.authenticate()]:
			pass

		self.__view(log)
		if log != original:
			self.__write(log)