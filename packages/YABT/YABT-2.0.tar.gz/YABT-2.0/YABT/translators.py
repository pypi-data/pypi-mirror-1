"""
This module contains the actual Translator class

BaseTranslator: The super class for all translator classes
Translator: The actual class for doing text translation.
BufferedTranslator: A varient of Translator which performs faster for long text.

"""

import logging
import array
try:
    from psyco.classes import *
except ImportError:
    class psyobj(object):
        pass

from YABT.exceptions import *

logging.getLogger("YABT.translators").manager.emittedNoHandlerWarning = True

class BaseTranslator(psyobj):
    """
    The super class for all translator classes

    Methods are:
    addCharacterMap: Add a character mapping
    addState: Add a state to the known list of states
    addRule: Add a rule to the translator
    load: Load a loader object
    noRuleHandler: A handler method called when a group exists but no rule
    matches.
    getStates: Get a list of states which exist in the translator
    translate: Perform a translation

    """

    def addCharacterMap(self, orig, repl):
        """
        Add a character mapping to the translator

        Arguments are:
        orig: the original character
        repl: the replacement character

        """
        raise NotImplementedError("Class is abstract")

    def addState(self, state):
        """
        Adds a state to the list of known states

        Arguments are:
        state: the state

        """
        raise NotImplementedError("Abstract class")

    def addRule(self, rule):
        """
        Add a rule to the translator

        Arguments are:
        rule: The rule or rule set to add

        """
        raise NotImplementedError("Abstract class")

    def noRuleHandler(self, state, text, start, end):
        """
        Method called when no rule matches

        Arguments are:
        state: The state of the translator
        text: The text being translated
        start: The index of where the focus should begin
        end: Where the focus must end by.

        """
        raise NotImplementedError("Abstract method should be overridden")

    def load(self, loader):
        """
        Load the translation table from the loader

        Arguments are:
        loader: The loader to load the translation table

        """
        raise NotImplementedError("Abstract class")

    def getStates(self):
        """Return a list of the states in this translator"""
        raise NotImplementedError("Abstract class")

    def translate(self, inText, state, bfcontext, afcontext):
        """
        Perform the translation

        Arguments are:
        inText: the text to be translated
        state: The state to start the translator in
        bfcontext: The text which would appear before inText in the source
        afcontext: The text which would appear after inText in the source

        """
        raise NotImplementedError("Abstract class")

class Translator(BaseTranslator):
    """
    The class for doing text translation

    addRule: A method to add a rule to the translator.
    addState: adds a state to the list of known states
    addCharacterMap: Add a character mapping to the translator.
    getStates: Show all valid states for the translator.
    load: Load translation table from loader
    translate: perform translation

    """

    def __init__(self):
        """Create a new YABT translator object"""
        self._logger = logging.getLogger("YABT.translators.Translator")
        if self._logger.level == 0:
            self._logger.setLevel(logging.WARNING)
        self._charMaps = {}
        self._rules = []
        self.state = 0
        self._states = set()

    def addRule(self, rule):
        """
        A method to add a rule to the translator

        Arguments are:
        rule: The rule or rule set object to add

        """
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info("Adding rule " + str(rule) + " to translator.")
        self._rules.append(rule)

    def addState(self, state):
        """
        Adds a state to the known states

        Arguments are:
        state: The state to add

        """
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info("Adding state " + str(state))
        self._states.add(state)

    def addCharacterMap(self, orig, repl):
        """
        Adds a character mapping to the translator

        Arguments are:
        orig: The original character.
        repl: the character to replace orig with.

        """
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info("Adding charmap from " + orig + " to " + repl)
        self._charMaps.update({orig: repl})

    def noRuleHandler(self, state, text, start, end):
        """
        This implementation simply inserts the character into the output
        without altering the state

        """
        return (text[start], 1, state)

    def load(self, loader):
        """
        Loads a translation table from a loader

        Arguments are:
        loader: The loader object to load the translation table from

        """
        loader.load(self)

    def translate(self, text, state, bfcontext=" ", afcontext=" "):
        """
        Performs the actual translation

        Arguments are:
        text: The text to translate
        state: The state to start the translation in.
        bfcontext: The text which is before the translation text, this is not
        actually translated.
        afcontext: The text which is after the translation text, this is not
        actually translated.

        """
        if not state in self.getStates():
            raise InvalidStateException("State " + str(state) + " not found")
        output = array.array("u")
        position = len(bfcontext)
        end = position + len(text)
        fullText = u"".join([bfcontext, text, afcontext])
        for orig, repl in self._charMaps.iteritems():
            fullText = fullText.replace(orig, repl)
        while position < end:
            selectedRule = None
            for rule in self._rules:
                selectedRule = rule.isMatch(state, fullText, position, end)
                if not selectedRule is None:
                    break
            else:
                noRuleInfo = self.noRuleHandler(state, fullText, position, end)
                output.fromunicode(noRuleInfo[0])
                position += noRuleInfo[1]
                if noRuleInfo[2] != -1:
                    state = noRuleInfo[2]
                continue
            output.fromunicode(selectedRule.translation)
            if selectedRule.finalState != -1:
                state = selectedRule.finalState
            position += len(selectedRule.focus)
        self.state = state
        return output.tounicode()

    def getStates(self):
        """Get a set of the states valid for this translator"""
        return self._states

class BufferedTranslator(Translator):
    """
    A performance enhanced version of Translator

    This class improves on performance by splitting the input text into
    lines and processing each line independently. While this improves
    performance, you should note the following:
    As each line is processed separately, no rule which spans more than one
    line can be applied
    Whilst this generally improves performance in some cases it may
    cause a negative impact on performance, eg. those cases where only very short
    blocks of text are being translated

    This class implements the same interface as the Translator class

    """

    def translate(self, text, state, bfcontext=' ', afcontext=' '):
        """
        This performs the translation

        This method performs translation on the input text passed in. This method
        takes the same arguments as the translate method of the Translator
        class. This method probably should perform better than the one in
        Translator, but please make note of the limitations mentioned in the
        class doc string.

        """
        self.state = state
        output = array.array('u')
        inputList = text.splitlines(True)
        inputList.insert(0, bfcontext)
        inputList.append(afcontext)
        beforeContext = inputList[0]
        translateText = inputList[1]
        for afterContext in inputList[2:]:
            output.fromunicode(super(BufferedTranslator,
                                    self).translate(translateText,
                                                    self.state, beforeContext,
                                                    afterContext))
            beforeContext = translateText
            translateText = afterContext
        return output.tounicode()
