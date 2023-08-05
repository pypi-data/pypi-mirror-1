
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
	BOM_UTF8 = "\xef\xbb\xbf"
	BOM_UTF16_LE = "\xff\xfe"
	BOM_UTF16_BE = "\xfe\xff"

	def _lock_nix(self, mode, fd, block):
		if not block:
			mode |= fcntl.LOCK_NB
		fcntl.lockf(fd, mode)

	def _lock_win(self, fd, block):
		MODE = block and msvcrt.LK_LOCK or msvcrt.LK_NBLCK
		msvcrt.locking(fd, MODE, 1)

	def _lock_sh(self, *args):
		"apply a shared lock"
		self._lock_nix(fcntl.LOCK_SH, *args)

	def _lock_ex(self, *args):
		"apply an exclusive lock"
		self._lock_nix(fcntl.LOCK_EX, *args)

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
			lines = self.get_lines(file, lock=True)
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

	def get_lines(self, *args, **kwargs):
		"""
		quiet version of read_lines: if the operation fails,
		returns an empty list
		"""
		try:
			lines = self.read_lines(*args, **kwargs)
		except Exception, exception:
			lib.prn(exception)
			lines = []
		return lines

	def read_lines(self, file, keep=False, lock=False, localized=False):
		"""
		returns a list containing the lines read from 'file'
		"""
		lib.prn("reading %s" % file, "INFO")
		if lock:
			f = self.lockopen(file, "rU", create=False)
		else:
			f = self.open(file, "rU")
		lines = f.read().splitlines(keep)
		f.close()
		if localized:
			from TheMingServer import localizer
			available_locales = localizer.parse_header(lines[0])
			if available_locales:
				file = localizer.get_resource(file, available_locales)
				return self.read_lines(file, keep, lock)
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
				f = self.open(os.sep.join((sites, dir, file)))
				list = f.read()
				f.close()
				if list.find(key) != -1:
					return list.splitlines()
			except: # handles non-e-zine subsites
				continue
		return []

	def get_plate(self, name, directory, depth=10):
		"""
		give me a file name and a starting dir, and I will walk down the
		directories tree trying to find that file. Return value: the template
		lines, or []
		"""
		if not consts.PLATES:
			directory = os.curdir
			depth = 1
		for i in range(depth):  # a depth of 10 should be enough!
			path = directory + os.sep + name
			if os.path.exists(path):
				return self.read_lines(path, localized=True)
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
		"""
		Activates printing of debug information by assigning
		a function to the self.prn placeholder. This is usually
		invoked by Debugger.__init__, but it can be called at any
		time for redirecting the output of self.prn to an arbitrary
		stream.
		"""
		def func(obj, label=None):
			if issubclass(obj.__class__, Exception):
				cls = str(obj.__class__).split(".")[-1]
				msg = str(obj) or "please check the traceback for details"
				stream.write("EXCEPTION: %s: %s\n" % (cls, msg))
			else:
				if label: stream.write(label + ": ")
				stream.write(str(obj) + "\n")
		self.prn = func
		stream.write("Content-Type: text/plain; charset=%s\n\n" % consts.CHARSET)

	def prn(self, obj, label=None):
		"""
		placeholder for the debug information printing function.
		Examples and associated output:
		prn(exception_instance) --> 'EXCEPTION: [class]: [message]'
		prn(object, 'WARNING')  --> 'WARNING:' + str(object)
		prn(object)             -->  str(object)
		"""
		pass

	def set_files(self, list):
		"""
		make sure strings in list are in FILES
		"""
		f = self.lockopen(consts.FILES, "r+U")
		fnames = f.read().splitlines()
		addlist = []
		for entry in filter(None, list):
			if entry not in fnames:
				f.write(entry + "\n")
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
		pieces = line.split(sep)
		return filter(None, map(str.strip, pieces))

	def write_data(self, dict, fname):
		f = self.lockopen(fname, "w")
		size = 0
		for key, value in dict.items():
			for subkey, subvalue in value.items():
				f.write(subkey + "|" + subvalue + "\n")
			f.write("---\n")
			size += int(value["sum"])
			if size > consts.FILE_MAX: break
		f.close()

	def open(self, fname, *args):
		"""open() wrapper: if the file is opened for reading, we look
		for a possible BOM and (if we do find one) print some headache-saving
		info about it, moving to the beginning of the file's actual content
		"""
		f = open(fname, *args)
		if hasattr(f, "read"):
			bytes = f.read(2)
			if bytes in (self.BOM_UTF16_LE, self.BOM_UTF16_BE):
				self.prn("%s appears to be utf-16 encoded: only ASCII compatible formats are supported!" % fname, "ERROR")
				raise IOError, (42, os.strerror(42), bytes)
			elif (bytes + f.read(1)) == self.BOM_UTF8:
				self.prn("%s appears to be utf-8 encoded" % fname, "INFO")
			else:
				f.seek(0)
		return f

	def lockopen(self, fname, mode="r", create=True, block=False, retries=3, shared=-1):
		"""
		opens a file and applies a lock to it. By default, the lock
		will be a shared one if the file is opened for reading ONLY; exclusive
		in all other cases. This behaviour can be overridden by setting the 'shared'
		parameter to the correct boolean value. NOTES:
		- 'mode' must be a string following the same rules valid for the built-in
		  'file' function... but: append mode is not recognized, and the 'b' flag
		  has no effect (files are automatically opened in binary mode);
		- locking is *advisory* on Unix, mandatory on Windows;
		- on Windows, the lock will always be strictly exclusive.
		  "Strictly" means that the current process will not be able to map
		  another file descriptor to the locked file (and use it) until this
		  gets unlocked.
		"""
		if mode[0] not in ("r", "w"):
			raise ValueError, "invalid mode " + mode
		EX = True
		if mode.find("+") != -1:
			FLAGS = os.O_RDWR
		elif mode[0] == "w":
			FLAGS = os.O_WRONLY
		else:
			FLAGS = os.O_RDONLY
			EX = False
		if create:	FLAGS |= os.O_CREAT
		FLAGS |= getattr(os, "O_BINARY", 0)
		fd = os.open(fname, FLAGS)
		if EX == shared: EX ^= 1
		lock = EX and self._lock_ex or self._lock_sh
		for i in range(retries):
			try:
				lock(fd, block)
				fobj = os.fdopen(fd, mode)
				if mode[0] == "w": fobj.truncate()
				return fobj
			except Exception, instance:
				self.prn(instance)
				time.sleep(.01)
		else:
			raise IOError, "cannot lock and open " + fname

#-------------------------------------------------------------------------

if os.name == "nt":
	import msvcrt, sys
	Lib3._lock_sh = Lib3._lock_ex = Lib3._lock_win
	msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
else:
	import fcntl

lib = Lib3()
