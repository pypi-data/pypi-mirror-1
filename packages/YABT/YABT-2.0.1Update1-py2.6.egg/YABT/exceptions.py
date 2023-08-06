"""
This module provides the exception classes for YABT

InvalidStateException: Exception to indicate that the state does not exist
InvalidTranslationTableException: Indicates that the table does not
conform to the format.

"""

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

