'''This contains classes for the different context types for translation rules'''
# Copyright (C) 2007 Michael Whapples, All Rights Reserved.
# Original Author: Michael Whapples, mwhapples@users.sourceforge.net
# Unless linsor has explicitly granted you any other licensing terms, the contents of this file is subject to the RPL 1.1,
# available at the BrlTex website (http://brltex.sourceforge.net).
# All software distributed under the Licenses is provided strictly on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, AND the licensor
# HEREBY DISCLAIMS ALL SUCH WARRANTIES, INCLUDING WITHOUT LIMITATION, ANY WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, QUIET ENJOYMENT, OR NON-INFRINGEMENT.
# Licensor reserves the right to change the Venue stated in the license to the UK.
# 

import re
import string
import sys
try:
	from psyco.classes import *
except:
	pass


class ContextSuper:
	def __init__(self, pattern):
		self.pattern = pattern

class ContextA(ContextSuper):
	def search(self, context):
		return True

class ContextCBefore(ContextSuper):
	def search(self, context):
		return context[-1] in self.pattern

class ContextCAfter(ContextSuper):
	def search(self, context):
		return context[0] in self.pattern

class ContextTBefore(ContextSuper):
	def search(self, context):
		return context.endswith(self.pattern)

class ContextTAfter(ContextSuper):
	def search(self, context):
		return context.startswith(self.pattern)

class ContextR(ContextSuper):
	def __init__(self, pattern):
		self.pattern = pattern
		self.compiled = re.compile(pattern)
	def search(self, context):
		if self.compiled.search(context):
			return True
		else:
			return False

class ContextTypeFactory:
	def __init__(self):
		self.__customMatches = {}
	def getContext(self, type, pattern, before):
		if type == '^r':
			if before == True:
				contextObject = ContextR(pattern + '$')
			else:
				contextObject = ContextR('^' + pattern)
		elif type == '^a':
			contextObject = ContextA(pattern)
		elif type == '^t':
			if before:
				contextObject = ContextTBefore(pattern)
			else:
				contextObject = ContextTAfter(pattern)
		elif type == '^c':
			if before:
				contextObject = ContextCBefore(self.__customMatches[pattern])
			else:
				contextObject=ContextCAfter(self.__customMatches[pattern])
		#We should check that the search function is actually valid
		#This need not actually match, so long as it doesn't give an error
		try:
			contextObject.search(u'h')
			return contextObject
		except:
			pass
	def setCustomMatches(self, cmatches):
		self.__customMatches = cmatches
	def getCustomMatches(self):
		return self.__customMatches

