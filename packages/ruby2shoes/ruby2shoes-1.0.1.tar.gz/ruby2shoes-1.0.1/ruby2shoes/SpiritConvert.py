
# SpiritConvert.py::converts .sp and .fc files
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

import os, string, shutil, time

class SpiritConvert:
	NAME = "SpiritConvert"
	PRESS = ["paperback"]
	PROMPT = "Use which CafePress template: "
	
	def __init__(self, debug, lib, consts):
		self.debug = debug
		self.lib = lib
		self.TEMP = consts.TEMP
		self.ROOT = consts.ROOT
		self.RUBY2DIR = self.ROOT+os.sep+"user"+os.sep+"headers"
		return

	def __prep(self, files):
		for file in files:
			if ((string.find(file,".fc") != -1) or 
				(string.find(file,".sp") != -1)):
				name = file
				break
		shutil.copy(name, self.TEMP)
		os.chdir(self.TEMP)
		name = os.path.basename(name)
		return name

	def html(self, files):
		name = self.__prep(files)	
		import ruby2html
		r = ruby2html.ruby2html()
		r.convert(name)
		return

	def text(self, files):
		name = self.__prep(files)
		import ruby2text
		r = ruby2text.ruby2text()
		r.convert(name)
		return name

	def cafepress(self, files):
		choice = self.lib.choose(self.PRESS, self.PROMPT)
		latex = self.PRESS[choice]
		name = self.__prep(files)
		shutil.copy(self.RUBY2DIR+os.sep+"header."+latex, self.TEMP)
		import ruby2latex
		r = ruby2latex.ruby2latex()
		r.convert(name, latex)
		base = string.split(name,".")[0]
		os.system("latex "+base+".tex")
		if (latex == "paperback"):
			os.system("dvips -T 5.0in,8.0in -o "+base+".ps "+base+".dvi")
		os.system("ps2pdf14 "+base+".ps")
		print "converted "+name+" to cafepress "+self.PRESS[choice]+" pdf" 

	def service(self, params, options):
		try:
			self.lib.checkdir(self.TEMP)		
			op = options[1]
			files = self.lib.harvest(params[0])
			if (op == "h"):
				self.html(files)
			elif (op == "t"):
				self.text(files)
			elif (op == "p"):
				self.cafepress(files)
		except SystemExit:
			pass
		except:
			self.lib.exc(self.NAME, 1)
		return
	
