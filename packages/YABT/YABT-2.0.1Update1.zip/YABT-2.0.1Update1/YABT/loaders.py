"""
YABT.loaders: a module containing various YABT loader classes

BaseLoader: The class that all loaders should inherit from.
BasicXMLFileLoader: A loader which can load XML files.
BasicXMLStringLoader: A loader to load from a XML string.

"""

from xml.parsers import expat
try:
    from psyco.classes import *
except ImportError:
    class psyobj(object):
        pass

from YABT.basicContextTypes import ContextFactory
from YABT.exceptions import InvalidTranslationTableException
from YABT.rules import GroupStateRuleSet, GeneralContextRule, WordDictRule

class BaseLoader(psyobj):
    """
    This is the abstract class which all loaders should inherit from.
    
    setInput: Set the input source this class should load the table from.
    getInput: Return the input to be used for loading the information from.
    load: load the data into the translator.
    
    """

    def __init__(self):
        """Do not use this as BaseLoader is abstract"""
        super(BaseLoader, self).__init__()
        self._translator = None
        self._input = None

    def setInput(self, inputSource):
        """Set the input source to load the translation table from"""
        self._input = inputSource
    
    def getInput(self):
        """Return the input source for loading the information from"""
        return self._input

    def load(self, translator):
        """Load the translation information into the translator"""
        raise NotImplementedError("Use an actual implementation class")


class BasicXMLFileLoader(BaseLoader):
    """
    A loader to load basic XML translation tables from file

    All methods are as for BaseLoader, except for the below:
    setInput: This takes a file object of a XML file
    load: Overrides load from BaseLoader with an actual implementation
    _startElement: This method is called when the XML parser encounters
    a start tag. This method should only be used by subclasses which override this
    method and require the functionality.
    _endElement: This method is called when the XML parser encounters
    a end tag. This should only be used by subclasses.
    _characterData: This method is called when the XML parser encounters a 
    text element. This should be used only by subclasses.

    """

    def __init__(self, inputsrc=None):
        """Initialises a BasicXMLFileLoader"""
        BaseLoader.__init__(self)
        self.setInput(inputsrc)
        self.contextFactory = ContextFactory()
        self.customMatches = {}
        self._path = ""
        self._iclass = None
        self._trans = None
        self._bfcontext = None
        self._afcontext = None
        self._focus = None
        self._fstate = None
        self._tmpMatch = None
        self._tmpMatchName = None
        self._orig = None
        self._repl = None
        self.__decisions = {}
        self._rules = GroupStateRuleSet()

    def load(self, translator):
        """Load the XML file which has been set into the translator"""
        self._translator = translator
        self.customMatches = {}
        parser = expat.ParserCreate()
        parser.StartElementHandler = self._startElement
        parser.EndElementHandler = self._endElement
        parser.CharacterDataHandler = self._characterData
        try:
            parser.ParseFile(self.getInput())
        except expat.ExpatError:
            raise InvalidTranslationTableException("Table is not valid")
        self.getInput().seek(0)
    def _startElement(self, name, attrs):
        """Method called when a start tag is encountered"""
        self._path += "." + name
        if name == "char":
            self._characterData(unichr(int(attrs["ord"])))
        elif self._path == ".transtable.YABTdata.charmap":
            self._orig = None
            self._repl = None
        elif self._path == ".transtable.YABTdata.charmap.orig":
            self._orig = ""
        elif self._path == ".transtable.YABTdata.charmap.repl":
            self._repl = ""
        elif self._path == ".transtable.YABTdata.decision":
            iclass = int(attrs["inputclass"])
            if not iclass in self.__decisions:
                self.__decisions.update({iclass: set()})
            for state in attrs["states"].split(","):
                self.__decisions[iclass].add(int(state))
                self._translator.addState(int(state))
        elif self._path == ".transtable.YABTdata.rule":
            self._iclass = None
            self._focus = None
            self._bfcontext = None
            self._afcontext = None
            self._trans = None
            self._fstate = None
        elif self._path == ".transtable.YABTdata.rule.iclass":
            self._iclass = ""
        elif self._path == ".transtable.YABTdata.rule.focus":
            self._focus = ""
        elif self._path == ".transtable.YABTdata.rule.bfcontext":
            self._bfcontext = ""
        elif self._path == ".transtable.YABTdata.rule.afcontext":
            self._afcontext = ""
        elif self._path == ".transtable.YABTdata.rule.trans":
            self._trans = ""
        elif self._path == ".transtable.YABTdata.rule.fstate":
            self._fstate = ""
        elif self._path.startswith(".transtable.metadata.YABT_custom_matches."):
            self._tmpMatchName = name
            self._tmpMatch = ""

    def _endElement(self, name):
        """Method called when an end tag is encountered"""
        if name == "char":
            pass
        elif self._path == ".transtable.YABTdata.charmap":
            self._translator.addCharacterMap(self._orig, self._repl)
        elif self._path == ".transtable.YABTdata.rule":
            self._addRule()
        elif self._path.startswith(".transtable.metadata.YABT_custom_matches."):
            self.customMatches.update({self._tmpMatchName: self._tmpMatch})
        elif self._path == ".transtable":
            self._translator.addRule(self._rules)
        self._path = self._path[:-1 - len(name)]

    def _characterData(self, data):
        """Method called when a text element is encountered"""
        if self._path == ".transtable.YABTdata.charmap.orig":
            self._orig += data
        elif self._path == ".transtable.YABTdata.charmap.repl":
            self._repl += data
        elif self._path == ".transtable.YABTdata.rule.iclass":
            self._iclass += data
        elif self._path == ".transtable.YABTdata.rule.focus":
            self._focus += data
        elif self._path == ".transtable.YABTdata.rule.bfcontext":
            self._bfcontext += data
        elif self._path == ".transtable.YABTdata.rule.afcontext":
            self._afcontext += data
        elif self._path == ".transtable.YABTdata.rule.trans":
            self._trans += data
        elif self._path == ".transtable.YABTdata.rule.fstate":
            self._fstate += data
        elif self._path.startswith(".transtable.metadata.YABT_custom_matches."):
            self._tmpMatch += data

    def _addRule(self):
        """Private method to prepare data and adding rule"""
        iclass = int(self._iclass)
        focus = unicode(self._focus)
        trans = unicode(self._trans)
        fstate = int(self._fstate)
        bfcontext = self._bfcontext[2:]
        afcontext = self._afcontext[2:]
        bftype = self._bfcontext[:2]
        aftype = self._afcontext[:2]
        if bftype == "^c":
            bfcontext = self.customMatches[bfcontext]
        if aftype == "^c":
            afcontext = self.customMatches[afcontext]
        bfContextObj = self.contextFactory.getContextInstance(bftype,
                                bfcontext, self.contextFactory.BEFORE)
        afContextObj = self.contextFactory.getContextInstance(aftype,
                                afcontext, self.contextFactory.AFTER)
        group = focus[0]
        rule = GeneralContextRule(focus, bfContextObj, afContextObj, trans, 
                                  fstate)
        for state in self.__decisions[iclass]:
            self._rules.addRule(rule, (group, state))

class BasicXMLStringLoader(BasicXMLFileLoader):
    """
    A loader to load XML from a string

    All methods are as for BasicXMLFileLoader with the following exception:
    load: This overrides the BasicXMLFileLoader version and so works on 
    a string of XML rather than a file type object

    """

    def __init__(self):
        """Create a XML string loader"""
        super(BasicXMLStringLoader, self).__init__()

    def load(self, translator):
        """Load the XML string set into the translator"""
        self._translator = translator
        self.customMatches = {}
        parser = expat.ParserCreate()
        parser.StartElementHandler = self._startElement
        parser.EndElementHandler = self._endElement
        parser.CharacterDataHandler = self._characterData
        try:
            parser.Parse(self.getInput())
        except expat.ExpatError:
            raise InvalidTranslationTableException("Table is not valid")


class BasicWordDictLoader(BaseLoader):
    """Load a WordDictRule from a simple text file"""
    def __init__(self, inputsrc=None):
        """Create a WordDictLoader with optional input source"""
        super(BasicWordDictLoader, self).__init__()
        self.setInput(inputsrc)

    def load(self, translator):
        """Load the word dictionary into the translator"""
        input = self.getInput()
        originalPosition = input.tell()
        wd = WordDictRule()
        for line in input.readlines():
            if len(line) == 0 or not line[0].isdigit():
                continue
            s = line.split()
            if len(s) != 3:
                continue
            state = 0
            try:
                state = int(s[0])
            except ValueError:
                continue
            wd.addWord(state, s[1], s[2])
        translator.addRule(wd)
        input.seek(originalPosition)

