
# lib_rharris.py::library for personal scripts
# richardharris@operamail.com
# http://cheeseshop.python.org

# Copyright (C) 2004 by Richard Harris
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

import pickle, ftplib, os, string, sys, time, traceback, urllib
import StringIO

class lib_rharris:
	NAME = "lib_rharris"
	LOG_EXC = os.path.expandvars("$HOME"+os.sep+"rh.error.log")
	MSG_EXC = ": Exiting on unforeseen exception."
	CLEAR = "clear"
	RETRIES = 2
	RM_LOG = 0
	
	def __init__(self):
		self.debug = "--debug" in sys.argv
		self.retries = 0
		if os.path.exists(self.LOG_EXC) and self.RM_LOG:
			os.remove(self.LOG_EXC)
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

	def credits(self, name, author, cprt, clear=0):
		if ((not self.debug) and (clear)):
			os.system(self.CLEAR)
		one = string.center(name+' by '+author+' (C) '+cprt,80)
		two = string.center('Released under the GNU General Public License',80)
		print "\n"+ one + "\n" + two + "\n"
		return

	def exc(self, name, msg="", exit=1):
		info = sys.exc_info()
		error = traceback.format_exception_only(info[0],info[1])
		error_hdr = name+": "+string.strip(error[0])+": "+time.ctime(time.time())
		if not (self.debug):
			f = open(self.LOG_EXC,'a')
			f.write(error_hdr+"\n")
			if (msg != ""):
				f.write(msg+"\n")
			traceback.print_tb(info[2], None, f)
			f.write("\n")
			f.close()
			if (exit):
				if (msg != ""):
					msg = name + ": "+ msg
				else:
					msg = name + self.MSG_EXC
				self.exit(msg)
		else:
			raise
		return

	def entrance(self):	
		pass # deprecator

	def exit(self, msg=""):
		if os.path.exists(self.LOG_EXC):
			print self.LOG_EXC+" has error details."
		print msg	
		sys.exit()

	def find_line(self, lines, pattern):
		index = -1
		for line in lines:
			if (line.find(pattern) != -1):
				return lines.index(line)
		return index

	def fm_projects(self, remote):
		if (remote):
			url = "http://unix.freshmeat.net/stats"
		else:
			url = "/home/richard/public_html/tech/fm.28dec04.html" # womm
		lines = self.get_lines(url, remote)
		if (lines != []):
			prev = self.find_line(lines,'<td align="left"><b>Projects</b></td>')
			projects = self.strip_html(lines[prev+1])
			return projects
		else:
			self.exit(self.NAME+": unable to retrieve "+url)

	def ftp(self, mode, files, login, dir=None):
		"""
		mode: 1 store, 0 retrieve
		login = (host, user, passwd)
		"""
		# log onto remote
		if not (self.debug):
			try:
				ftp = ftplib.FTP(login[0], login[1], login[2])
				print "Logged onto "+login[0]
			except:
				msg = "Cannot connect to "+login[0]
				self.exc(self.NAME, msg, 1)
			else:
				ftp.set_pasv(1)
				if (dir != None):
					ftp.cwd(dir)
		# stor or retr files			
		try:
			for file in files:
				fname = os.path.basename(file)
				stor = mode
				if (stor):
					if not (self.debug):
						ftp.storbinary('STOR ' + fname, open(file, 'rb'))
						print "Stored "+fname
					else:
						print "Would be storing "+fname+" on remote\n\tfrom local "+file
				else:	
					if not (self.debug):
						f = open(fname,'w')
						ftp.retrbinary('RETR ' + fname, f.write)
						f.close()
						print "Retrieved "+fname
					else:
						print "Would be retrieving "+fname
		except:
			self.exc(self.NAME, "Failed on "+fname, 1)
		else:
			if not (self.debug):
				ftp.quit()
		return
	
	def get_args(self):
		self.params = []
		self.options = []
		add = 0
		args = sys.argv
		for i in range(1, len(args)):
			arg = args[i]
			if (string.find(arg,'--') == 0):
				if (string.find(arg,":") != -1):
					add = 1
					arg = string.replace(arg,":","")	
				self.options.append(string.replace(arg,'--',''))
			elif (string.find(arg,'-') == 0):
				for j in range(1,len(arg)):
					self.options.append(arg[j])
			elif (add):
				add = 0
				self.options.append(arg)
			elif (arg != ''):
				self.params.append(arg)
		if (self.debug):
			print "Params: "+`self.params`
			print "Options: "+`self.options`
		return (self.params, self.options)

	def get_dict(self, fname):
		try:
			f = open(fname)
			dict = pickle.load(f)
			f.close()
		except:	
			dict = {}
		return dict

	def get_lines(self, file, remote=0):
		lines = []
		if not (remote):
			file = os.path.expandvars(file)
			file = os.path.expanduser(file)
			try:
				f = open(file)
				lines = f.readlines()
				f.close()
			except:
				pass
		else:
			try:
				f = urllib.urlopen(file)
				lines = f.readlines()
			except KeyboardInterrupt:
				self.exit()
			except SystemExit:
				pass
			except:
				self.retries = self.retries + 1
				if (self.retries <= self.RETRIES):
					lines = self.get_lines(file)
		self.retries = 0	
		return lines

	def get_output(self, cmd, index=1):
		cmd = os.path.expandvars(cmd)
		cmd = os.path.expanduser(cmd)
		os.chdir(os.path.expandvars("$HOME"))
		output = os.popen3(cmd)[index].readlines()
		return output

	def get_string(self, prompt):
		str = raw_input(prompt)
		return str

	def date_stamp(self):
		tmp = time.ctime(time.time())
		tokens = self.tokens(tmp)
		year = tokens[-1][-2:]
		stamp = string.join([tokens[2],tokens[1],year]," ")
		return stamp

	def save_dict(self, fname, dict):
		f = open(fname,'w')
		pickle.dump(dict,f)
		f.close()
		return

	def sf_index(self, remote):
		if (remote):
			url = "http://sourceforge.net"
		else:
			url= "/home/richard/public_html/tech/auto/sf.fp.html"
		lines = self.get_lines(url, remote)
		if (lines != []):
			index = self.find_line(lines, "Registered Projects:")
			line = self.strip_html(lines[index])
			tokens = self.tokens(line)
			total = tokens[2]
		else:
			self.exit(self.NAME+": unable to retrieve "+url)
		return total

	def tokens(self, line, sep=" "):
		tokens = []
		line = string.strip(line)
		if (line != ""):
			tmp = string.split(line, sep)
			for entry in tmp:
				if (entry != ""):
					tokens.append(entry)
		return tokens

	#
	# time stamp methods
	#

	def make_stamp(self, stamp):
		now = time.time()
		f = open(stamp,'w')
		f.write(`now`)
		f.close()
		return

	def get_stamp(self, stamp):
		VIRGIN = '''
		A time stamp has not been used on this directory tree before.
		Actions are based on a timestamp file that has just been created.
		Next time you run this app on this directory, all files newer than
		now will be acted upon.
		'''
		last_time = None
		if (os.path.exists(stamp)):
			f = open(stamp)
			last_time = float(string.strip(f.readline()))
			f.close()
		else:
			self.make_stamp(stamp)
			print VIRGIN
			return -1
		return last_time

	#
	# html methods 
	#

	def insert_tags(self, lines, pairs):
		def __strip(line):
			line = string.replace(line,"<!--","")
			line = string.replace(line,"-->","")
			line = string.strip(line)
			return line
		pairs["stamp"] = self.date_stamp()+"\n"
		newlns = []
		out = 1
		pending = ""
		for line in lines:
			if (out):
				newlns.append(line)
			if (string.find(line,"<!--") == 0):
				key = __strip(line)
				if (key in pairs.keys()):
					newlns.append(pairs[key])
					pending = key
					out = 0
				elif (key == pending+" end"):
					newlns.append(line)
					out = 1
		return newlns

	def form_only(self, file):
		FORM = ["form","input","textarea", "select", "option", "optgroup", "base", "isindex"]
		g = ""
		lines = file.readlines()
		for line in lines:
			tag = line.split(">")[0].lower()
			for tg in FORM:
				if (tag.find(tg) != -1):
					g = g + line
					break
		data = StringIO.StringIO(g)
		return data

	def html_canonical(self, file, lower=0):
		data = string.replace(file.read(),"\n"," ")
		g = ""
		tag = 0
		comment = 0
		for i in range(0, len(data)):
			if (i < comment):
				continue
			if data[i] == "<":
				if (data[i+1] == "!") and (data[i+2] not in ["d","D"]):
					comment = data[i+1:].index("-->")+ 2 + i
					continue
				else:	
					tag = 1
					g = g + "\n"
			elif data[i] == ">":
				tag = 0
			if (tag and lower):
				g = g + string.lower(data[i])
			else:
				g = g + data[i]
		data = StringIO.StringIO(g)
		return data

	def strip_html(self, line):
		length = len(line)
		newln = []
		tag = 0
		i = 0
		while (i < length):
			if (line[i] == '<'):
				tag = 1
			if not (tag):
				newln.append(line[i])				
			if (line[i] == '>'):
				tag = 0
				newln.append(" ")
			i = i + 1
		newln = string.strip(string.join(newln,""))
		next = ""
		while (newln != next):
			next = newln
			newln = string.replace(newln,"	"," ")
		return newln

	def table_data(self, lines, i):
		"""prep with canonical, does not work with nested tables"""
		table = []
		tr = []
		tag = 0
		data = "-=-"
		while (string.find(lines[i],"</table") == -1):
			if (string.find(lines[i],"<tr") != -1):
				if (tr != []): table.append(tr)
				tr = []
			elif (string.find(lines[i],"<td") != -1):
				data = ""
				tag = 1
			elif (string.find(lines[i],"</td") != -1):
				if not (data == "-=-"): tr.append(data)
				tag = 0
			if (tag): data = data + self.strip_html(lines[i])
			i += 1	
		return table
	
	#
	# harvest methods
	#

	def harvest2(self, args, dirname, names):
		"""used by harvest"""
		for name in names:
			if ((string.find(name,args[0]) != -1) and
				(string.find(name,"~") == -1) and
				(string.find(name,"#") == -1)):
				args[1].append(dirname+os.sep+name)
		return

	def harvest(self, dir, name):
		list = []
		os.path.walk(dir, self.harvest2, [name, list])
		return list
		
	
