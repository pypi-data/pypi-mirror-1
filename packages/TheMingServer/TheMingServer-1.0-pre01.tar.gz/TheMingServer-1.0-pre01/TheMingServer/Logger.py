
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

import os, cPickle, time
from TheMingServer import consts, form, lib, exceptions

lib.prn(__name__, "init")

class Logger:
	LOG = consts.LOG_DIR+os.sep+"ming.log"
	HDR = '''
<?xml version="1.0" encoding="%(charset)s"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html;charset=%(charset)s" />
    <title>The Ming Server Log</title>
    <style type="text/css">
      body {text-align: center}
      table {margin: 2px auto}
      th, td {padding: 2px 4px; text-align: center}
	  td  {text-align: left}
      td.r {text-align: right}
    </style>
  </head>
  <body>
    <h3>The Ming Server Log</h3>
    <hr />''' % {'charset': consts.CHARSET}

	def __init__(self):
		if not os.path.isdir(consts.LOG_DIR):
			try:
				os.mkdir(consts.LOG_DIR)
			except:
				raise exceptions.ServerError, "Cannot create log directory."

	def __authenticate(self):
		try:
			if form["pass"].value != consts.LOG_PASSWD:
				raise Exception
		except:
			raise exceptions.ForbiddenError, \
				"You do not have permission to perform this action."

	#------------------------------------------

	def __read(self, fileobj):
		fileobj.seek(0)
		try:
			dict = cPickle.load(fileobj)
		except:
			lib.prn("the log file is empty", "INFO")
			dict = {}
		if "time" not in dict.keys(): # log not yet viewed
			dict["time"] = 0
		return dict

	def __write(self, dict, fileobj):
		lib.prn("updating log file", "INFO")
		try:
			fileobj.seek(0)
			cPickle.dump(dict, fileobj, 1)
			fileobj.truncate()
		except:
			raise exceptions.ServerError, "The log file cannot be updated."

	#------------------------------------------

	def __view(self, dict):
		print consts.HDR_CONTENT_TYPE
		print self.HDR
		if len(dict) <= 1:
			print "<h4>No Data In Log</h4>"
		else:
			print "<p>Current Time:	%s </p>" % time.asctime(time.localtime(self.now))
			then = dict["time"]
			if then:
				print "<p>Last Reset: %s </p>" % time.asctime(time.localtime(then))
			print '<hr />\n<table border="1">'
			print '<tr> <th>New Hits</th> <th>Total </th> <th>Page Name </th> </tr>'

			keys = dict.keys()
			keys.sort()
			changed = 0					
			for key in keys:
				entry = dict[key]
				if isinstance(dict[key], list):
					if (entry[2].find("blog=") == -1): # ming server entries
						urlpath  = entry[2].replace(os.sep, "/")
						if (not os.path.isfile(consts.DATA+os.sep+urlpath)): # autoclean of log
							del dict[key]
						else:
							total = entry[0]
							diff  = total - entry[1]
							if ((diff > 0) or ("all" in form.keys())):
								changed = 1
								print '<tr><td class="r">%d</td> <td class="r">%d</td> <td> \
								<a href="%s?page=%s">%s</a></td> </tr>'\
								% (diff, total, consts.CGI_NAME, urlpath, key)
					else:					# blog server entries
						tmp = entry[2].split("&")
						blog = tmp[0].split("=")[1]
						article = tmp[1].split("=")[1]
						urlpath = "blogs"+os.sep+blog+os.sep+"entries"+os.sep+article
						# XXX shouldn't assume self.DATA in next line
						if (not os.path.isfile(consts.DATA+os.sep+urlpath)): # autoclean of log
							del dict[key]
						else:
							total = entry[0]
							diff  = total - entry[1]
							if ((diff > 0) or ("all" in form.keys())):
								changed = 1
								print '<tr><td class="r">%d</td> <td class="r">%d</td> <td> \
								<a href="%s?%s">%s</a></td> </tr>'\
								% (diff, total, consts.CGI_NAME, entry[2], key)

			if (changed == 0) and ("all" not in form.keys()):
				print '<tr><td class="r">n/a</td><td class="r">n/a</td><td>No New Hits</td><tr>'
			print "</table>"
		print "</body>\n</html>"
		#
		# reset log
		last = 0
		dict["time"] = self.now
		for key in dict.keys():
			if isinstance(dict[key], list):
				dict[key][1] = dict[key][0]

	#
	#  Public methods
	#

	def log_entry(self, entry, path):
		if path.find(consts.PRIVATE) != -1:
			return
		file = lib.lockopen(self.LOG, "r+")
		log = self.__read(file)
		if log.has_key(entry):
			log[entry][0] = log[entry][0] + 1
		else:
			log[entry] = [ 1, 0 , path]
		self.__write(log, file)
		file.close()

	def run(self):
		if consts.DEMO or [self.authenticate()]:
			pass

		file = lib.lockopen(self.LOG, "r+")
		log = self.__read(file)
		self.now = time.time()
		self.__view(log)
		self.__write(log, file)
		file.close()
