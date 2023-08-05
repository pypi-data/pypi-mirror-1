
# SpiritConsts.py::Constants for the Spirit Project
# ruby2shoes@users.sourceforge.net
# http://ruby2shoes.sourceforge.net

# Copyright (C) 2004 by Ruby Dos Zapatas
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

class SpiritConsts:
	DEBUG = 0

	# Expansions allow full name, ~/, or $VAR from environment
	# ie ROOT = "/home/richard/spirit", "~/spirit", or "$HOME/spirit"
	if (os.name == "posix"):
		RC   = os.path.expandvars(os.path.expanduser("~/.spiritrc"))
	else:	
		RC   = os.path.expandvars(os.path.expanduser("~/spirit.rc"))
	if (os.name == "posix"):
		TEMP = os.path.expandvars(os.path.expanduser("/tmp/spirit"))
	else:
		TEMP = os.path.expandvars(os.path.expanduser("~/spirit/tmp"))
	ROOT = os.path.expandvars(os.path.expanduser("~/spirit"))
	SAFE = os.path.expandvars(os.path.expanduser("~/archive"))

	for dir in [ TEMP, ROOT, SAFE ]:
		if not (os.path.isdir(dir)):
			os.makedirs(dir)

	MAX_ARCHIVES = 5

	def __init__(self):
		return
