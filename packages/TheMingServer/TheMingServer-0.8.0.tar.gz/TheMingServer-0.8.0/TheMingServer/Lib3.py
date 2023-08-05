
# Lib3.py is part of The Ming Server
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

import os, time
from TheMingServer import consts

class Lib3:
	NAME = "Lib3"
	CONTENT = "content"
	ORDER = "_order"

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
			while i < length:
				entry = {}
				while lines[i] != "---\n":
					if "|" not in lines[i]:
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

	def get_lines(self, file, keep=False):
		"""
		returns f.readlines on file
		"""
		try:
			f = open(file, "rU")
			lines = f.read().splitlines(keep)
			f.close()
		except:
			self.prn("the file '%s' is inaccessible" % file, "WARNING")
			lines = []
		return lines

	def get_subsite_file(self, key, file, data):
		"""
		searches all subsite name files to find the one
		with key
		"""
		sites = data + os.sep + "sites"
		dirs = os.listdir(sites)
		for dir in dirs:
			try:
				f = open(os.sep.join((sites, dir, file)), "r")
				list = f.read()
				f.close()
				if list.find(key) != -1:
					return list.splitlines()
			except: # handles non-e-zine subsites
				continue
		return []

	def get_plate(self, name, directory, depth=10):
		"""Give me a file name and a starting dir, and I will walk down the directories
tree trying to find that file. Return value: the template lines, or None.
"""
		if not consts.PLATES:
			directory = os.curdir
			depth = 1
		for i in range(depth):  # a depth of 10 should be enough!
			path = directory + os.sep + name
			if os.path.exists(path):
				self.prn("loading template from '%s'" % path, "INFO")
				return self.get_lines(path)
			directory = os.path.dirname(directory) or os.curdir
		self.prn("can't find a template named '%s'" % name, "WARNING")
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

	def insert_tags(self, template, tags):
		tags["stamp"] = self.date_stamp()
		output = []
		outside = 1
		pending = ""
		for line in template:
			if outside:
				output.append(line)
			if line.startswith("<!--"):
				key = self.get_tag(line)
				if key in tags.keys():
					if isinstance(tags[key], str):
						output.append(tags[key])
					else:
						output.extend(tags[key])
					if key != "title":
						pending = key
						outside = 0
				elif key == pending + " end":
					output.append(line)
					outside = 1
		return "\n".join(output)

	def parse_data(self, data, parsed_data, pre=0):
		key = ""
		defn = []
		for line in data:
			if line.startswith("<!") and line.find("end-->") == -1:
				if key:
					if pre: defn = ["<pre>\n"] + defn + ["</pre>\n"]
					parsed_data[key] = defn
				line = 	self.get_tag(line)
				key = line
				defn = []
			else:
				defn.append(line)
		if (key != ""):
			if pre: defn = ["<pre>\n"] + defn + ["</pre>\n"]
			parsed_data[key] = defn
		elif defn:
			if pre: defn = ["<pre>\n"] + defn + ["</pre>\n"]
			parsed_data[self.CONTENT] = defn
		return parsed_data

	def parse_key(self, lines):
		while not lines[-1].strip():
			lines = lines[:-1]
		files = {}
		order = []
		fname = title = desc = ""
		for line in lines:
			line = line.strip()
			if not line:
				files[fname] = (title, "".join(desc))
				order.append(fname)
				fname = title = desc = ""
			elif not fname:
				fname = line
			elif not title:
				title = line
			else:
				desc = desc+" "+line
		if fname:
			files[fname] = (title, "".join(desc))
			order.append(fname)
		files[self.ORDER] = order
		return files

	def enable_printing(self, stream):
		def func(msg, label=None):
			if label: stream.write(label + ": ")
			stream.write(str(msg) + "\n")
		self.prn = func
		stream.write("Content-Type: text/plain\n\n")

	def prn(self, msg, label=None):
		pass

	def set_files(self, list):
		"""
		make sure strings in list are in 3.files
		"""
		files = self.get_lines(consts.FILES, 0)
		changed = 0
		for entry in list:
			if entry not in files:
				changed = 1
				files.append(entry)
		if changed:
			f = open(consts.FILES, "wb")
			for file in files:
				if (file != ""):
					f.write(file+"\n")
			f.close()

	def strip_html(self, line):
		length = len(line)
		newln = []
		tag = 0
		i = 0
		while i < length:
			if line[i] == '<':
				tag = 1
			if not (tag):
				newln.append(line[i])
			if line[i] == '>':
				tag = 0
				newln.append(" ")
			i = i + 1
		newln = "".join(newln).strip()
		next = ""
		while newln != next:
			next = newln
			newln = newln.replace("  ", " ")
		return newln

	def time_stamp(self):
		return time.ctime()

	def tokens(self, line, sep=" "):
		tokens = []
		line = line.strip()
		if line:
			tmp = line.split(sep)
			for entry in tmp:
				if entry:
					tokens.append(entry)
		return tokens

	def write_data(self, dict, file):
		f = open(file, "wb")
		size = 0
		keys = dict.keys()
		for key in keys:
			d = dict[key]
			ks = d.keys()
			for k in ks:
				f.write(k+"|"+d[k]+"\n")
			f.write("---\n")
			size += int(d["sum"])
			if size > consts.FILE_MAX: break
		f.close()
		return

#-------------------------------------------------------------------------
lib = Lib3()