# tex2sp.py
# Copyright Ruby Dos Zapatas 2004
# ruby2shoes@users.sourceforge.net
# 
# Ruby releases this file under the 
# GNU GPL license. See COPYING.
#
# created: 10 Jun 04
#
import os, string, sys

USAGE = '\nusage: python path/to/tex2sp.py hollywood_class.tex\n'
TWOS = ["scene","interiorshot","exteriorshot"]
UPPER = ["speaker","scene","interiorshot","exteriorshot"]
EMPTY = {
	"fadein":"FADE IN:",
	"fadeout":"FADE OUT",
	"continuing":""
	}
MARGINS = {
	"continuing":("                         ",80),
	"description":("",80),
	"dialogue":("               ",50),
	"exteriorshot":("",80),
	"fadein":("",80),
	"fadeout":("",80),
	"interiorshot":("",80),
	"narrative":("",80),
	"parenthetical":("                    ",60),
	"scene":("",80),
	"speaker":("                         ",80),
	"titleover":("               ",60)
	}
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

def set_style(style):
	if (style in TWOS):
		style = "**"+style
	else:	
		style = "***"+style
	return style

def remove_label(line):
	while (string.find(line,"\\label") != -1):
		one = string.index(line,"\\label")
		two = string.index(line,"}",one)
		line = line[:one] + line[two+1:]
	return line

def remove_ref(line):
	while (string.find(line,"\\ref") != -1):
		one = string.index(line,"\\ref")
		two = string.index(line,"}",one)
		line = line[:one] + line[one+5:two] + line[two+1:]
	return line

def pass_one(lines):
	PAIRS_ONE = [
	('\\char`\\"{}','"'),
	("-{}-","--"),
	("\\underbar{","_"),
	("~"," "),
	("\\emph{","_"),
	("\\ldots{}","...")
	]
	one = []
	fadein = 0
	for line in lines:
		if not fadein:
			if (string.find(line,'\\fadein') == 0):
				one.append("***fadein\nFADE IN: \n")
				fadein = 1
			elif (string.find(line,'\\title') == 0):
				line = values(line)[1]
				one.append("*movie\n*title: "+line+"\n")
			elif (string.find(line,'\\author') == 0):
				line = values(line)[1]
				one.append("*author(s): "+line+"\n")
			elif (string.find(line,'\\address') == 0):
				one.append("**address\n****input\n/home/user/spirit/address.txt\n")
			continue
		# simple substitutions
		if (string.find(line,"\\label") != -1):
			line = remove_label(line)
 		if (string.find(line,"\\ref") != -1):
 			line = remove_ref(line)
		for pair in PAIRS_ONE:
			line = string.replace(line,pair[0],pair[1])
		one.append(line)	
	if (DEBUG):
		write_lines("one", one)
	return one

def values(line):
	line = string.strip(line)
	line = string.replace(line,"\\"," ",1)
	line = string.replace(line,"{"," ")
	line = string.replace(line,"}"," ")
	tokens = string.split(line)
	style = tokens[0]
	if (EMPTY.has_key(style)):
		line = EMPTY[style]
	else:	
		line = tokens[1:]
		line = string.join(line)
		if (style == "speaker"):
			EMPTY["continuing"] = line + " (CONT'D)"
	upper = style in UPPER		
	style = set_style(style)
	return (style, line, upper)

def pass_two(lines):
	two = []
	more = 0
	pending = ""
	fadein = 0
	for line in lines:
		if not fadein:
			if (string.find(line,'***fadein') == 0):
				fadein = 1
			two.append(line)
			continue
		if (more):
			if (string.strip(line) == ""):
				if ((pending != "") and (pending[-1] == "}")):
					pending = pending[:-1]
				two.append(pending + "\n")
				pending = ""
				more = 0
			else:
				pending = pending + " " + string.strip(line)
		elif (string.find(line,"\\") == 0):
			vals = values(line)
			style = vals[0]
			two.append(style + "\n")
			pending = string.strip(vals[1])
			if (vals[2]):
				pending = string.upper(pending)
			elif (string.find(vals[0],"paren") != -1):
				pending = "("+pending+")"
			more = 1
	two.append(pending + "\n")
	if (DEBUG):
		write_lines("two", two)
	return two

def append(list, line, margins):
	line = string.strip(line)
	indent = margins[0]
	length = margins[1]
	if (len(line) < length - len(indent)):
		list.append(indent + line + "\n")
	else:
		if (string.find(line,"\\\\") != -1):
			line = string.replace(line,"\\\\","|")
			tokens = string.split(line,"|")
			for token in tokens:
				token = string.strip(token)
				if (token != string.strip(tokens[-1])):
					token = token + " \\\\"
				list.append(indent + token + "\n")
		else:
			tokens = string.split(line, " ")
			while (len(tokens) > 0):
				i = 1
				if (indent != ""):
					tokens = [indent] + tokens
				line = tokens[0] + " "
				while ((len(tokens) > i ) and
					(len(line) < length)):
					line = line + tokens[i] + " "
					i = i + 1
				list.append(line + "\n")
				tokens = tokens[i:]
	return		

def pass_three(lines):
	three = []
	margins = None
	for line in lines:
		if (string.find(line,"*") == 0):
			three.append(line)
			if (string.find(line,"titleover") != -1):
				three.append("Title Over:\n")
			style = string.replace(string.strip(line),"*","")
			try:
				margins = MARGINS[style]
			except:
				margins = ("",80)
		else:
			append(three, line, margins)
	if (DEBUG):
		write_lines("three", three)
	return three

def tex2sp(file):
	sys.stdout.write(sys.argv[1])
	lines = get_lines(file)
	lines = pass_one(lines)
	lines = pass_two(lines)
	lines = pass_three(lines)
	fname = string.replace(file,".tex",".sp")
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
	tex2sp(file)
