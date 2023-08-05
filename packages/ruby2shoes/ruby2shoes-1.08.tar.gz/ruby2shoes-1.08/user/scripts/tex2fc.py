# tex2fc
# Copyright Ruby Dos Zapatas 2004
# ruby2shoes@users.sourceforge.net
# 
# Ruby releases this file under the 
# GNU GPL license. See COPYING.
#
# created:  9 Jun 04
#
# Output requires handwork for underline/emphasis
# and for remaining latex lines, removal of
# end_document line, replacement of "novel" with
# "story" in story.fc documents
#
import os, string, sys

USAGE = '\nusage: python path/to/tex2fc.py tex2convert.tex\n'
PARAGRAPH = "***paragraph\n"
DEBUG = 0

def usage():
	print USAGE
	sys.exit(1)
	return

def get_lines(file):
	try:
		f = open(file)
		lines = f.readlines()
		f.close()
	except:	
		lines = []
	return lines

def write_lines(file, lines):
	f = open(file,'w')
	for line in lines:
		f.write(line)
	f.close()
	return

# easy conversions, paragraphs
def pass_one(lines):
	PAIRS_ONE = [
	("{}``",'"'),
	("''",'"'),
	('\\char`\\"{}','"'),
	("\\emph{","_"),
	("\\underbar{","_"),
	("\\\\",""),
	("\\ldots{}","..."),
	("\\begin{center}{*}{*}{*}\\end{center}","****\\asterisks")
	]
	one = []
	para = 0
	title = 0
	for line in lines:
		# skip down to title
		if not title:
			if (string.find(line,'\\title') == 0):
				title = 1
			else:	
				continue
		if (string.strip(line) != ""):
			# input files
			if (string.find(line,"\\input{") == 0):
				line = string.replace(line,"{"," ")
				line = string.replace(line,"}"," ")
				tokens = string.split(line)
				file = tokens[1]
				rest = tokens[2:]
				one.append("****input\n"+file+"\n****none\n"+string.join(rest)+"\n")
				continue
			# replace most blank lines with paras
			if ((para) and (line[0] != "\\")):
				one.append(PARAGRAPH)
			para = 0
			# simple substitutions
			for pair in PAIRS_ONE:
				line = string.replace(line,pair[0],pair[1])
			# begin-end latex styles 	
			if (string.find(line,"\\begin{") == 0):
				line = string.replace(line,"\\begin{","****begin_")
				line = string.replace(line,"}","")
			elif (string.find(line,"\\end{") == 0):
				line = string.replace(line,"\\end{","****end_")
				line = string.replace(line,"}","")
			one.append(line)
		elif not para: 
			para = 1
	if (DEBUG):
		write_lines("one", one)
	return one

def pass_two(lines):
	PAIRS_TWO = [
	("\\title{","*novel\n*title: "),
	("\\author{","*author(s): "),
	("\\part*{","*part+: "),
	("\\chapter*{","*chapter+: "),
	("\\section*{","**subsection+:   "),
	("\\subsection*{","**subsection+:     "),
	("\\subsubsection*{","**subsection+:     ")
	]
	two = []
	for line in lines:
		old_line = line
		# replace style tags
		for pair in PAIRS_TWO:
			line = string.replace(line,pair[0],pair[1])
		# if style replaced, strip closing brace		
		if ((line != old_line) and (string.strip(line)[-1] == "}")):
			line = string.strip(line)[:-1] + "\n"
		two.append(line)
	if (DEBUG):
		write_lines("two",two)	
	return two

def tex2fc(file):
	sys.stdout.write(sys.argv[1])
	lines = get_lines(file)
	lines = pass_one(lines)
	lines = pass_two(lines)
	fname = string.replace(file,".tex",".fc")
	write_lines(fname, lines)
	print " converted to " + fname
	return

if (("-?" in sys.argv) or
	(len(sys.argv) != 2) or
	(string.find(sys.argv[1],".tex") == -1) or
	(not os.path.isfile(sys.argv[1]))):
	usage()
else:
	file = sys.argv[1]
	tex2fc(file)
