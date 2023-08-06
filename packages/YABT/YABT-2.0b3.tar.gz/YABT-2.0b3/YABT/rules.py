"""
This module provides the classes for rules

BaseRule: An abstract class which all rule like classes should inherit from
RuleSet: A basic class for rule sets, not intended to be used directly.
GeneralContextRule: A rule to match nearly any context
GroupStateRuleSet: This groups its rules by group and state

"""

try:
    from psyco.classes import psyobj
except ImportError:
    class psyobj(object):
        def __init__(self):
            """Initialize psyobj stand in class"""
            object.__init__(self)

class BaseRule(psyobj):
    """Abstract class for all rule like objects to inherit"""

    def __init__(self):
        """Should not be used to create an object, only for subclasses"""
        super(BaseRule, self).__init__()
    def isMatch(self, state, text, position, end):
        """
        Determines whether this rule can match. If this rule matches it
        returns the rule object otherwise returns None.
        """
        raise NotImplementedError("Abstract class")

class RuleSet(BaseRule):
    """
    This is a basic rule set, it will check whether any of its rules matches,
    it does no condition checking itself, so is mainly useful fo a super class to more advanced rule sets

    """
    def __init__(self):
        """Create a basic rule set"""
        BaseRule.__init__(self)
        self.__ruleSet = []

    def findRule(self, state, text, position, end):
        """
        This finds the first matching rule, it is intended to be called from
        this class or a subclass

        """
        for rule in self.__ruleSet:
            matchingRule = rule.isMatch(state, text, position, end)
            if not matchingRule is None:
                return matchingRule
        return None

    def addRule(self, rule):
        """Add a rule to the rule set"""
        self.__ruleSet.append(rule)

    def isMatch(self, state, text, position, end):
        """
        Finds the first matching rule of the set and returns it. If no
        match is found then None is returned.

        """
        return self.findRule(state, text, position, end)

class GeneralContextRule(BaseRule):
    """
    Rule to check whether the current position matches the focus and that the
    context matches. Nearly any context should be possible to specify.

    """
    def __init__(self, focus, bfcontext, afcontext, trans, fstate):
        """Create a general context rule"""
        super(GeneralContextRule, self).__init__()
        self.focus = focus
        self.translation = trans
        self.finalState = fstate
        if bfcontext.priority < afcontext.priority:
            self.__context = (afcontext, bfcontext)
        else:
            self.__context = (bfcontext, afcontext)

    def isMatch(self, state, text, position, end):
        """
        Checks whether this rule actually matches. If it matches it returns
        itself otherwise returns None

        """
        if text.startswith(self.focus, position, end):
            focusEnd = position + len(self.focus)
            if self.__context[0].match(text, position, focusEnd):
                if self.__context[1].match(text, position, focusEnd):
                    return self
        return None

class GroupStateRuleSet(psyobj):
    """This rule set groups rules according to group and state all in one"""
    def __init__(self):
        """Create a group and state rule set"""
        super(GroupStateRuleSet, self).__init__()
        self.__groups = {}
    def addRule(self, rule, group):
        """
        Add a rule to the group

        Arguments are:
        rule: The rule to add
        group: this is the group and state the rule belongs to in a tuple

        """
        if not group in self.__groups:
            self.__groups.update({group: []})
        self.__groups[group].append(rule)

    def isMatch(self, state, text, position, end):
        """Find the rule or return None if no rule matches"""
        group = text[position]
        if not (group, state) in self.__groups:
            return None
        for rule in self.__groups[(group, state)]:
            selectedRule = rule.isMatch(state, text, position, end)
            if not selectedRule is None:
                return selectedRule
        return None

class WordDictRule(BaseRule):
    """This class provides a rule to find words from a dictionary"""

    def __init__(self):
        """Create a blank word dictionary rule"""
        super(WordDictRule, self).__init__()
        self._words = {}

    def isMatch(self, state, text, position, end):
        """Checks for a matching word"""
        self.focus = None
        self.translation = None
        self.finalState = state
        # Check that we are at the beginning of a word
        if text[position - 1].isalpha():
            return None
        # Find the length of the word at position
        index = position
        word = ""
        while index < end:
            if not text[index].isalpha():
                word = text[position:index]
                break
            index += 1
        try:
            self.translation = self._words[state][word]
        except KeyError:
            return None
        else:
            self.focus = word
            return self
        return None

    def addWord(self, state, orig, repl):
        """Add a word to the dictionary"""
        if not state in self._words:
            self._words.update({state: {}})
        self._words[state].update({orig: unicode(repl)})

