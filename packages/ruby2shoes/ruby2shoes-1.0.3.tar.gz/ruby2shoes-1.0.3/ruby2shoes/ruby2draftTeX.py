# -*- coding: iso-8859-1 -*->
# ruby2draftTeX
# Copyright Ruby Dos Zapatas 2004
# Ruby releases this file under the 
# GNU GPL license. See COPYING.
#
# created: March 27, 2004
#

import os, string, sys

CHAR = {
	"á":"\\'a",
	"é":"\\'e",
	"í":"\\'i",
	"ó":"\\'o",
	"ú":"\\'u",
	"Á":"\\'A",
	"É":"\\'E",
	"Í":"\\'I",
	"Ó":"\\'O",
	"Ú":"\\'U",
	"Ñ":"\\~N",
	"ñ":"\\~n",
	"¿":"?`",
	"¡":"!`",
	}

HEAD = '''%% Created by Ruby\'s ruby2draftTeX - http://ruby2shoes.sourceforge.net

\\tolerance = 10000
\\hbadness = 10000
\\baselineskip = 9 pt
\\font\\df = cmtt8
\\df

'''

NI = "\\noindent\n"
BS = "\\bigskip\n"
MS = "\\medskip\n"
SS = "\\smallskip\n"
BYE = "\\bye\n"

ELEMENTS = [
	"Title: ",
	"Author(s): ",
	"Part: ",
	"Chapter: ",
	"Section: ",
	"Subsection: "
	]

BEFORE = {
	"Title: ":BS + NI,
	"Author(s): ":MS + NI,
	"Part: ":BS + NI,
	"Chapter: ":MS + NI,
	"Section: ":SS + NI,
	"Subsection: ":SS + NI
	}

AFTER = {
	"Title: ":BS,
	"Author(s): ":MS,
	"Part: ":BS,
	"Chapter: ":MS,
	"Section: ":SS,
	"Subsection: ":""
	}

class ruby2draftTeX:

	def tex_chars(self, name,tex):
		f = open(name)
		g = open(tex,'w')
		keys = CHAR.keys()
		c = f.read(1)
		while (c != ""):
			if (c in keys):
				g.write(CHAR[c])
			else:
				g.write(c)
			c = f.read(1)
		g.close()
		f.close()
		return

	def tex_lines(self, tex):
		f = open(tex)
		lines = f.readlines()
		f.close()
		f = open(tex,'w')
		f.write(HEAD)
		for line in lines:
			for element in ELEMENTS:
				if (string.find(line,element) == 0):
					line = string.replace(line,element,"")
					f.write(BEFORE[element])
					f.write(line)
					f.write(AFTER[element])
					break
			else:
				f.write(line)
		f.write(BYE)
		f.close()
		return

	def convert(self, name):
		sys.stdout.write(name)
		tex = string.replace(name, "txt", "tex")
		self.tex_chars(name,tex)
		self.tex_lines(tex)
		print " converted to "+tex
		return
