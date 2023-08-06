"""Tests for the translator module"""

import unittest
import os.path

from YABT import loaders, translators
from YABT.exceptions import *

class Translator_SuperTestCase(unittest.TestCase):
    def setUp(self):
        self.translator = translators.Translator()
        self.loader = loaders.BasicXMLStringLoader()
        f = open(os.path.join(os.path.dirname(__file__), "correct.xml"))
        s = f.read()
        f.close()
        self.loader.setInput(s)
        self.translator.load(self.loader)
    def tearDown(self):
        self.loader = None
        self.translator = None

class Translator_BasicTranslate(Translator_SuperTestCase):
    def testTranslate_grade1(self):
        expected = u'THIS SHOULD BE GRADE#A'
        actual = self.translator.translate("this should be grade1", 1, " ", " ")
        self.assertEquals(expected, actual)
    def testTranslate_grade2(self):
        expected = u'? %D 2 GRADE#B'
        actual = self.translator.translate("this should be grade2", 2, " ", " ")
        self.assertEquals(expected, actual)
    def testTranslate_invalidState(self):
        self.assertRaises(InvalidStateException, self.translator.translate, "hello", 0, " ", " ")
    def testGetStates(self):
        expected = set([1,2,3,4,5])
        actual = self.translator.getStates()
        self.assertEquals(expected, actual)

class BufferedTranslator_SuperTestCase(unittest.TestCase):
    def setUp(self):
        self.translator = translators.BufferedTranslator()
        self.loader = loaders.BasicXMLStringLoader()
        f = open(os.path.join(os.path.dirname(__file__), "correct.xml"))
        s = f.read()
        f.close()
        self.loader.setInput(s)
        self.translator.load(self.loader)
    def tearDown(self):
        self.loader = None
        self.translator = None

class BufferedTranslator_BasicTranslate(BufferedTranslator_SuperTestCase):
    def testTranslate_grade1(self):
        expected = "THIS SHOULD BE GRADE#A"
        actual = self.translator.translate("this should be grade1", 1, " ", " ")
        self.assertEquals(expected, actual)
    def testTranslate_grade2(self):
        expected = "? %D 2 GRADE#B"
        actual = self.translator.translate("this should be grade2", 2, " ", " ")
        self.assertEquals(expected, actual)
    def testGetStates(self):
        expected = set([1,2,3,4,5])
        actual = self.translator.getStates()
        self.assertEquals(expected, actual)
    def testTranslate_invalidState(self):
        self.assertRaises(InvalidStateException, self.translator.translate, "hello", 0, " ", " ")

