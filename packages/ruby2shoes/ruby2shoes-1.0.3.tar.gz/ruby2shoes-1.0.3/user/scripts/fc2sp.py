# fc2sp.py
# Copyright Ruby Dos Zapatas 2004
# ruby2shoes@users.sourceforge.net
# 
# Ruby releases this file under the 
# GNU GPL license. See COPYING.
#
# created:  2 Sep 04
#
import os, string, sys

USAGE = '\nusage: python path/to/fc2sp.py fc2convert.fc\n'
SKIP = ["/", "#"]

def usage():
	if ((len(sys.argv) ==1) or
		("-?" in sys.argv) or
		(string.find(sys.argv[1],".fc") == -1)):
		print USAGE
		sys.exit(1)
	return

def get_lines(file):
	f = open(file)
	lines = f.readlines()
	f.close()
	return lines

def is_scene(line):
	if ((string.find(line,"paragraph") == -1) and
		(string.find(line,"input") == -1) and
		(string.find(line,"none") == -1)
		):
		return 1
	return 0

def get_chunks(lines):
	chunks = []
	chunk = None
	for line in lines:
		if (line[0] in SKIP):
			if (chunk != None):
				chunks.append(chunk)
				chunk = None
		elif ((line[0] == "*") and
			  (line[1] != " ")):
			if (chunk != None):
				chunks.append(chunk)
				chunk = None
			if is_scene(line):
				chunks.append(string.strip(line))
		elif ((line[0] == "*") and
			  (line[1] == " ")):
			pass
		else:
			line = string.replace(line,"\n"," ")
			if (chunk == None):
				chunk = line
			else:	
				chunk = chunk + line
	chunks.append(chunk)			
	return chunks

def get_slug(chunk):
	slug = "SPEAKER"
	marker = "\n***speaker\n\t\t\t\t\t"
	i = string.find(chunk,'"',1)
	if (string.find(chunk,'"') == 0):
		j = string.find(chunk,'"',i+1)
		slug = chunk[i:j]
	else:
		slug = chunk[:i]
	slug = string.replace(slug,".","")
	slug = string.replace(slug,",","")
	slug = string.replace(slug,'"',"")
	tokens = string.split(slug)
	done = 0
	slug = ""
	for token in tokens:
		if ((not done) and
			(token[0] in string.lowercase)
			):
			continue
		elif ((done) and
			  (token[0] in string.lowercase)
			  ):
			break
		else:
			done = 1
			if (slug == ""):
				slug = token
			else:
				slug = slug + " " + token
	slug = string.upper(slug)			
	return((marker, slug))

def get_dialog(chunk):
	dialog = "WORDS"
	marker = "\n***dialogue\n\t\t"
	i = string.find(chunk,'"',1)
	if (string.find(chunk,'"') == 0):
		j = string.find(chunk,'"',i+1)
		dialog = string.strip(chunk[0:i]) + " " + string.strip(chunk[j:])
	else:
		dialog = string.strip(chunk[i:])
	dialog = string.replace(dialog,'"',"")
	return ((marker, dialog))

def get_scene(chunk):
	if (string.find(chunk,"(i)") != -1):
		marker = "\n**interiorshot\nINT. "
		text = None
	elif ((string.find(chunk,"story") != -1) or
		  (string.find(chunk,"novel") != -1)):
		marker = "*movie"
		text = None
	elif (string.find(chunk,"title") != -1):
		marker = "\n*title\n"
		text = string.join(string.split(chunk)[1:])
	elif (string.find(chunk,"author(s)") != -1):
		marker = "\n**authors(s)\n"
		text = string.join(string.split(chunk)[1:])
		text = text + '''\n**copyright: $YEAR
**address
****input
/home/$USER/spirit/address.txt
***fadein
FADE IN:'''
	else:	
		marker = "\n**exteriorshot\nEXT. "
		text = None
	return ((marker, text))

def get_desc(chunk):
	marker = "\n***description\n"
	return ((marker, chunk))

def parse_chunks(chunks):
	sp = []
	for chunk in chunks:
		if (chunk != None):
			if (string.find(chunk,'"') != -1):
				sp.append(get_slug(chunk))
				sp.append(get_dialog(chunk))
			elif (string.find(chunk,'*') != -1):
				sp.append(get_scene(chunk))
			else:
				sp.append(get_desc(chunk))
	return sp

def print_sp(sp, file):
	name = string.replace(file,".fc", ".sp")
	f = open(name,'w')
	for item in sp:
		f.write(item[0])
		if (item[1] != None):
			f.write(item[1])
	f.write('\n***fadeout\nFADE OUT\n')		
	f.close()
	print file + " converted to " + name
	return

def fc2sp(file):
	lines = get_lines(file)
	chunks = get_chunks(lines)
	sp = parse_chunks(chunks)
	print_sp(sp, file)

usage()
fc2sp(sys.argv[1])
