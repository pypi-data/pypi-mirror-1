# ruby2text.py
# Copyright Ruby Dos Zapatas 2003
# Ruby releases this file under the 
# GNU GPL license. See COPYING.
#
# created: 04 Jul 03
#
import os, string, sys

INDENT = "    "

class ruby2text:

	def __convert(self, file, type):
		f = open(file)
		lines = f.readlines()
		f.close()
		read = 0
		indent = 0
		name = string.replace(file,type,'.txt')
		g = open(name,'w')
		for i in range(0, len(lines)):
			if (read):						                 # read in input file
				read = 0
				f = open(string.strip(lines[i]))
				data = f.readlines()
				f.close()
				for entry in data:
					g.write(entry)
				continue
			lines[i] = string.replace(lines[i],"\\\\","")
			lines[i] = string.replace(lines[i],"\t","     ")
			if ((string.find(lines[i],"\\newline") != -1) or # null lines
				(string.find(lines[i],"*none") != -1)):
				continue
			elif (string.find(lines[i],"<!") != -1):           # adc comment lines
				g.write("\n")
			elif (string.find(lines[i],"*") == 0):           # style lines
				if (string.find(lines[i],":") != -1):
					tokens = string.split(lines[i])
					tmp = string.replace(tokens[0],"*","")
					tmp = string.replace(tmp,"+","")
					tmp = string.capitalize(tmp)
					tmp = string.replace(tmp,"Subsection",":")
					tmp = string.replace(tmp,"Section",":")
					g.write("\n" + tmp + " " + string.join(tokens[1:])+"\n")
				elif (string.find(lines[i],"frontmatter") != -1):
					continue
				elif (string.find(lines[i],"asterisks") != -1):
					g.write("\n\n                                  *  *  *\n\n")
				elif (string.find(lines[i],"end_") != -1):
					indent = 0
					g.write("\n")
				elif (string.find(lines[i],"begin_") != -1):
					indent = 1
					g.write("\n")
				else:
					if (lines[i][1] != " "):
						if (string.find(lines[i],"input") != -1): # flag input file
							read = 1
						g.write("\n")
			elif (string.find(lines[i],"#") == 0):
				if (string.find(lines[i],"<!") != -1):
					comment = string.replace(lines[i],"#","")
					g.write(comment)
			else:
				line = string.replace(lines[i],"_","") # remove underbars
				if (indent):
					line = INDENT + line
				if (string.find(line,"(CONT'D)") != -1):
					line = string.upper(line)
				g.write(line)      # text
		g.close()
		return name

	def convert(self, file):
		sys.stdout.write(file)
		if (string.find(file,".fc") != -1):
			name = self.__convert(file, ".fc")
		else:
			name = self.__convert(file,".sp")
		print " converted to "+name	

if __name__ == "__main__":
	obj = ruby2text()
	file = sys.argv[1]
	obj.convert(type)
