
# Logger.py
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

import os, pickle, sys, time

class Logger:
	NAME = "Logger"
	RETRIES = 2

	def __init__(self, consts, debug):
		self.debug = debug
		self.changed = 0
		self.retries = 0
		self.DATA = consts.DATA
		self.PRIVATE = consts.PRIVATE
		self.LOG_DIR = consts.LOG_DIR
		self.LOG = self.LOG_DIR + os.sep + "ming.log"	
		self.DEMO = consts.DEMO
		self.LOG_PASSWD = consts.LOG_PASSWD
		self.HDR = consts.HDR
		self.E403 = consts.E403
		return

	def __get_log(self):
		try:
			f = open(self.LOG)
			dict = pickle.load(f)
			f.close()
			if ("time" not in dict.keys()): # log not yet viewed
				dict["time"] = 0
		except:
			dict = {}
		return dict
		
	def __reset(self, dict, form, now):
		if ("days" in form.keys()):
			days = int(form["days"].value)
		else:
			days = 1
		then = dict["time"]	
		if (now > (then + (((days*24)-2)*60*60))):
			last = 0
			dict["time"] = now
			for key in dict.keys():
				if isinstance(dict[key], list):
					diff  = dict[key][0] - dict[key][1]
					last += diff
					dict[key][1] = dict[key][0]
			dict["last"] = last		
			self.__write_log(dict)
		return						

	def __view_log(self, dict):
		new = 0
		self.__write_hdr()
		keys = dict.keys()
		keys.sort()
		if (len(keys) <= 1):
			print "<h4>No Data In Log</h4>"
			sys.exit()
		else:	
			now = time.time()
			then = dict["time"]
			if (not then):
				then = now
			print "<p>Current Time:  "+time.asctime(time.localtime(now))
			print "<br>Last Reset: "+time.asctime(time.localtime(then))
			print "<br>&nbsp;<hr><table width=50% border=1>"
			print "<tr align=right><td>New Hits <td>Total <td align=center>Page Name"
			for key in keys:
				if isinstance(dict[key], list):
					path  = dict[key][-1]
					if ((not os.path.isfile(self.DATA+os.sep+path)) or
						(self.PRIVATE in path)):
						del dict[key]
						self.changed = 1
					else:	
						total = dict[key][0]
						diff  = dict[key][0] -  dict[key][1]
						print '''<tr align=right><td>%d <td>%d <td align=center>
						<a href="/cgi-bin/ming.cgi?page=%s">%s</a>''' % (diff, total, path, key[:-1])
		return now		

	def __write_hdr(self):
		print self.HDR
		print "<html><head>\n"
		print "<title>The Ming Server Log</title>\n"
		print "</head><body>\n"
		print "<h3 align=center>The Ming Server Log</h3>\n"
		print "<hr><center>"
		return

	def __write_log(self, dict):
		try:
			if (not (os.path.isdir(self.LOG_DIR))):
				os.mkdir(self.LOG_DIR)
			f = open(self.LOG,'w')
			pickle.dump(dict, f)
			f.flush()
			f.close()
		except:
			self.retries = self.retries + 1
			if (self.retries <= self.RETRIES):
				self.__write_log(dict)
		self.retries = 0	
		return

	#
	#  Public methods
	#

	def log_entry(self, entry, path):
		dict = self.__get_log()
		if (dict.has_key(entry)):
			dict[entry][0] = dict[entry][0]+1
		else:
			dict[entry] = [ 1, 0 , path]
		self.__write_log(dict)
		return

	def run(self, form):
		try:
			if (self.DEMO or
				(("view" in form.keys()) and (self.LOG_PASSWD == form["view"].value))):
				dict = self.__get_log()
				now = self.__view_log(dict)
				if (("view" in form.keys()) and (self.LOG_PASSWD == form["view"].value)):
					self.__reset(dict, form, now)
				if (dict["time"] == 0):
					dict["time"] = now
					self.__write_log(dict)
				elif (self.changed):
					self.__write_log(dict)
			elif ("remove" in form.keys()):
				if (self.LOG_PASSWD == form["remove"].value):
					item = form["item"].value
					dict = self.__get_log()
					del dict[item]
					self.__write_log(dict)
					self.__view_log(dict)
			else:		
				print self.HDR+self.E403
		except:
			pass
