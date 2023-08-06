"""
This module contains the basic context types for YABT

Classes:
ContextFactory: This is a factory class for context objects
ContextSuper: This class should be the super class to all contextObjects
All other classes are only for internal use and only need be known to other
classes as implementations of ContextSuper.

"""

import re

try:
    from psyco.classes import *
except ImportError:
    class psyobj(object):
        pass

class ContextSuper(psyobj):
    """
    This is the super class that all context objects should implement

    This class is an abstract class which all context objects should implement.
    Subclasses should override the following:
    __init__(self, pattern): This constructor is the one called by the factory
    class. The pattern argument is the string used to specify how this context
    object should match.
    match(self, text, start, end): This method is called to check whether the
    context matches. The text argument is the complete string, start is the
    start index of the focus and end is the index of the end of the focus
    (IE. text[start:end] should give the focus).

    """
    
    def match(self, text, start, end):
        """Abstract method to check whether the context matches"""
        raise NotImplementedError

    def __init__(self, pattern):
        """Create a context object with the given pattern"""
        self.pattern = pattern
        self.priority = 0

class ContextA(ContextSuper):
    """This is a context type for all contexts to match"""
    def match(self, text, start, end):
        """Returns True regardless of the actual context"""
        return True

class ContextCSuper(ContextSuper):
    """This is the super class for custom match contexts"""
    def __init__(self, pattern):
        """This class is abstract, this merely partially sets up"""
        ContextSuper.__init__(self, pattern)
        self.priority = 2
    def match(self, text, start, end):
        """Reports whether the context matches"""
        raise NotImplementedError
class ContextCBefore(ContextCSuper):
    """Checks if the character before is in the list of characters"""
    def match(self, text, start, end):
        """Only matches if the adjacent character is in the custom list"""
        return text[start - 1] in self.pattern

class ContextCAfter(ContextCSuper):
    def match(self, text, start, end):
        return text[end] in self.pattern

class ContextTSuper(ContextSuper):
    def __init__(self, pattern):
        ContextSuper.__init__(self, pattern)
        self.priority = 3

class ContextTBefore(ContextTSuper):
    def match(self, text, start, end):
        return text.endswith(self.pattern, 0, start)

class ContextTAfter(ContextTSuper):
    def match(self, text, start, end):
        return text.startswith(self.pattern, end)

class ContextRBefore(ContextSuper):
    def __init__(self, pattern):
        ContextSuper.__init__(self, pattern + "$")
        self._compiled = re.compile(self.pattern)
        self.priority = 1
    def match(self, text, start, end):
        if self._compiled.search(text, 0, start):
            return True
        else:
            return False

class ContextRAfter(ContextSuper):
    def __init__(self, pattern):
        ContextSuper.__init__(self, "^" + pattern)
        self._compiled = re.compile(self.pattern)
        self.priority = 1
    def match(self, text, start, end):
        if self._compiled.search(text, end):
            return True
        else:
            return False

class ContextFactory:
    """
    This class creates the requested context object

    Methods are:
    getContextInstance: this is the method called to get a context object.
    addContextType: Adds a context type to the factory.

    """

    BEFORE = 0
    AFTER = 1
    def __init__(self):
        """Create a ContextFactory for getting context objects"""
        self._contextObjects = {}
        self._contextTypes = {"^a": (ContextA, ContextA),
                               "^c": (ContextCBefore, ContextCAfter),
                               "^t": (ContextTBefore, ContextTAfter),
                               "^r": (ContextRBefore, ContextRAfter)}

    def addContextType(self, name, before, after):
        """
        Add a new context type to the context factory

        Arguments are:
        name: The string used to identify the type
        before: The class to be used for before contexts
        after: The class to be used for after contexts

        """
        self._contextTypes.update({name: (before, after)})

    def getContextInstance(self, ctType, pattern, position):
        """
        This method will create a context object according to arguments

        Arguments are:
        type: The string to identify the type to be created
        pattern: The string which defines how the context should match
        position: This should be one of ContextFactory.BEFORE or
        ContextFactory.AFTER

        """
        try:
            obj = self._contextObjects[(ctType, pattern, position)]
        except KeyError:
            obj = self._contextTypes[ctType][position](pattern)
            self._contextObjects.update({(ctType, pattern, position): obj})
        return obj
