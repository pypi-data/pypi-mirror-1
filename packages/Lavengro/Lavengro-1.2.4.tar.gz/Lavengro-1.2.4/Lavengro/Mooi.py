# Mooi.py  Copyright Richard Harris 2002
#
# "Mooi" is Romany for face. This is the interface
# to the user for Lavengro.
#
# author: Richard Harris (richardharris@operamail.com)
# The author releases this file under the GPL
# license. See COPYING for specifics.
#
# created: 11apr02
#
import os, shutil, string, sys, time

class Mooi:
	MAX_CHOICES = 15
	DIR = os.path.expandvars('${HOME}/Lavengro')
	LRC = os.path.expandvars(DIR + os.sep + 'lavengrorc')
	HDR = "\nLavengro - The Word Master" 
	MODE = ['lavengro - programmed learning',
			'test - one chance to answer, scored result',
			'tutor - retest until all correct, no score',
			'quiz - bsd compatible, uses index file (see docs)']

	def __init__(self, debug):
		self.header = 0
		self.lav = None
		self.lavLoaded = 0
		self.modes = [0,0,0,0]				# lavengro, test, tutor, quiz
		self.oldLav = []
		self.pending = []
		self.prevUsrChoice = -1
		self.quiz = []
		self.record = ''
		self.scored = []
		self.subdir = None
		self.subject = None
		self.taken = []
		self.tests = None
		self.total = 0
		# set program's directory
		if os.path.exists(self.LRC):
			f = open(self.LRC,'r')
			tmpdir = string.strip(f.readline())
			f.close()
			if os.path.exists(tmpdir):
				self.DIR = tmpdir
			else:
				msg = 'Directory ' + tmpdir + ' in .lavengrorc does not exist.'
				self.exit(msg, 1)
		return

	# kill the blank lines at bottom of file
	def purge(self, lines):
		for i in range(len(lines)-1,0,-1):
			if (string.strip(lines[i]) == ''):
				lines = lines[:-1]
			else:			
				break
		return lines

	# get user to choose an element from thing
	def show_choices(self, list, index):
		length = len(list)
		if (os.name != "nt"):
			os.system("clear")
		else:
			os.system("cls")
		i = index
		choices = ['0']
		print self.HDR
		print "-------------------"
		print '(0) quit'
		while ((i < length) and
			   (i < (index + self.MAX_CHOICES))):
			print '('+`i+1`+') '+list[i]
			choices.append(`i+1`)
			i = i+1
		if (i < length):
			print '(m) more'
		if (i > self.MAX_CHOICES):
			print '(b) back'
		print "-------------------"
		return choices

	def query(self, list, prompt):
		last = 0
		i = 1
		choices = self.show_choices(list, last)
		choice = None
		while (choice not in choices):
			choice = raw_input(prompt)
			if (choice in ['m','b']):
				if (choice == 'm'):
					last = last + self.MAX_CHOICES
				if (choice == 'b'):
					last = last - self.MAX_CHOICES
				if ((last < 0) or (last > len(list))):
					last = 0
				choices = self.show_choices(list, last)
		if (choice == '0'):
			self.exit(" ",0)
		else:	
			choice = int(choice)-1
		return choice

	#compare files by date, oldest first
	def compDates(self, file1, file2):
		x = os.path.getmtime(self.prefix + file1)
		y = os.path.getmtime(self.prefix + file2)
		if (x < y):
			return 1
		elif (x > y):
			return -1
		return 0

	#compare list elements by third field
	def compThird(self, one, two):
		x = (string.split(one,':'))[2]
		y = (string.split(two,':'))[2]
		if (x < y):
			return 1
		elif (x > y):
			return -1
		return 0

	# sort .lav data and combine with remaining untaken tests
	def sort(self, lines):
		scores = []
		testables = []
		tutors = []
		lists = [scores, testables, tutors]
		tests = []
		for line in lines:
			if (string.find(line, '*SCORE*') != -1):
				scores.append(line)
			elif (string.find(line, '*TESTABLE*') != -1):
				testables.append(line)
			elif (string.find(line, '*TUTOR*') != -1):
				tutors.append(line)
		for i in range(0, len(lists)):
			if (len(lists[i]) > 0):
				lists[i].sort(self.compThird)
				for entry in lists[i]:
					tokens = string.split(entry,':')
					self.tests.remove(tokens[0])
					if ((tokens[1].find('*SCORE*') != -1) and
						(float(tokens[2]) >= 90.0)):
						continue
					tests.append(tokens[0])
					if (i < 2):
						self.scored.append(tokens[0])
		self.tests = tests + self.tests
		return

	# get quiz in lavengro mode, choosing dir then file
	def selectQuiz(self):
		# subsequent lavengro loads
		if ((self.modes[0]) and (self.tests != None)): 
			if (len(self.tests) != 0):
				self.quiz = [ self.prefix + self.get_next(), 0, 1]
				return
			else:
				self.exit('All tests taken.', 0)
		# choose dir/subject
		if (self.subject == None):
			dirs = []
			files = os.listdir(self.DIR)
			for file in files:
				if ((os.path.isdir(self.DIR + os.sep + file)) and
					(file != 'py')):
					dirs.append(file)
			self.subject = choice = self.query(dirs, 'Choose subject: ')
			self.subdir = dirs[choice]
		# set testing mode
		self.modes = [0,0,0,0]
		self.modes[self.query(self.MODE, 'Select testing mode: ')] = 1
		# bsd is its own thing
		if (self.modes[3]):
			self.bsdMode()
			return			
		# choose test in subject
		self.tests = []
		files = os.listdir(self.DIR + os.sep + self.subdir)
		for file in files:
			if (not os.path.isdir(self.DIR + os.sep + self.subdir + os.sep + file)):
				# no backups, *MEs, .lavs, or bsd indices
				if ((string.find(file,'~') == -1) and
					(string.find(file,'.lav') == -1) and
					(string.find(file,'ME') == -1) and
					(string.find(file,'index') == -1)):
					self.tests.append(file)
 		if (len(self.tests) == 0):
			self.exit('No tests for chosen subject.\nExiting...', 1)
		self.prefix = self.DIR + os.sep + self.subdir + os.sep
		self.tests.sort(self.compDates)
		user = os.path.expandvars('$USER')
		if (user == ''):
			user = 'user'
		self.record = self.prefix + user + '.lav'

		if (self.modes[0]):				# initial lavengro mode load
			if os.path.exists(self.record):
				self.sort(self.loadLav())
			else:					   
				self.lav = open(self.record, 'w')
			self.quiz = [ self.prefix + self.get_next(), 0, 1]
		else:							# all test and tutor loads
			if not self.lavLoaded: self.loadLav()
			self.tests.sort()
			choice = self.query(self.tests, 'Enter quiz number: ')
			self.quiz = [ self.prefix + self.tests[choice], 0, 1]
		return

	def get_next(self):
		next = self.tests.pop()
		if (next in self.scored):
			self.modes[1] = 1
			self.modes[2] = 0
		else:
			self.modes[1] = 0 
			self.modes[2] = 1
		return next

	def loadLav(self):
		if (os.path.exists(self.record)):
			shutil.copyfile(self.record, self.record + '.safe')
			self.lav = open(self.record, 'r')
			lines = self.lav.readlines()
			self.lav.close()
			self.oldLav = lines
		else:
			self.oldLav = []
			lines = []
		self.lav = open(self.record, 'w')
		self.lavLoaded = 1
		return lines

	# get quiz in bsd mode, choosing file, questions, and answers
	def bsdMode(self):
		self.prevUsrChoice = -1	
		self.quiz = []	
		# get bsd index
		f = open(self.DIR + os.sep + 'index')
		lines = f.readlines()
		f.close()
		lines = self.purge(lines)
		# get bsd file choice
		print "(Available quizzes - 'q' to quit)"
		choice = self.query(lines, 'Enter quiz number: ')
		tokens = string.split(lines[choice],':')
		self.quiz.append(tokens[0])		
		# get question field
		tokens = tokens[1:]
		print "(Available fields)"
		choice = self.query(tokens, 'Choose question field: ')
		self.quiz.append(choice)
		self.prevUsrChoice = choice
		# set answer field
		if (len(tokens) > 2):
			print "(Available fields)"
			choice = self.query(tokens, 'Choose answer field: ')
			self.quiz.append(choice)
		else:
			if (choice == 0):
				self.quiz.append(1)
			else:
				self.quiz.append(0)
		return

	# open the chosen quiz and pull question and answer fields
	def loadQuiz(self, data):
		try:
			while (len(data) > 0):
				data.pop()
			f = open(self.quiz[0],'r')
			lines = f.readlines()
			f.close()
			lines = self.purge(lines)
			lines2 = []
			tmpline = ''
			# get test title if exists
			if ( (lines[0])[0] == '#'):
				title = string.strip(lines[0])
				title = string.strip(string.replace(title,'#',''))
				print '\nCurrent test: ' + title
			# cat '\' continued lines
			for line in lines:
				if (line[0] == '#'):
					continue	
				line = string.strip(line)
				tmplist = list(line)
				tmpline = tmpline + line
				if (tmplist[-1] != '\\'):
					lines2.append(tmpline)
					tmpline = ''
				else:
					tmpline = string.replace(tmpline,'\\','')
			# create list of entries
			for line in lines2:
				entry = []
				tokens = string.split(line,':')
				entry.append(string.strip(tokens[self.quiz[1]]))
				entry.append(string.strip(tokens[self.quiz[2]]))
				data.append(entry)
				self.total = len(data)
		except:
			self.exit('Failure to load test.\nExiting...', 1)
		return

	### ----- Public Interface ----- ###

	# - Lavengro - #
	# load data for Lavengro instance
	def loadData(self, data):
		self.selectQuiz()
		self.loadQuiz(data)
		return 

	# - Pooker - #
	# print reply to user's answers
	def reply(self, answer, correct):
		if ((self.modes[1] == 1) or
			(self.modes[3] ==1)):
			print '   ' + answer + '   ' + `correct` + ':' + \
				  `self.total` + ' correct'
		elif (self.modes[2] == 1):
			print '   ' + answer
		return

	def purge_pending(self, name):
		tmp = []
		for entry in self.pending:
			if (string.find(entry,name) != 0):
				tmp.append(entry)
		self.pending = tmp
		return
		
	# calculate and print test result
	def scoreQuiz(self, correct, responses):
		now = time.time()
		name = os.path.basename(self.quiz[0])
		self.taken.append(name)
		if ((self.modes[1] == 1) or
			(self.modes[3] == 1)):
			score = round( ((correct * 100) / self.total), 0)
			print '\nScore: ' + `score` + '%\n'
			raw_input("Enter to continue")
			if (self.lav != None):
				if (score > 80):
					self.purge_pending(name)
					self.pending.append(name + ':*SCORE*:' + `score` + '\n')
				else:
					self.purge_pending(name)
					self.pending.append(name + ':' + '*TUTOR*:' + `now` + '\n')
		elif (self.modes[2] == 1):
			print '\nScore: ' + `responses` + ' responses to get ' + \
				  `self.total` + ' correct.'
			if ( responses < (1.2 * self.total)):
				level = '*TESTABLE*'
			else:
				level = '*TUTOR*'
			print level + '\n' 
			raw_input("Enter to continue")
			if (self.lav != None):
				self.purge_pending(name)
				self.pending.append(name + ':' + level + ':' + `now` + '\n')
		return

	# app's exit method
	def exit(self, str, int):
		if (self.lav != None):
			for line in self.pending:
				self.lav.write(line)
			for line in self.oldLav:
				name = (string.split(line,':'))[0]
				if not (name in self.taken):
					self.lav.write(line)
			self.lav.close()
		print str
		sys.exit(int)
		return

	# wrapper for raw_input to isolate interface
	def input(self, str):
		return raw_input(str)

	# expose modes[2]
	def isTutor(self):
		return (self.modes[2] == 1)



