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
    addDecission: Add a decission mapping
    addRule: Add a rule to the translator
    load: Load a loader object
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

    def addDecission(self, inputClass, state):
        """
        Adds a mapping of the input class to the state

        Arguments are:
        inputClass: the input class
        state: the state to add to the input class

        """
        raise NotImplementedError("Abstract class")

    def addRule(self, iclass, focus, bfcontext, afcontext, trans, fstate):
        """
        Add a rule to the translator

        Arguments are:
        iclass: The input class defining which states the rule can apply
        focus: The text to be translated by the rule
        bfcontext: The context object to match the text before the focus
        afcontext: The context object to match the text after the focus
        trans: The translation of the focus
        fstate: The state to leave the translator in

        """
        raise NotImplementedError("Abstract class")

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
    addDecission: Add a decission mapping to the translator.
    addCharacterMap: Add a character mapping to the translator.
    getStates: Show all valid states for the translator.
    load: Load translation table from loader
    translate: perform translation

    """

    class _Rule:
        """Private class used to represent a rule"""
        def __init__(self, iclass, focus, bfcontext, afcontext, trans, fstate):
            if not isinstance(focus, basestring):
                raise TypeError("Focus must be str or unicode not " +
                                focus.__class__.__name__)
            if not isinstance(trans, basestring):
                raise TypeError("Translation must be str or unicode not " +
                                trans.__class__.__name__)
            self.inputClass = iclass
            self.focus = unicode(focus)
            if bfcontext.priority < afcontext.priority:
                self.context = (afcontext, bfcontext)
            else:
                self.context = (bfcontext, afcontext)
            self.translation = unicode(trans)
            self.finalState = fstate
        def ruleMatch(self, state, text, start, end):
            """Method to check whether the rule can be applied"""
            if state in self.inputClass:
                if text.startswith(self.focus, start, end):
                    focusEnd = start + len(self.focus)
                    if self.context[0].match(text, start, focusEnd):
                        if self.context[1].match(text, start, focusEnd):
                            return True
            return False

    def __init__(self):
        """Create a new YABT translator object"""
        self._logger = logging.getLogger("YABT.translators.Translator")
        if self._logger.level == 0:
            self._logger.setLevel(logging.WARNING)
        self._charMaps = {}
        self._inputClasses = {}
        self._rules = {}
        self.state = 0

    def addRule(self, iclass, focus, bfcontext, afcontext, trans, fstate):
        """
        A method to add a rule to the translator

        Arguements are as follows in this order:
        iclass: The input class.
        focus: The focus.
        bfcontext: The before context object.
        afcontext: The after context object.
        trans: The translation of the focus.
        fstate: The state the translator should be left in after applying the rule.
        Set fstate to -1 should the state not change when the rule is applied.

        """
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info("Adding rule " + str(iclass) + ", " +
                               focus + ", " + str(bfcontext) + ", " +
                               str(afcontext) + ", " + trans + ", " +
                               str(fstate) + " to translator.")
        if not self._rules.has_key(focus[0]):
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug("Adding group " + focus[0])
            self._rules.update({focus[0]: []})
        self._rules[focus[0]].append(self._Rule(self._inputClasses[iclass],
                                                focus, bfcontext, afcontext,
                                                trans, fstate))

    def addDecission(self, iclass, state):
        """
        Adds a decission mapping to the translator

        The arguements are:
        iclass: The input class.
        state: The state to add to the input class.

        """
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info("Adding input class " + str(iclass) + 
                               " to state " + str(state))
        if not self._inputClasses.has_key(iclass):
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug("Adding class " + str(iclass) + 
                                    " to translator")
            self._inputClasses.update({iclass: []})
        self._inputClasses[iclass].append(state)

    def addCharacterMap(self, orig, repl):
        """
        Adds a character mapping to the translator

        Arguements are:
        orig: The original character.
        repl: the character to replace orig with.

        """
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info("Adding charmap from " + orig + " to " + repl)
        self._charMaps.update({orig: repl})

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

        Arguements are:
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
            try:
                group = self._rules[fullText[position]]
            except KeyError:
                output.fromunicode(fullText[position])
                position += 1
                continue
            rule = None
            for rule in group:
                if rule.ruleMatch(state, fullText, position, end):
                    break
            else:
                output.fromunicode(fullText[position])
                position += 1
                continue
            output.fromunicode(rule.translation)
            if rule.finalState != -1:
                state = rule.finalState
            position += len(rule.focus)
        self.state = state
        return output.tounicode()

    def getStates(self):
        """Get a set of the states valid for this translator"""
        states = set()
        for iclass in self._inputClasses.values():
            states.update(iclass)
        return states

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
        takes the same arguements as the translate method of the Translator
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
