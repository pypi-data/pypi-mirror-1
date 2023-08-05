
# SpiritArchive.py::maintains local and remote archives
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

import ftplib, os, shutil, string, zipfile

class SpiritArchive:
	NAME = "SpiritArchive"
	OVRWRT = NAME+"::Refusing to overwrite existing "
	
	def __init__(self, debug, lib, consts):
		self.debug = debug
		self.lib = lib
		self.MAX = consts.MAX_ARCHIVES
		self.RC = consts.RC
		self.SAFE = consts.SAFE
		self.TEMP = consts.TEMP
		return

	def cycle(self, target):
		name = os.path.basename(target)
		for i in range(2, self.MAX+1):
			last = target + os.sep + name + "."+ `i-1` + ".zip"
			next = target + os.sep + name + "."+ `i` + ".zip"
			os.remove(last)
			shutil.copy2(next, last)
		return	

	def getname(self, target):
		name = os.path.basename(target)
		list = os.listdir(target)
		count = len(list) + 1
		if (count > self.MAX):
			self.cycle(target)
			count = self.MAX
		fname = target + os.sep + name + "."+ `count` +".zip"
		return fname
	
	def zip(self, name, files):
		print "archiving:"
		target = self.SAFE+os.sep+name
		target = self.lib.checkdir(target)
		head = os.path.basename(target)
		fname = self.getname(target)
		for file in files:
			if ((string.find(file,head) != -1) and
				(string.find(file,"~") == -1) and
				(string.find(file,"#") == -1)):
				shutil.copy(file,self.TEMP)
				print "  " + file
		try:
			z = zipfile.ZipFile(fname,'w', zipfile.ZIP_DEFLATED)
		except:	
			z = zipfile.ZipFile(fname,'w')
		os.chdir(self.TEMP)
		files = os.listdir(".")
		for file in files:
			z.write(file)
			os.remove(file)
		z.close()
		os.rmdir(self.TEMP)
		return

	def unzip(self, params):
		print "restoring:"
		try:
			head = os.path.basename(params[0])
			i, full = self.lib.isdir(self.SAFE+os.sep+head)
			name = os.path.basename(full)
			fname = full+os.sep+name+"."+params[1]+".zip"
			z = zipfile.ZipFile(fname)
			list = z.namelist()
			for name in list:
				print "  "+name
				if (os.path.isfile(name)):
					print self.OVRWRT + name
				else:	
					f = open(name,'w')
					f.write(z.read(name))
					f.close()
			z.close()	
		except:
			self.lib.exc(self.NAME, 1)
		return	

	def put(self, name, files):
		print "uploading:"
		if (name[0] == "."):
			name = name[1:]
		i, full = self.lib.isdir(self.SAFE+os.sep+name)
		name = os.path.basename(full)
		fname = name+".ftp.zip"
		for file in files:
			if ((string.find(file, name) != -1) and
				(string.find(file,"~") == -1) and
				(string.find(file,"#") == -1)):
				shutil.copy(file,self.TEMP)
				print "  "+file
		try:
			z = zipfile.ZipFile(fname,'w', zipfile.ZIP_DEFLATED)
		except:	
			z = zipfile.ZipFile(fname,'w')
		lastdir = os.getcwd()	
		os.chdir(self.TEMP)
		files = os.listdir(".")
		for file in files:
			z.write(file)
			os.remove(file)
		z.close()
		# .spiritrc
		f = open(self.RC)
		tokens = string.split(string.strip(f.readline()))
		f.close()
		# connect
		os.chdir(lastdir)
		try:
			ftp = ftplib.FTP(tokens[0], tokens[1], tokens[2])
		except:
			os.remove(fname)
			self.lib.exc(self.NAME, 1)
		else:
			ftp.set_pasv(1)
			ftp.cwd('archive')
		# store
		try:
			ftp.storbinary('STOR ' + fname, open(fname, 'rb'))
		except:
			os.remove(fname)
			self.lib.exc(self.NAME, 1)
		else:
			ftp.quit()
		os.remove(fname)
		os.rmdir(self.TEMP)
		print "uploaded "+fname
		return

	def get(self, name):
		i, full = self.lib.isdir(self.SAFE+os.sep+name)
		name = os.path.basename(full)
		fname = name+".ftp.zip"
		print "retrieving: "+fname
		f = open(self.RC)
		tokens = string.split(string.strip(f.readline()))
		f.close()
		f = open(fname,'w')
		try:
			ftp = ftplib.FTP(tokens[0], tokens[1], tokens[2])
		except:
			self.lib.exc(self.NAME, 1)
		else:
			ftp.set_pasv(1)
			ftp.cwd('archive')
		try:
			ftp.retrbinary('RETR ' + fname, f.write)
		except:
			self.lib.exc(self.NAME, 1)
		else:
			ftp.quit()
		f.close()
		try:
			z = zipfile.ZipFile(fname)
			list = z.namelist()
			for name in list:
				if (os.path.isfile(name)):
					print "  "+self.OVRWRT + name
				else:	
					f = open(name,'w')
					f.write(z.read(name))
					f.close()
					print "  "+name
			z.close()
			os.remove(fname)
		except:
			self.lib.exc(self.NAME, 1)
		return

	def service(self, params, options):
		try:
			self.lib.checkdir(self.SAFE)		
			self.lib.checkdir(self.TEMP)		
			op = options[1]
			if (op == "z"):
				files = self.lib.harvest(params[0])
				self.zip(params[0], files)
			elif (op == "u"):
				self.unzip(params)
			elif (op == "p"):
				files = self.lib.harvest(params[0])
				self.put(params[0], files)
			elif (op == "g"):
				self.get(params[0])
		except SystemExit:
			pass
		except:
			self.lib.exc(self.NAME, 1)
		return
	
