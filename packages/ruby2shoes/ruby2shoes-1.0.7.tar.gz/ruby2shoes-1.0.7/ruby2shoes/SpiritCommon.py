
# SpiritCommon.py::Common Library for Spirit Project
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

import os, string, sys, time, traceback
import SpiritConsts

class SpiritCommon:
	NAME = "SpiritCommon"
	LOG_EXC = os.path.expanduser("~/errors.spirit")
	MSG_EXC = ": Exiting on unforeseen exception."
	
	def __init__(self):
		consts = SpiritConsts.SpiritConsts()
		self.DEBUG = consts.DEBUG
		self.ROOT = consts.ROOT
		self.TEMP = consts.TEMP
		return

	# should take dict or list and do the right thing.
	def choose(self, set, prompt, index=-1):
		"""
		takes a list or a dict and a prompt
		returns int(raw_input) for list, key for dict[key] for a dict
		if set member is compound, index determines which element is menued
		"""		
		if (isinstance(set, dict)): # set is a Python dictionary
			keys = set.keys()
			keys.sort()
			for key in keys:
				if (index != -1):
					print '(' + key + ') ' + set[key][index]
				else:	
					print '(' + key + ') ' + set[key]
			choice = None
			while (choice not in set.keys()):
					choice = raw_input(prompt)
		else: # set is a Python list
			length = len(set)
			for i in range(0, length):
				if (index != -1):
					print '(' + `i` + ') ' + set[i][index]
				else:	
					print '(' + `i` + ') ' + set[i]
			choice = -1
			while ((choice < 0) or (choice > length)):
				try:
					choice = int(raw_input(prompt))
				except:
					choice = -1
		return choice

	def exc(self, name, exit=0):
		info = sys.exc_info()
		error = traceback.format_exception_only(info[0],info[1])
		error_hdr = name+": "+string.strip(error[0])+": "+time.ctime(time.time())
		f = open(self.LOG_EXC,'a')
		f.write(error_hdr+"\n")
		traceback.print_tb(info[2], None, f)
		f.write("\n")
		f.close()
		if (exit):
			print "Spirit" + self.MSG_EXC
			print "  "+error_hdr
			print "  For details see: "+self.LOG_EXC
			sys.exit()
		if (self.DEBUG):
			raise
		return

	def exit(self, code=0):
		sys.exit(code)

	def harvest2(self, args, dirname, names):
		for name in names:
			if ((string.find(name,args[0]) != -1) and
				(string.find(name,"~") == -1) and
				(string.find(name,"#") == -1)):
				args[1].append(dirname+os.sep+name)
		return

	def harvest(self, name):
		list = []
		os.path.walk(self.ROOT, self.harvest2, [name, list])
		if (self.DEBUG):
			print list
		return list
		
	def isdir(self, dir):
		if not (os.path.isdir(dir)):
			head = os.path.basename(dir)
			dirname = os.path.dirname(dir)
			list = os.listdir(dirname)
			for item in list:
				if ((string.find(item,head) != -1) and
					os.path.isdir(dirname+os.sep+item)):
					return 0, dirname + os.sep + item	 # found a match
			return 1, dir  # no match
		else:
			return 0, dir  # is a dir

	def checkdir(self, dir):
		mkdir, target = self.isdir(dir)
		if (mkdir):
			os.mkdir(target)
		return target

	def rm_tmpdir(self):
		list = os.listdir(self.TEMP)
		for file in list:
			os.remove(self.TEMP+os.sep+file)
		os.rmdir(self.TEMP)
		return

	def get_lines(self, file):
		f = open(file)
		lines = f.readlines()
		f.close()
		return lines

	def write_lines(self, file, lines):
		f = open(file,'w')
		for line in lines:
			f.write(line)
		f.close()
		return lines
