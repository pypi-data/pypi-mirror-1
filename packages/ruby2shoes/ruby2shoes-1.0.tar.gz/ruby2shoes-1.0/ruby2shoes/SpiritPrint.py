
# SpiritPrint.py::Printing fc and sp files
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

import os, shutil, string

class SpiritPrint:
	NAME = "SpiritPrint"
	OVRWRT = NAME+"::Refusing to overwrite existing "
	DVI = NAME+"::First run: Spirit -pd "

	def __init__(self, debug, lib, consts):
		self.debug = debug
		self.lib = lib
		self.TEMP = consts.TEMP
		self.ROOT = consts.ROOT
		self.RUBY2DIR = self.ROOT+os.sep+"user"+os.sep+"headers"
		return

	def get_type(self, file):
		f = open(file)
		line = string.strip(f.readline())
		f.close()
		return(line[1:])

	def dvi(self, name, files):
		for file in files:
			if (((string.find(file,name+".sp") != -1) or 
				(string.find(file,name+".fc") != -1)
				) and string.find(file,"~") == -1):
				print file
				type = self.get_type(file)
				shutil.copy(file, self.TEMP)
				shutil.copy(self.RUBY2DIR+os.sep+"header."+type, self.TEMP)
				os.chdir(self.TEMP)
				file = os.path.basename(file)
				import ruby2latex
				r = ruby2latex.ruby2latex()
				r.convert(file)
				name = string.split(file,".")[0]
				file = name+".tex"
				os.system("latex " + file)
				break
		return

	def draft_dvi(self,name):	
		import ruby2text
		r = ruby2text.ruby2text()
		r.convert(name)
		name = string.split(name,".")[0]
		fname = name+".txt"
		import ruby2draftTeX
		r = ruby2draftTeX.ruby2draftTeX()
		r.convert(fname)
		import sys ; sys.exit()
		fname = name+".tex"
		os.system("tex " + fname)
		return

	def draft(self, name):
		print name
		shutil.copy(name, self.TEMP)
		os.chdir(self.TEMP)
		name = os.path.basename(name)
		self.draft_dvi(name)
		return

	def block(self, name):
		print name
		shutil.copy(name, self.TEMP)
		os.chdir(self.TEMP)
		name = os.path.basename(name)
		f = open(name)
		lines = f.readlines()
		f.close()
		f = open(name,'w')
		i = 0
		while (string.find(lines[i],"PRINT BLOCK BEGIN") == -1):
			i = i + 1
		while (string.find(lines[i],"PRINT BLOCK END") == -1):
			f.write(lines[i])
			i = i + 1
		f.close()		
		self.draft_dvi(name)
		return

	def all(self, name):
		file = self.TEMP+os.sep+name+".dvi"
		if not (os.path.isfile(file)):
			print self.DVI+name
		else:
			os.system("dvips "+file)
		return

	def two_sides(self, name):
		file = self.TEMP+os.sep+name+".dvi"
		if not (os.path.isfile(file)):
			print self.DVI+name
		else:
			os.system("dvips -A "+file)
			os.system("dvips -r -B "+file)
		return

	def parse_pages(self, pages):
		parsed = []
		tokens = string.split(pages,",")
		for token in tokens:
			if (string.find(token,"-") == -1):
				parsed.append(token)
			else:
				bounds = string.split(token,"-")
				lower = int(bounds[0])
				upper = int(bounds[1])
				if (lower < upper):
					for i in range(lower,upper+1):
						parsed.append(`i`)
				else:		
					for i in range(lower,upper-1,-1):
						parsed.append(`i`)
		return parsed			

	def pages(self, name, pages):
		file = self.TEMP+os.sep+name+".dvi"
		if not (os.path.isfile(file)):
			print self.DVI+name
		else:
			pages = self.parse_pages(pages)
			for page in pages:
				os.system("dvips -pp"+page+" "+file)
		return

	def service(self, params, options):
		try:
			self.lib.checkdir(self.TEMP)		
			op = options[1]
			if (op == "d"):
				files = self.lib.harvest(params[0])
				self.dvi(params[0], files)
			elif (op == "a"):
				self.all(params[0])
			elif (op == "2"):
				self.two_sides(params[0])
			elif (op == "p"):
				self.pages(params[0], params[1])
			elif (op == "8"):
				files = self.lib.harvest(params[0])
				self.draft(files[0])
			elif (op == "b"):
				files = self.lib.harvest(params[0])
				self.block(files[0])
		except SystemExit:
			pass
		except:
			self.lib.exc(self.NAME, 1)
		return
	
