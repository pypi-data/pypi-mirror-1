#!/usr/bin/env python

# setup.py is part of The Ming Server
# billy-bob@billy-bob-ming.com

# Copyright (C) 2005, 2006	Richard Harris, Marco Rimoldi
# Released under the GNU General Public License
# (See the included COPYING file)

# The Ming Server is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# The Ming Server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with The Ming Server; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA	 02110-1301	 USA


"""A Honking-Good Little Python Application Server

Maybe you'd like a server that gives you control of your site, that
keeps its own log, a server that serves HTML, pre-formatted text, or the
output of any Python code wrapped in a data page.  That's what The Ming
Server does.  And it is the basis for the MingMods which connect your
content to your PayPal account and for MingZine which lets you publish
other people this way and take a percentage of their direct sales.
"""

import sys, os, shutil
from distutils.cmd import Command
from distutils.core import setup
from distutils.command.install_data import install_data

NAME = "The Ming Server"
UNIX_NAME = "TheMingServer"
LICENSE = "GNU General Public License"
PLATFORMS = ["any"]
CLASSIFIERS = """
Development Status :: 4 - Beta
Environment :: Web Environment
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Intended Audience :: System Administrators
License :: OSI Approved :: GNU General Public License (GPL)
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Internet :: WWW/HTTP :: Dynamic Content
Topic :: Internet :: WWW/HTTP :: Site Management
"""

os.linesep = "\n"
get = globals().get

def walk_data(dir):
	result = []
	start = len(dir) + 1
	append = lambda foo, dir, names: result.append((dir[start:] or '.', \
					filter(os.path.isfile, [os.path.join(dir, name) for name in names])))
	os.path.walk(dir, append, None)
	return result

PACKAGES = [
		'TheMingServer.DirectSets',
		'TheMingServer.DirectSingles',
		'TheMingServer',
		'TheMingServer.makers',
		'TheMingServer.parsers',
		'TheMingServer.writers',
		'TheMingServer.paypal'
		]
PACKAGE_DATA = ('plate',)  # this won't be passed directly to setup
SCRIPTS = ['cgibin/ming.cgi']
DATA_FILES = walk_data('data')
HTDOCS = walk_data('htdocs')

class install(Command):

	prompts = (
		('lib', ("Path to cgi-bin directory where The Ming Server will be installed", 0, 1)),
		('data', ("Path to your Ming Server data tree (ie /path/to/www/data)", 1, 1)),
		('htdocs', ("Path to your web server's htdocs directory (ie /path/to/public_html)", 1, 1))
		)

	def finalize_options(self):
		self.print_header()
		if not self.has_any_option_set():
			self.ask_user()
			self.install_scripts = self.install_lib

			# here's a workaround for installing "plate"s to each package directory
			# (we would use the package_data key if it didn't require py2.4)

			abs_path = os.path.abspath(self.install_lib)
			data_files = []
			for packname in PACKAGES[:3]:
				dirname = packname.replace(".",os.sep)
				data_files.append((abs_path + os.sep + dirname, ["%s/%s" % (dirname, file) for file in PACKAGE_DATA]))
			for entry in data_files:
				dst = entry[0]
				if not os.path.isdir(dst):
					os.makedirs(dst)
				for src in entry[1]:
					shutil.copy(src, dst)
			
#=========================== the rest is constant for every package of Billy Bob's

		self.set_undefined_options('build',
								   ('build_lib', 'build_lib'))

	description = "install " + NAME

	user_options = [
		('install-lib=', None, "installation directory for Python modules"),
		('install-scripts=', None, "installation directory for Python scripts"),
		('install-data=', None, "installation directory for data files"),
		('install-htdocs=', None, "web server's htdocs directory (for static resources)"),
		('compile', 'c', "compile .py to .pyc [default]"),
		('no-compile', None, "don't compile .py files"),
		('optimize=', 'O',
		 "also compile with optimization: -O1 for \"python -O\", "
		 "-O2 for \"python -OO\", and -O0 to disable [default: -O0]"),
		('force', 'f',
		 "force installation (overwrite any existing files)")
		]

	def initialize_options(self):
		self.install_lib = None
		self.install_scripts = None
		self.install_data = None
		self.install_htdocs = None
		self.force = 0
		self.skip_build = 0
		self.build_lib = None
		self.compile = None
		self.optimize = None
		self.root = None

	def ask_user(self):
		i = 0
		for key, options in self.prompts:
			i += 1
			print "(%d)" % i,
			install_dir = self.get_dir(*options)
			setattr(self, "install_" + key, install_dir)

	def get_dir(self, prompt, optional=0, create=1):
		print "Enter %s%s:" % (prompt, optional and " (optional)" or "")
		while 1:
			try:
				install_dir = raw_input("> ").strip()
			except:
				print "\n\nInstallation interrupted by user."
				sys.exit()
			if optional and install_dir == "":
				return None
			elif os.path.exists(install_dir):
				break
			elif create:
				try:
					os.mkdir(install_dir)
					break
				except: pass
			print "Please specify a valid%s directory path%s..." % \
				(not create and " (and existing)" or "",
				 optional and ", or press Enter to skip the \ninstallation of this item" or "")
		print
		return install_dir

	def print_header(self):
		print "_" * 76
		print "\n  %s Installation Script" % NAME
		print "_" * 76
		print

	def run(self):
		commands = self.get_sub_commands()
		if commands:
			for cmd_name in commands:
				print "* installing %s..." % cmd_name[8:]
				self.run_command(cmd_name)
			print "\nInstallation completed."
		else:
			print "Nothing to do!"

	def has_lib(self):
		return self.install_lib and self.distribution.packages

	def has_scripts(self):
		return self.install_scripts and self.distribution.scripts

	def has_data(self):
		return self.install_data and self.distribution.data_files

	def has_htdocs(self):
		return self.install_htdocs and get('HTDOCS')

	def has_any_option_set(self):
		if (self.install_lib or
			self.install_data or
			self.install_scripts or
			self.install_htdocs):
			   return True
		return False

	sub_commands = [
		('install_lib',		has_lib),
		('install_scripts', has_scripts),
		('install_data',	has_data),
		('install_htdocs',	has_htdocs)
		]

class install_htdocs(install_data):

	description = "install static web resources and example files"

	def initialize_options(self):
		install_data.initialize_options(self)
		self.data_files = get('HTDOCS')

	def finalize_options (self):
		self.set_undefined_options('install',
								   ('install_htdocs', 'install_dir'),
								   ('root', 'root'),
								   ('force', 'force'),
								   )

#-------------------------------------------------------

if sys.version < '2.2.3':
	from distutils.dist import DistributionMetadata
	DistributionMetadata.classifiers = None
	DistributionMetadata.download_url = None

doclines = __doc__.splitlines()

setup(
	verbose = 0,
	cmdclass = {'install': install,
				'install_htdocs': install_htdocs},
	name = UNIX_NAME,
	version = "1.0",
	license = LICENSE,
	platforms = PLATFORMS,
	classifiers = filter(None, CLASSIFIERS.splitlines()),
	author = "Billy-Bob Ming",
	author_email = "billy-bob@billy-bob-ming.com",
	description = "A Honking-Good Little Python Application Server",
	url = "http://python.org/pypi/%s" % UNIX_NAME,
	long_description = "\n".join(doclines[2:]),
	package_dir = get('PACKAGE_DIR'),
	packages = get('PACKAGES'),
	scripts = get('SCRIPTS'),
	data_files = get('DATA_FILES')
	)
