# ruby2html.py
# Copyright Ruby Dos Zapatas 2003
# Ruby releases this file under the 
# GNU GPL license. See COPYING.
#
# created: 04 Jul 03
#
import os, string, sys

TITLE = "<!--title-->"
AUTHORS = "<!--authors-->"
YEAR = "<!--year-->"
CONTENT = "<!--content-->"
COUNT = "<!--count-->"
PAIRS = ["begin_quotation", "end_quotation",
		 "begin_quote", "end_quote",
		 "begin_verse", "end_verse", ]
TAGS     = {"part+:":["<p>&nbsp;<hr>\n<p>&nbsp;\n<h3>","</h3>\n<p>&nbsp;\n"],
			"chapter+:":["<p>&nbsp;<hr align=left width=75%>\n<p>&nbsp;\n<h3>","</h3>\n<p>&nbsp;\n"],
			"section+:":["<p>&nbsp;<hr align=left width=50%>\n<p>&nbsp;\n<h4>","</h4>\n<p>&nbsp;\n"],
			"subsection+:":["<p>&nbsp;<hr align=left width=25%>\n<p>&nbsp;\n<h4>","</h4>\n"],
			"paragraph":["\n<p>\n",""],
			"frontmatter":["",""],
			"begin_quotation":["<br><table width=70%><tr><td>&nbsp;&nbsp;</td><td><pre>\n",
							   "</pre></td></tr></table>\n"],
			"end_quotation":["",""],
			"begin_quote":["<br><table width=70%><tr><td>&nbsp;&nbsp;</td><td><pre>\n",
						   "</pre></td></tr></table>\n"],
			"end_quote":["",""],
			"begin_verse":["<br><table width=70%><tr><td>&nbsp;&nbsp;</td><td><pre>\n",
						   "</pre></td></tr></table>\n"],
			"end_verse":["",""],
			"asterisks":["<p align=\"center\">***",""],
			"---------":"---------",
			"interiorshot":["<h4><code>","</code></h4>\n"],
			"exteriorshot":["<h4><code>","</code></h4>\n"],
			"scene":["<h4><code>","</code></h4>\n"],
			"description":["<p><code>","</code>\n"],
			"narrative":["<p><code>","</code>\n"],
			"speaker":["<p><center><code>","</code></center>\n"],
			"dialogue":["<center><table width=50%><tr><td><code>","</code></td></tr></table></center>\n"],
			"parenthetical":["<center><code>","&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</code></center>\n"],
			"continuing":["<br><center><code>","</code></center>\n"],
			"titleover":["<h4><pre>","</pre></h4>\n"],
			"flushright":["<p align=right><code>","</code>\n"],
			"fadein":["<h4><code>","</code></h4>\n"],
			"fadeout":["<h4><code>","</code></h4><hr>"],
			"address":["<p align=right><pre>\n","</pre>\n"],
			"":["",""]
			 }
PLATE = [
	'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2//EN">\n',
	'<meta name="generator" content="ruby2shoes::ruby2html">\n',
	'<!--title--><title>\n',
	'</title>\n',
	'<center>\n',
	'<h2>&nbsp;</h2>\n',
	'<table width="95%" border="0" cellpadding="8">\n',
	'<tr>\n',
	'<td align="left">\n',
	'<h3 align=center>\n',
	'<!--title-->\n',
	'</h3>\n',
	'<h4 align=center>\n',
	'<!--authors-->By\n',
	'</h4><hr>\n',
	'<!--content-->\n',
	'<!--content end-->\n',
	'<hr></table>\n',
	'</center>\n'
	]

TWO_LINES = ["part+:","chapter+:","section+:","subsection+:"]

class ruby2html:
	
	def ulem(self, line):
		tokens = string.split(string.strip(line))
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
					tmp = front + "<u>" + token[:i+1] + "</u>" + back
				else:
					tmp = front + "<u>" + token + "</u>" + back
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
					tmp = front + "<u>" + token[:i+1] + "</u>" + back
				else:
					tmp = front + "<u>" + token + "</u>" + back
				holder.append(tmp)
			else:
				holder.append(token)
		str = string.join(holder)
		return str + "\n"

	def parse(self, file):
		dict = {}
		pending = ""
		f = open(file)
		lines = f.readlines()
		f.close()
		title = string.join(string.split(lines[1])[1:])
		dict[TITLE] = ["-=-",title+"\n"]
		authors = string.join(string.split(lines[2])[1:])
		dict[AUTHORS] = ["-=-",authors+"\n"]
		copyright = string.join(string.split(lines[3])[1:])
		dict[YEAR] = ["-=-",copyright+"\n"]
		name = string.replace(file,".sp",'.html')
		name = string.replace(name,".fc",'.html')
		content = []
		count = 0
		read = 0
		newlines = 0
		two_lines = 0
		for i in range(4, len(lines)):
			if (read):
				read = 0
				f = open(string.strip(lines[i]))
				data = f.readlines()
				f.close()
				for entry in data:
					if (string.strip(entry) == ""):
						content.append("\n<p>\n")
					else:
						content.append(entry)
				continue
			if (two_lines):
				content.append(lines[i])
				two_lines = 0
				continue
			if (string.find(lines[i],"*") == 0):
				if ((string.find(lines[i]," ") == 1) or
					(string.find(lines[i],"none") != -1) or
					(string.find(lines[i],"newpage") != -1)):
					continue
				elif (string.find(lines[i],"input") != -1):
					read = 1
				elif (string.find(lines[i],"newline") != -1):
					content.append("<br>\n")
				else:
					content.append(pending)
					tokens = string.split(lines[i])
					style = string.replace(tokens[0],"*","")
					if (string.find(style,"asterisks") != -1):
						style = "asterisks"
## 					if (style in PAIRS):
## 						if (string.find(style,"begin") != -1):
## 							newlines = 1
## 						else:
## 							newlines = 0
					try:		
						content.append(TAGS[style][0])
						if ((style in TWO_LINES) and
							(lines[i+1][0] not in ["*","#"])):
							two_lines = 1
						if (len(tokens) > 1) and (style != "asterisks"):
							count = count + (len(tokens) - 1)
							tmp = string.join(tokens[1:])
							if (two_lines):
								tmp = tmp + " <br>"
							content.append(tmp)
					except:
						pass
					try:	
						pending = TAGS[style][1]
					except:
						pending = ""
			elif (string.find(lines[i],"#") == 0):
				if (string.find(lines[i],"<!") != -1):
					comment = string.replace(lines[i],"#","")
					content.append(comment)
			else:
				words = string.split(lines[i])
				count = count + len(words)
				if (string.find(pending,"pre") == -1):
					lines[i] = string.replace(lines[i],"\\\\","<br>")
				else:	
					lines[i] = string.replace(lines[i],"\\\\","")
				if (string.find(lines[i],"_") != -1):
					content.append(self.ulem(lines[i]))
				else:
					content.append(lines[i])
					if ((newlines) and
						(string.find(lines[i+1],"_end") == -1)
						):
						content.append("<br>")
		content.append(pending)
		dict[CONTENT] = content
		dict[COUNT] = ["-=-", `count`+"\n"]
		return (name, dict)

	def write_html(self, values, plate):
		dict = values[1]
		f = open(values[0],'w')
		for line in plate:
			f.write(line)
			if (string.find(line,"<!--") == 0):
				for key in dict.keys():
					if (string.find(line,key) == 0):
						for line in dict[key]:
							if (line != "-=-"):
								f.write(line)
						break
		f.close()
		return

	def load_plate(self):
		if (os.path.exists("r2h.plate")):
			f = open("r2h.plate")
			plate = f.readlines()
			f.close()
		else:
			plate = PLATE
		return plate	

	def convert(self, name):
		sys.stdout.write(name)
		plate = self.load_plate()
		values = self.parse(name)
		self.write_html(values, plate)
		print " converted to " + values[0]

if __name__ == "__main__":
	obj = ruby2html()
	file = sys.argv[1]
	obj.convert(type)
