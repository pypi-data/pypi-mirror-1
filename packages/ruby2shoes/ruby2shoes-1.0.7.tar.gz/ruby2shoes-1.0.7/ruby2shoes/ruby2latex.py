# ruby2latex.py
# Copyright Ruby Dos Zapatas 2003
# Ruby releases this file under the 
# GNU GPL license. See COPYING.
#
# created: 04 Jul 03
#
import os, string, sys

USAGE = '\nusage: python path/to/ruby2latex.py ruby.fc|ruby.sp\n'
BLANKS = ["paragraph", "fadein", "fadeout", "continuing", "titleover"]
PAIRS = ["begin_quotation", "end_quotation",
		 "begin_quote", "end_quote",
		 "begin_verse", "end_verse", ]
CREDITS = "%%   File created by ruby2shoes's ruby2latex.py\n"+\
		  "%%        See http://ruby2shoes.sourceforge.net\n"
QUOTE = '"'
LQUOTE = ["{","}","`","`"]
RQUOTE = ["'","'"]
FC = ["story", "novel"]
SP = ["tv", "movie"]

class ruby2latex:
	def get_file(self, file):
		f = open(file)
		orig = f.readlines()
		f.close()
		lines = []
		for line in orig:
			if (string.find(line,"#") != 0):
				lines.append(string.strip(line))
		return lines

	def underbar(self, line):
		tokens = string.split(line)
		holder = []
		for token in tokens:
			tmp = ""
			front = ""
			back = ""
			if (string.find(token,"_") == 0):
				token = token[1:]
				if (token[-1] in string.punctuation):
					i = -1
					while (token[i] in string.punctuation):
						back = token[i] + back
						i = i - 1
					tmp = front + "\\underbar{" + token[:i+1] + "}" + back
				else:
					tmp = front + "\\underbar{" + token + "}" + back
				holder.append(tmp)
			elif ((string.find(token,"_") == 1) and
				  (token[0] in string.punctuation)
				  ):
				front = front + token[0]
				token = token[2:]
				if (token[-1] in string.punctuation):
					i = -1
					while (token[i] in string.punctuation):
						back = token[i] + back
						i = i - 1
					tmp = front + "\\underbar{" + token[:i+1] + "}" + back
				else:
					tmp = front + "\\underbar{" + token + "}" + back
				holder.append(tmp)
			else:
				holder.append(token)
		str = string.join(holder)
		return str

	def canonical(self, line):
		if (string.find(line,"_") != -1):
			line = self.underbar(line)
		line = string.replace(line,"&","\\&")
		line = string.replace(line,"--","-{}-")
		line = string.replace(line,"INT.","")
		line = string.replace(line,"EXT.","")
		return line

	def	do_quotes(self, lines, g):
		mid = 0
		for line in lines:
			tex = []
			if ((mid) and
				(string.strip(line) == "")
				):
				mid = 0
			for i in range(0,len(line)):
				if (line[i] == QUOTE):
					if (mid):
						mid = 0
						tex = tex + RQUOTE
					else:
						mid = 1
						tex = tex + LQUOTE
				else:
					tex.append(line[i])
			line = string.join(tex,"")
			g.write(line)
		return

	def do_header(self, hdr, lines, type, g):
		title = ""
		episode = ""
		author = ""
		address = ""
		title = string.strip(lines[1])
		title = string.join(string.split(title)[1:])
		authors = string.strip(lines[2])
		authors = string.join(string.split(authors)[1:])
		year = string.strip(lines[3])
		year = string.join(string.split(year)[1:])
		i = 4
		if (type in ["movie","tv"]):
			while(string.find(lines[i],"**address") == -1):
				i = i + 1
			i = i + 1
			if (string.find(lines[i],"input") != -1):
				f = open(string.strip(lines[i+1]))
				text = f.readlines()
				for row in text:
					address = address + string.strip(row)
					if (row != text[-1]):
						address = address + "~\\\\\n"
				i = i + 2		
			else:	
				address = lines[i]
				i = i + 1
				while ((string.find(lines[i],"fadein") == -1) and
					   (string.find(lines[i],"scene") == -1)
					   ):
					address = address + "~\\\\\n" + lines[i]
					i = i + 1
		# got it - now write header
		g.write(CREDITS)
		if (string.find(title,"-") != -1):
			tokens = string.split(title,"-")
			title = tokens[0]
			episode = tokens[1]
		for line in hdr[2:]:
			line = string.replace(line,"$TITLE", title)
			line = string.replace(line,"$EPISODE", episode)
			line = string.replace(line,"$AUTHOR", authors)
			line = string.replace(line,"$ADDRESS", address)
			line = string.replace(line,"$YEAR", year)
			g.write(line + '\n')
		return i

	def do_manuscript(self, index, ms, type, g):
		in_style = 0
		outline = 0
		newlines = 0
		skip = 0
		tokens = []
		length = len(ms)
		for i in range(index, length):
			line = ms[i]
			if (string.strip(line) == ""):
				continue
			# latex tokens
			if (string.find(line,"*") == 0):
				tokens = string.split(line)
				if (in_style and not outline):
					g.write("}")
					in_style = 0
				# outline element, not latex
				if (line[1] == " "):
					outline = 1
					continue
				else:
					outline = 0
				# line is either a style marker
				if (type in FC):
					if not (line[4] == "\\"):
						style = string.replace(line,"*","")
						if (style in BLANKS):
							g.write("\n\n")
						elif (style == "none"):
							pass
						elif (style in PAIRS):
							if (string.find(style,"begin") != -1):
								newlines = 1
							else:
								newlines = 0
							tokens = string.split(style,"_")
							g.write("\n\n\\"+tokens[0]+"{"+tokens[1]+"}\n")
						elif (tokens[0][-1] == ":"):
							in_style = 1
							tokens = string.split(style)
							style = string.replace(tokens[0],"+","*")
							style = string.replace(style,":","")
							g.write("\n\n\\" + style + "{")
							tmp = string.join(tokens[1:])
							if (i+1 < len(ms)) and (ms[i+1][0] not in ["*","#"]):
								tmp = tmp + "\\\\"
							g.write(tmp)
						else:
							in_style = 1
							g.write("\n\n\\" + style + "{")
					# or it is pure latex
					else:
						latex = line[4:]
						if (string.find(latex,"asterisks") != -1):
							latex = "\\begin{center}{*}{*}{*}\\end{center}"
						elif (string.find(latex,"frontmatter") != -1):
							latex = "\\newpage\n\n~\n\\newpage"
						latex = "\n" + latex + "\n"
						g.write(latex)
				elif (type in SP):
					if not (line[1] == "\\"):
						style = string.replace(line,"*","")
						if (style in BLANKS):
							skip = 1
						g.write("\n\n\\" + style + "{")
						in_style = 1
					# or it is pure latex
					else:
						latex = line[2:]
						latex = "\n\n\\" + latex
						g.write(latex)
			# text from the ms
			else:
				if (skip):
					skip = 0
				elif ((string.find(line,"#") == 0) or
					  (outline)):
					continue
				else:
					line = self.canonical(line)
					g.write(line)
					if ((newlines) and
						(string.find(ms[i+1],"end_") == -1)):
						g.write("\n\\newline\n")
					elif ((i+1 < length) and
						not (string.find(ms[i+1],"*") == 0)):
						g.write("\n")

		if (in_style):
			g.write("}")
		g.write("\n\\end{document}")
		return

	def convert(self, file, latex=None):
		ms = self.get_file(file)
		type = string.replace(string.strip(ms[0]),"*","")
		if (latex != None):
			hdr = self.get_file("header." + latex)
		else:
			hdr = self.get_file("header." + type)
		ext = "." + file[-2:]
		name = string.replace(file,ext,"")
		# convert .fc file to latex
		try:
			g = open(name + ".tmp",'w')
			index = self.do_header(hdr, ms, type, g)
			self.do_manuscript(index, ms, type, g)
		except:
			print "fiction2latex: error in conversion to latex"
			g.close()
			raise
		g.close()
		# read up latex tmp file
		f = open(name + ".tmp")
		lines = f.readlines()
		f.close()
		# second pass to convert quotation marks
		try:
			g = open(name + ".tex",'w')
			self.do_quotes(lines, g)
		except:
			print "fiction2latex: error in conversion of quotes"
			g.close()
			raise
		g.close()
		# third pass for latex cleanup
		if (latex != None):
			try:
				g = open(name + ".tex",'w')
				self.do_latex(lines, latex, g)
			except:
				print "fiction2latex: error in latex cleanup"
				g.close()
				raise
			g.close()
		os.remove(name + ".tmp")
		return

	def	do_latex(self, lines, latex, g):
		if (latex == "paperback"):
			for line in lines:
				if (string.find(line,"\\rhead{") != -1):
					continue
				if (string.find(line,"\\underbar{") != -1):
					line = string.replace(line,"\\underbar{","\\emph{")
				g.write(line)
		return

if __name__ == "__main__":
	obj = ruby2latex()
	file = sys.argv[1]
	if (len(sys.argv) == 3):
		type = sys.argv[2]
	else:
		type = None
	obj.convert(file, type)
