# TalentAgencyList.py
# Copyright Ruby Dos Zapatas 2004
# Ruby releases this file under the 
# GNU GPL license. See COPYING.
#
# created: 19 March 2004
#
import os, string, urllib

class TalentAgency:
	WGAWDIR = os.getcwd()
	AGENCIES = 'http://www.dir.ca.gov/ftproot/TALENTA.TXT'
	TMPFILE = 'TALENTA.tmp'
	FIELDS = 'fields'
	KILLFILE = 'TalentAgencyKillfile'
	DB = 'agencies.db'

	def __init__(self):
		self.lines = []
		return

	def getAgencies(self):
		val = urllib.urlretrieve(self.AGENCIES, self.WGAWDIR + os.sep + self.TMPFILE)
		return

	def readLines(self):
		f = open(self.TMPFILE)
		self.lines = f.readlines()
		f.close()
		return

	def reduceLines(self):
		tmplines = []
		kill = []
		if os.path.exists(self.KILLFILE):
			g = open(self.KILLFILE)
			tmp = g.readlines()
			g.close()
			for line in tmp:
				kill.append(string.strip(string.upper(line)))
		for i in range(1,len(self.lines)):
			self.lines[i] = string.replace(self.lines[i],'\t\t','\t')
			self.lines[i] = string.replace(self.lines[i],'Õ','O')
			self.lines[i] = string.replace(self.lines[i],'#','')
			self.lines[i] = string.replace(self.lines[i],'&','and')
			self.lines[i] = string.replace(self.lines[i],', TALENT AGENCY','')
			self.lines[i] = string.replace(self.lines[i],'SUITE','Ste.')
			tokens = string.split(self.lines[i],'\t')
			if (string.find(tokens[1],'DBA:') != -1):
				tokens[1] = string.replace(tokens[1],'DBA: ',':')
				tokens[1] = (string.split(tokens[1],':'))[1]
			tokens = tokens[1:-2]
			good = 1
			for entry in kill:
				if (string.find(tokens[0],entry) != -1):
					good = 0
					break
			if good:
				tmplines.append(tokens)
		self.lines = tmplines
		self.lines.sort()
		return

	def writeDB(self):
		fields = 0
		more = 0
		if os.path.exists(self.FIELDS):
			g = open(self.FIELDS)
			fields = g.readlines()
			g.close()
			more = 1
		f = open(self.DB,'w')
		for line in self.lines:
			tokens = string.split(line[0])
			f.write(string.capitalize(tokens[0]))
			for i in range(1,len(tokens)):
				f.write(' ' + string.capitalize(tokens[i]))
			f.write(':')			
			tokens = string.split(line[1])			
			f.write(string.capitalize(tokens[0]))
			for i in range(1,len(tokens)):
				f.write(' ' + string.capitalize(tokens[i]))
			f.write(':')
			tokens = string.split(line[2])			
			f.write(string.capitalize(tokens[0]))
			for i in range(1,len(tokens)):
				f.write(' ' + string.capitalize(tokens[i]))
			f.write(', ' + line[3] + ' ' + line[4])
			if more:
				for line in fields:
					f.write(':' + string.strip(line))
			f.write('\n')
		f.close()
		return

	def run(self):
		self.getAgencies()
		self.readLines()
		self.reduceLines()
		self.writeDB()
		return
	
#-----------------main
obj = TalentAgency()
obj.run()
