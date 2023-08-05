# __init__ for The Ming Server package

import cgi
form = cgi.FieldStorage()

from Constants import consts
from Lib3 import lib
from ErrorHandler import exceptions

try:
	debug = consts.DEBUG
except:
	try:
		debug = int(form["debug"].value)
	except:
		debug = 0

if debug:
	from Debugger import debugger

from Localizer import localizer

from Indexer import Indexer          # ^
from Logger import Logger            # |
from Incoming import Incoming        # |  module
from PageMaker import PageMaker      # |  can import class...
from Ming import Ming				 # |

__all__ = ["Logger", "Incoming", "PageMaker", "localizer", "form", "consts", "lib", "exceptions"]
