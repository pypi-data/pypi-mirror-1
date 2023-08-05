# Pooker.py  Copyright Richard Harris 2002
#
# Pooker means "to ask" in Romany. This is the
# quiz-parsing and -executing engine for Lavengro.
#
# author: Richard Harris (truenolejano@yahoo.com)
# The author releases this file under the GPL
# license. See COPYING for specifics.
#
# created: 12apr02
# change log:
# (1) 28apr02 mark wrong answers in tutor mode
# (2) 17jun03 debug code
#
import string, whrandom

class Pooker:

	def __init__(self, mooi, debug):
		self.debug = debug
		self.correct = 0
		self.data = []
		self.mooi = mooi
		self.responses = 0
		self.retest = []
		return

	def save(self,list):
		tmp = ''
		retval = []
		for entry in list:
			tmp = string.replace(entry,'\\[','=ls=')
			tmp = string.replace(tmp,'\\]','=rs=')
			tmp = string.replace(tmp,'\\{','=lc=')
			tmp = string.replace(tmp,'\\}','=rc=')
			retval.append(tmp)
		return retval

	def restore(self,list):
		tmp = ''
		retval = []
		for entry in list:
			tmp = string.replace(entry,'=ls=','[')
			tmp = string.replace(tmp,'=rs=',']')
			tmp = string.replace(tmp,'=lc=','{')
			tmp = string.replace(tmp,'=rc=','}')
			retval.append(tmp)
		return retval

	# expand answer to alternate answers (see `man quiz`)
	def expand(self, element):
		retval = ['']
		tmp = []
		mark = 0
		last = 0
		brace = 0
		bracket = 0
		previous = []
		chars = element[0]
		for i in range(0, len(chars)):
			if (chars[i] == '|'):
				mark = len(retval)
				if (not bracket):
					last = len(retval)
					retval.append('')
				else:
					retval = retval + tmp
			elif (chars[i] == '['):
				previous.append(mark)
				bracket = bracket + 1
				tmp = retval[mark:]
			elif (chars[i] == ']'):
				bracket = bracket - 1
				mark = previous[-1]
				previous = previous[:-1]
			elif (chars[i] == '{'):
				previous.append(mark)
				brace = brace + 1
				add = retval[mark:]
				mark = len(retval)
				retval = retval + add
			elif (chars[i] == '}'):
				brace = brace - 1
				mark = previous[-1]
				previous = previous[:-1]
			else:
				for j in range(mark, len(retval)):
					retval[j] = retval[j] + chars[i]
		return retval

	# detect | or {, get all possible answers, get longest question
	def process(self, entry):
		slashes = 0
		answer = []
		question = []
		# save escaped control chars
		if ((string.find(entry[0],'\\') != -1) or
			(string.find(entry[1],'\\') != -1)):
			slashes = 1
			entry = self.save(entry)
		# if more than one question, get longest
		question.append(entry[0])
		if ((string.find(question[0],'|') != -1) or
			(string.find(question[0],'{') != -1)):
			tmp = self.expand(question)
			question[0] = tmp[0]
			for i in range(1, len(tmp)):
				if (len(tmp[i]) > len(question[0])):
					question[0] = tmp[i]
		# get all possible answers
		answer.append(entry[1])
		if ((string.find(answer[0],'|') != -1) or
			(string.find(answer[0],'{') != -1)):
			answer = self.expand(answer)
		# return expanded entry
		retval = question + answer
		if slashes:
			retval = self.restore(retval)
		return retval

	# ask question, process answer
	def doEntry(self, entry):
		wrong = 1
		current = self.process(entry)
		answer = current[1]
		response = self.mooi.input( 'Q: ' + current[0] + '\nA: ' )
		if (response == 'q'):
			self.mooi.exit(' ', 0)
		self.responses = self.responses + 1
		for i in range(1, len(current)):
			if (response == current[i]):
				self.correct = self.correct + 1
				wrong = 0
				answer = current[i]
				break
		if ((self.tutor) and wrong):
			self.retest.append(entry)
		if wrong:
			answer = answer + '   -X-'	# (1)
		self.mooi.reply(answer, self.correct)
		return

	# randomly go through list of questions, repeat in tutor mode
	def doQuiz(self, data):
		self.correct = 0
		self.data = data
		self.responses = 0
		testing = 1
		self.tutor = self.mooi.isTutor()
		while (testing == 1):
			choice = -1
			chosen = [-1]
			length = len(self.data)
			while (len(chosen) <= length):
				while choice in chosen:
					choice = whrandom.randint(0,length-1)
				chosen.append(choice)
				self.doEntry(self.data[choice])
			if (len(self.retest) > 0):
				self.data = self.retest
				self.retest = []
			else:
				testing = 0
		self.mooi.scoreQuiz(self.correct, self.responses)
		return
