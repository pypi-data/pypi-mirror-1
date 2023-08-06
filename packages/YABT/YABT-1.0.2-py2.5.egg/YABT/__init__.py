'''
Module containing the base translation system

In this module you are meant to only use the Translator class.
'''
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

from pkg_resources import resource_stream
import logging
import array
import sys, os.path
from YABT import contextTypes
from YABT import exceptions
from xml.dom import minidom
from xml.parsers.expat import ExpatError
import StringIO
try:
	from psyco.classes import *
except:
	pass
logging.getLogger("YABT").manager.emittedNoHandlerWarning = True
class TranslationRule:
	'''
	This is the base class for translation rules.
	You are not meant to use this directly, but rather use the methods in the Translator class to create rules.
	'''
	def bFirst(self, bContext, aContext):
		return self.beforeContext(bContext) and self.afterContext(aContext)
	def aFirst(self, bContext, aContext):
		return self.afterContext(aContext) and self.beforeContext(bContext)
	def __init__(self, inputClass, focus, beforeContext, afterContext, translation, finalState, contextFactory):
		self.inputClass = inputClass
		self.focus = focus
		self.beforeContextObj=contextFactory.getContext(beforeContext[:2], beforeContext[2:], True)
		self.beforeContext=self.beforeContextObj.search
		self.afterContextObj=contextFactory.getContext(afterContext[:2], afterContext[2:], False)
		self.afterContext=self.afterContextObj.search
		if self.beforeContextObj.priority > self.afterContextObj.priority:
			self.checkContext=self.bFirst
		else:
			self.checkContext=self.aFirst
		self.translation = translation
		self.finalState = finalState

class Translator:
	'''The base translator class
	
	To make use of this you would do something like the following:
	
	>>> brl = Translator()
	>>> brl.loadConfigFile('britishtobrl.xml')
	>>> brl.translateText("hello world", 2, " ", " ")
	u'HELLO _W'
	
	If you forget to do the loadConfigFile call this will not raise an error, but simply no translation will happen.
	The default no rule translation is to insert the character so we would get:
	
	>>> translator().translateText("hello world", 2, " ", " ")
	u'hello world'
	'''
	def __init__(self):
		self.__characterMaps = {}
		self.__groups = {}
		self.__decission = {}
		self.contextFactory = contextTypes.ContextTypeFactory()
		self.logger = logging.getLogger('YABT.Translator')
		if self.logger.level == 0:
			self.logger.setLevel(logging.WARNING)
		if self.logger.isEnabledFor(logging.INFO):
			self.logger.info('Created a translator object')
	def getNumOfGroups(self):
		return len(self.__groups)
	def __addRule(self, inputClass, focus, beforeContext, afterContext, translation, finalState):
		#create the rule
		rule = TranslationRule(inputClass, focus, beforeContext, afterContext, translation, finalState, self.contextFactory)
		#Create the group if necessary and add the rule
		if not self.__groups.has_key(rule.focus[0]):
			self.__groups.update({rule.focus[0]: []})
			if self.logger.isEnabledFor(logging.DEBUG):
				self.logger.debug("Added the group " + focus[0])
		self.__groups[rule.focus[0]].append(rule)
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug("Created rule "+str(inputClass)+","+focus+","+beforeContext+","+afterContext+","+translation+","+str(finalState))
	def __addConnection(self, inputClass, state):
		# Add the inputClass if no decissions have be created for it before
		if not self.__decission.has_key(inputClass):
			self.__decission.update({inputClass: []})
			if self.logger.isEnabledFor(logging.DEBUG):
				self.logger.debug("Added input class " + str(inputClass))
		# Add the state to the inputClass
		self.__decission[inputClass].append(state)
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug("Added state " + str(state) + " to " + str(inputClass))
	def __addCharacterMap(self, original, replacement):
		self.__characterMaps.update({original: replacement})
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug("Added the character mapping from " + original + " to " + replacement)
	def getStates(self):
		states = []
		for inputClass in self.__decission.values():
			for state in inputClass:
				if not state in states:
					states.append(state)
		states.sort()
		return states
	def __noGroupTranslation(self, translateString, currentPosition):
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug("Character error " + translateString[currentPosition])
		return self.noGroupHandler(translateString, currentPosition)
	def noGroupHandler(self, translateString, currentPosition):
		return translateString[currentPosition]
	def __noRuleToApply(self, translateString, currentPosition):
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug("Rule error: cannot match anything around " + translateString[currentPosition] + " in state " + str(self.state))
		return self.noRuleHandler(translateString, currentPosition)
	def noRuleHandler(self, translateString, currentPosition):
		return translateString[currentPosition]
	def __applyRule(self, translateString, currentPosition, ruleToApply):
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug('translating from ' + ruleToApply.focus + ' in state ' + str(self.state) + ' with ' + ruleToApply.translation)
		if ruleToApply.finalState >= 0:
			self.state = ruleToApply.finalState
		return ruleToApply.translation
	def __applyCharacterMap(self, translateString):
		charMaps = self.__characterMaps
		for origChar, replChar in charMaps.iteritems():
			translateString = translateString.replace(origChar, replChar)
		return translateString
	def __beforeContextMatches(self, beforeString, beforeContext):
		return beforeContext(beforeString)
	def __afterContextMatches(self, afterString, afterContext):
		return afterContext(afterString)
	def __ruleMatches(self, translateString, currentPosition, endOfTranslateString, rules):
		# Set up some variables needed by the loop
		ruleNum = 0
		groupLen = len(rules)
		decissions = self.__decission
		state = self.state
		beforeString = translateString[:currentPosition]
		remainingString = translateString[currentPosition:]
		endPos = endOfTranslateString - currentPosition
		while ruleNum < groupLen:
			rule = rules[ruleNum]
			#first check if the rule is in the inputClass
			if state in decissions[rule.inputClass]:
				#now check the focus matches
				if remainingString.startswith(rule.focus, 0, endPos):
					#Check the context
					if rule.checkContext(beforeString, remainingString[len(rule.focus):]):
						#Seems like the rule is valid
						return rule
			ruleNum += 1
		return None
	def __translateText(self, textToTranslate, state, fakeBeforeText, fakeAfterText):
		#set everything up
		self.state = state
		currentPosition = len(fakeBeforeText)
		translateString = fakeBeforeText + textToTranslate + fakeAfterText
		#apply the character mappings
		translateString = self.__applyCharacterMap(translateString)
		#loop over just the textToTranslte part of translateString
		getGroups = self.__groups
		ruleMatches = self.__ruleMatches
		applyRule = self.__applyRule
		translateStringLen = len(translateString)
		translateTo = translateStringLen-len(fakeAfterText)
		#outputList = array.array('u')
		#outputAppend = outputList.fromunicode
		outputList = StringIO.StringIO()
		outputAppend = outputList.write
		while currentPosition < translateTo:
			#get the rules of the group beginning with current character
			try:
				group = getGroups[translateString[currentPosition]]
			except:
				manualTranslateString = self.__noGroupTranslation(translateString, currentPosition)
				outputAppend(manualTranslateString)
				currentPosition += len(manualTranslateString)
				continue
			#Check the rules in group for a match
			ruleToApply = ruleMatches(translateString, currentPosition, translateTo, group)
			if not ruleToApply is None:
				outputAppend(applyRule(translateString, currentPosition, ruleToApply))
				currentPosition = currentPosition + len(ruleToApply.focus)
			else:
				manualTranslateString = self.__noRuleToApply(translateString, currentPosition)
				outputAppend(manualTranslateString)
				currentPosition = currentPosition + len(manualTranslateString)
		output = outputList.getvalue()
		outputList.close()
		return output
	def translateText(self, translateString, state, beforeContext=' ', afterContext=' ', buffered=True, bufferChar='\f'):
		if not state in self.getStates():
			raise exceptions.InvalidStateException("State not defined")
		sys.setcheckinterval(5000)
		translated = u''
		if buffered:
			inputBuffers = [beforeContext]
			inputBuffers.extend(translateString.split(bufferChar))
			inputBuffers.append(afterContext)
			#counter = 2
			self.state = state
			inputLen = len(inputBuffers)
			#prevBuffer = beforeContext
			#curBuffer = inputBuffers[1]
			outputList = [self.__translateText(inputBuffers[i-1], self.state, inputBuffers[i -2], inputBuffers[i]) for i in xrange(2,inputLen)]
			#while counter < len(inputBuffers):
			#	outputList.append(self.__translateText(curBuffer, self.state, prevBuffer, inputBuffers[counter]))
			#	prevBuffer = curBuffer
			#	curBuffer = inputBuffers[counter]
			#	counter+=1
			translated=bufferChar.join(outputList)
		else:
			translated = self.__translateText(translateString, state, beforeContext, afterContext)
		sys.setcheckinterval(100)
		return translated
	def loadConfigFile(self, fileName):
		'''
		This loads a YABT configuration table from a file
		'''
		try:
			# First get the DOM
			configdoc = minidom.parse(fileName).documentElement
		except ExpatError:
			raise exceptions.InvalidTranslationTableException("The file does not seem to be valid XML")
		if self.logger.isEnabledFor(logging.INFO):
			self.logger.info("Translation table " + fileName + " is valid XML")
		self.__loadConfig(configdoc)
	def loadConfigString(self, configString):
		try:
			configdoc = minidom.parseString(configString).documentElement
		except ExpatError:
			raise Exceptions.InvalidTranslationTableException("The string is not valid XML of a translation table")
		if self.logger.isEnabledFor(logging.INFO):
			self.logger.info("Translation table is valid XML")
		self.__loadConfig(configdoc)
	def __loadConfig(self, configdoc):
		# Now get the meta data section, should be the first one only
		metadata_section = configdoc.getElementsByTagName('metadata')[0]
		# At the moment we only get the YABT_custom_matches from this
		cmatches = {}
		for node in metadata_section.getElementsByTagName('YABT_custom_matches')[0].childNodes:
			if node.nodeName != '#text':
				cmatches.update({node.nodeName: getTextContent(node)})
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug(str(len(cmatches)) + " custom character match groups created")
		self.contextFactory.setCustomMatches(cmatches)
		# Now get the YABT section
		yabt_sections = configdoc.getElementsByTagName('YABTdata')
		# We may have more than one for some reason (unknown to me)
		for datasection in yabt_sections:
			# Now go through the nodes deciding what to do
			for node in datasection.childNodes:
				if node.nodeName == 'charmap':
					self.__addCharacterMap(getTextContent(node.childNodes[0]), 
						getTextContent(node.childNodes[1]))
					if self.logger.isEnabledFor(logging.DEBUG):
						self.logger.debug("Added char map from line " + node.toxml())
				elif node.nodeName == 'decission':
					inputclass = node.attributes['inputclass'].childNodes[0].wholeText
					for state in node.attributes['states'].childNodes[0].wholeText.split(','):
						self.__addConnection(int(inputclass), int(state))
					if self.logger.isEnabledFor(logging.DEBUG):
						self.logger.debug("Added decission " + node.toxml())
				if node.nodeName == 'rule':
					self.__addRule(int(node.childNodes[0].childNodes[0].wholeText),
						getTextContent(node.childNodes[1]),
						getTextContent(node.childNodes[2]),
						getTextContent(node.childNodes[3]),
						getTextContent(node.childNodes[4]),
						int(node.childNodes[5].childNodes[0].wholeText))
					if self.logger.isEnabledFor(logging.DEBUG):
						self.logger.debug("Added rule from " + node.toxml())
		if self.logger.isEnabledFor(logging.INFO):
			self.logger.info("Finished loading translation table")

def getTextContent(node):
	'''getTextContent(node) - Gets the text content of a node. Any childNodes with nodeName char will be 
converted to characters of ordinal given by the ord attribute.'''
	outtext=u''
	if not node.hasChildNodes():
		return u''
	for child in node.childNodes:
		if child.nodeName == '#text':
			outtext+=child.nodeValue
		elif child.nodeName == 'char':
			outtext+=unichr(int(child.attributes['ord'].childNodes[0].nodeValue))
	return outtext




