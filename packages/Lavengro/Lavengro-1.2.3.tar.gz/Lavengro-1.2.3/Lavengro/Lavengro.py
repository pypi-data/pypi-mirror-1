# Lavengro.py  Copyright Richard Harris 2002
#
# author: Richard Harris (richardharris@operamail.com)
# The author releases this file under the GPL
# license. See COPYING for specifics.
#
# created: 23 Mar 02
#
import os, string, sys, time, traceback
import Mooi, Pooker

class Lavengro:
	NAME = "Lavengro"
	LOG_EXC = os.path.expandvars("$HOME/Lavengro.error.log")
	MSG_EXC = 'Exiting on unforeseen exception.'
	USAGE = '\nusage: python Lavengro.py\n'

	def __init__(self):
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
		self.debug = 'debug' in self.options
		self.mooi = Mooi.Mooi(self.debug)
		self.pooker = Pooker.Pooker(self.mooi, self.debug)
		self.data = []
		return

	def exc(self, exit=0):
		if (self.debug):
			raise
		else:
			info = sys.exc_info()
			error = traceback.format_exception_only(info[0],info[1])
			f = open(self.LOG_EXC,'a')
			f.write(self.NAME+": "+string.strip(error[0])+": "+time.ctime(time.time())+"\n")
			f.close()
			if (exit):
				print self.MSG_EXC
				sys.exit()
		return

	def usage(self):
		usage = 0
		if (('h' in self.options) or
			('?' in self.options)):
			usage = 1
		if usage:
			print self.USAGE
			sys.exit(1)
		return

	def run(self):
		self.usage()
		try:
			while (1):
				self.mooi.loadData(self.data)
				self.pooker.doQuiz(self.data)
		except SystemExit:
			pass
		except:
			self.exc(1)
		return

#-----------------main
obj = Lavengro()
obj.run()






