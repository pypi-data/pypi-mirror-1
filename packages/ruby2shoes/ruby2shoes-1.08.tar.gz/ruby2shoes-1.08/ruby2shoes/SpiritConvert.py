
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

import os, string, shutil, time, sys

class SpiritConvert:
	NAME = "SpiritConvert"
	TEXS = [
		"normal",
		"paperback",
		]
	PROMPT = "Use which PDF template: "
	
	def __init__(self, debug, lib, consts):
		self.debug = debug
		self.lib = lib
		self.TEMP = consts.TEMP
		self.ROOT = consts.ROOT
		self.RUBY2DIR = self.ROOT+os.sep+"user"+os.sep+"headers"
		return

	def which(self, files):
		if len(files) > 1:
			file = files[self.lib.choose(files, "Print which file: ")]
		else:
			file = files[0]
		return file

	def __prep(self, files):
		name = self.which(files)
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

	def ps(self, files, pdf=0):
		name = self.__prep(files)
		##	latex = self.TEXS[self.lib.choose(self.TEXS, self.PROMPT)]
		latex = "normal"
		f = open(name)
		line = f.readline()
		f.close()
		type = string.replace(string.strip(line),"*","")
		shutil.copy(self.RUBY2DIR+os.sep+"header."+type, self.TEMP)
		import ruby2latex
		r = ruby2latex.ruby2latex()
		r.convert(name)
		base = string.split(name,".")[0]
		#convert tex to dvi
		os.system("latex "+base+".tex")
		#convert dvi to ps
		if (latex == "paperback"):
			os.system("dvips -T 5.0in,8.0in -o "+base+".ps "+base+".dvi")
		else:	
			os.system("dvips -o "+base+".ps "+base+".dvi")
		print "converted "+name+" to "+base+".ps"
		#convert ps to pdf	
		if pdf:	
			os.system("ps2pdf "+base+".ps")
			print "converted "+name+" to "+latex+" pdf" 

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
				self.ps(files)
			elif (op == "d"):
				self.ps(files, 1)
		except SystemExit:
			pass
		except:
			self.lib.exc(self.NAME, 1)
		return
	
