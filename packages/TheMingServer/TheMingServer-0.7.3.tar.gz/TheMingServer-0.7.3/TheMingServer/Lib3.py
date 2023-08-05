
# Lib3.py
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

import time
import Constants

class Lib3:
	NAME = "Lib3"
	CONTENT = "content"
	ORDER = "_order"

	def __init__(self, debug):
		self.debug = debug
		c = Constants.Constants()
		self.DATA = c.DATA				# for DirectSets
		self.FILES = c.FILES
		self.FILE_MAX = c.FILE_MAX
		return

	def date_stamp(self):
		tmp = time.ctime(time.time())
		tokens = self.tokens(tmp)
		year = tokens[-1][-2:]
		stamp = " ".join([tokens[2],tokens[1],year])
		return stamp

	def form_token(self, t=None):
		if not t: t = time.time()
		return hex(abs(hash(t)))[2:]

	def get_dict(self, file, key="stamp"):
		i = 0
		file_dict = {}
		try:
			lines = self.get_lines(file)
			length = len(lines)
			while (i < length):
				entry = {}
				while (lines[i] != "---\n"):
					if ("|" not in lines[i]):
						entry[last] = entry[last] + "\n" + lines[i].strip()
					else:
						tokens = lines[i].split("|")
						entry[tokens[0]] = tokens[1].strip()
						last = tokens[0]
					i += 1
				file_dict[entry[key]] = entry
				i += 1
		except:
			try:
				file_dict[entry[key]] = entry
			except:
				pass
		return file_dict

	def get_lines(self, file, keep=True):
		"""
		returns f.readlines on file
		"""
		try:
			f = open(file)
			lines = f.read().splitlines(keep)
			f.close()
		except:
			lines = []
		return lines

	def get_subsite_file(self, key, file, data):
		"""
		searches all subsite name files to find the one
		with key
		"""
		import os
		sites = data+os.sep+"sites"
		dirs = os.listdir(sites)
		for dir in dirs:
			try:
				f = open(sites+os.sep+dir+os.sep+file)
				list = f.read()
				f.close()
				if key in list:
					return list.splitlines()
			except: # handles non-e-zine subsites
				continue
		return []

	def get_tag(self, line):
		tag = self.tokens(line,">")[0]
		tag = tag.replace("<!--", "")
		tag = tag.replace("--", "")
		return tag

	def get_types(self, file, site):
		"""
		get subsite's submission_types
		"""
		lines = self.get_lines(file)
		types = []
		for line in lines:
			line = line.strip()
			if line:
				tokens = self.tokens(line,"|")
				types.append( (tokens[0], site+"."+tokens[1]) )
		return types

	def insert_tags(self, lines, pairs):
		pairs["stamp"] = self.date_stamp()+"\n"
		newlns = []
		out = 1
		pending = ""
		for line in lines:
			if (out):
				newlns.append(line)
			if (line.find("<!--") == 0):
				key = self.get_tag(line)
				if (key in pairs.keys()):
					data = "".join(pairs[key])
					newlns.append(data)
					if (key != "title"):
						pending = key
						out = 0
				elif (key == pending+" end"):
					newlns.append(line)
					out = 1
		return newlns

	def parse_data(self, data, parsed_data, pre=0):
		key = ""
		defn = []
		for line in data:
			if (line.find("<!") == 0):
				if (key != ""):
					if (pre): defn = ["<pre>\n"]+defn+["</pre>\n"]
					parsed_data[key] = defn
				line = 	self.get_tag(line)
				key = line
				defn = []
			else:
				defn.append(line)
		if (key != ""):
			if (pre): defn = ["<pre>\n"]+defn+["</pre>\n"]
			parsed_data[key] = defn
		elif (defn != ""):
			if (pre): defn = ["<pre>\n"]+defn+["</pre>\n"]
			parsed_data[self.CONTENT] = defn
		return parsed_data

	def parse_key(self, lines):
		while (lines[-1].strip() == ""):
			lines = lines[:-1]
		files = {}
		order = []
		fname = title = desc = ""
		for line in lines:
			line = line.strip()
			if (line == ""):
				files[fname] = (title, "".join(desc))
				order.append(fname)
				fname = title = desc = ""
			elif (fname == ""):
				fname = line
			elif (title == ""):
				title = line+"\n"		# XXX make newln go away
			else:
				desc = desc+" "+line
		if (fname != ""):
			files[fname] = (title, "".join(desc))
			order.append(fname)
		files[self.ORDER] = order
		return files

	def prn(self, label, msg=""):
		"""
		let's you easily print objects in debug mode
		"""
		if self.debug:
			print "<p>::"+label+":: "
			print msg
		return

	def set_files(self, list):
		"""
		make sure strings in list are in 3.files
		"""
		try:
			f = open(self.FILES)
			files = f.read()
			f.close()
			files = files.split("\n")
		except:
			files = []
		changed = 0
		for entry in list:
			if (entry not in files):
				changed = 1
				files.append(entry)
		if (changed):
			f = open(self.FILES,'w')
			for file in files:
				if (file != ""):
					f.write(file+"\n")
			f.close()
		return

	def strip_html(self, line):
		length = len(line)
		newln = []
		tag = 0
		i = 0
		while (i < length):
			if (line[i] == '<'):
				tag = 1
			if not (tag):
				newln.append(line[i])
			if (line[i] == '>'):
				tag = 0
				newln.append(" ")
			i = i + 1
		newln = "".join(newln).strip()
		next = ""
		while (newln != next):
			next = newln
			newln = newln.replace("  ", " ")
		return newln

	def time_stamp(self):
		return time.ctime()

	def tokens(self, line, sep=" "):
		tokens = []
		line = line.strip()
		if (line != ""):
			tmp = line.split(sep)
			for entry in tmp:
				if (entry != ""):
					tokens.append(entry)
		return tokens

	def write_data(self, dict, file):
		f = open(file,'w')
		size = 0
		keys = dict.keys()
		for key in keys:
			d = dict[key]
			ks = d.keys()
			for k in ks:
				f.write(k+"|"+d[k]+"\n")
			f.write("---\n")
			size += int(d["sum"])
			if (size > self.FILE_MAX): break
		f.close()
		return
