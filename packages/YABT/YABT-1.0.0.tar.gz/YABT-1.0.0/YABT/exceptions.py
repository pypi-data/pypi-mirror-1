'''This module provides the exception classes for YABT'''

class InvalidTranslationTableException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class InvalidStateException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

