"""This module tests YABT.loaders"""

import unittest
import os.path

from YABT import loaders
from YABT.exceptions import InvalidTranslationTableException

class FakeTranslator:
    def __init__(self):
        self.charMaps = 0
        self.states = 0
        self.rules = 0
    def addCharacterMap(self, orig, repl):
        self.charMaps += 1
    def addState(self, state):
        self.states += 1
    def addRule(self, rule):
        self.rules += 1
    def load(self, loader):
        loader.load(self)

class BasicXMLFileLoader_SuperTestCase(unittest.TestCase):
    def setUp(self):
        self.loader = loaders.BasicXMLFileLoader()
    def tearDown(self):
        self.loader = None

class BasicXMLStringLoader_SuperTestCase(unittest.TestCase):
    def setUp(self):
        self.loader = loaders.BasicXMLStringLoader()
    def tearDown(self):
        self.loader = None

class BasicXMLFileLoader_ValidRun(BasicXMLFileLoader_SuperTestCase):
    def setUp(self):
        BasicXMLFileLoader_SuperTestCase.setUp(self)
        f = open(os.path.join(os.path.dirname(__file__), "correct.xml"))
        self.loader.setInput(f)
    def tearDown(self):
        self.loader.getInput().close()
        BasicXMLFileLoader_SuperTestCase.tearDown(self)
    def testLoad(self):
        t = FakeTranslator()
        t.load(self.loader)
        self.assertEquals(28, t.charMaps)
        self.assertEquals(13, t.states)
        self.assertEquals(1, t.rules)

class BasicXMLFileLoader_BadlyFormedTable(BasicXMLFileLoader_SuperTestCase):
    def setUp(self):
        BasicXMLFileLoader_SuperTestCase.setUp(self)
        f = open(os.path.join(os.path.dirname(__file__), "badlyformed.xml"))
        self.loader.setInput(f)
    def tearDown(self):
        self.loader.getInput().close()
        BasicXMLFileLoader_SuperTestCase.tearDown(self)
    def testLoad(self):
        t = FakeTranslator()
        self.assertRaises(InvalidTranslationTableException, t.load, self.loader)

class BasicXMLStringLoader_ValidRun(BasicXMLStringLoader_SuperTestCase):
    def setUp(self):
        BasicXMLStringLoader_SuperTestCase.setUp(self)
        f = open(os.path.join(os.path.dirname(__file__), "correct.xml"))
        s = f.read()
        f.close()
        self.loader.setInput(s)
    def testLoad(self):
        t = FakeTranslator()
        t.load(self.loader)
        self.assertEquals(28, t.charMaps)
        self.assertEquals(13, t.states)
        self.assertEquals(1, t.rules)

class BasicXMLStringLoader_BadlyFormed(BasicXMLStringLoader_SuperTestCase):
    def setUp(self):
        BasicXMLStringLoader_SuperTestCase.setUp(self)
        f = open(os.path.join(os.path.dirname(__file__), "badlyformed.xml"))
        s = f.read()
        f.close()
        self.loader.setInput(s)
    def testLoad(self):
        t = FakeTranslator()
        self.assertRaises(InvalidTranslationTableException, t.load, self.loader)

