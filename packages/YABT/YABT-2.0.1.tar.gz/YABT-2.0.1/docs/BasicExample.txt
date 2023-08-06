===========================
Basic usage example of YABT
===========================

Introduction
============

This documentation is to give some basic examples of how YABT can be used in applications to achieve Braille 
translation. This is not a developer guide for extending YABT. With in this document it will be assumed that you have 
already installed YABT and it works correctly.

Importing YABT
==============

For any application using YABT you will need its loaders module and translators module.

>>> from YABT import loaders, translators

To use the translation files provided with YABT you will need to include the pkg_resources module from setuptools. If 
you are shipping your translation tables and have them on the file system then this step is not necessary, but we are 
doing it here as these examples use the in built tables.

>>> import pkg_resources

This is all you need for the basic use, so it is time to move on to loading the translation table.

Loading a Translation Table
===========================

YABT 2.0 has separated its translator from the loader for the translation tables, so that potentially other formats of 
translation table may be created and used. In these examples we will only use the basic XML format used in YABT 1.0.

First we need to create the loader object. YABT ships with two loaders, one to read XML from a file, and one to read XML 
from a string. For loading from files use BasicXMLFileLoader and from strings use BaiscXMLSTringLoader.

>>> fileLoader = loaders.BasicXMLFileLoader()
>>> stringLoader = loaders.BasicXMLStringLoader()

For the file loader you should pass in a file like object into the setInput method.

>>> fileLoader.setInput(pkg_resources.resource_stream("YABT", "tables/britishtobrl.xml"))

For the string loader pass a string object into the setInput method.

>>> stringLoader.setInput(pkg_resources.resource_string("YABT", "tables/britishtobrl.xml"))

Now we need to create the translator objects which the loader should load into. Currently YABT comes with two translator 
implementations Translator and BufferedTranslator. The Translator class will translate the entire of the string in one 
go, where as the BufferedTranslator splits the string into lines before translating. This makes BufferedTranslator 
faster than Translator, but BufferedTranslator is unable to apply any rule which has a focus which spans a new line 
character, which is unlikely so generally BufferedTranslator is recommended.

>>> bufferedTranslator = translators.BufferedTranslator()
>>> translator = translators.Translator()

Tell the translator objects to load the translation data from the loader objects by calling the load method on the 
translator and passing in the loader object.

>>> translator.load(fileLoader)
>>> bufferedTranslator.load(stringLoader)

Now we should be able to proceed in actually using the translators for Braille translation.

Performing Translation
======================

You perform a translation by calling the translate method on the translator objects. This method takes the string (which 
can be unicode) to translate, the translation state, a string to show what text should appear before and a string to 
show what text should appear after. The state is used to represent different modes, in the britishtobrl table we are 
using, state 1 is for grade1, 2 is for grade2 and 5 is for computer Braille. These states may potentially vary for other 
tables, and additional states may exist. The context strings are not actually translated and do not appear in the 
translation, they are purely to tell YABT what text is meant to surround the translation string so that the correct 
rules can be used at the ends of the translation, so that should the output be joined with other Braille no join should 
be noticeable.

>>> bufferedTranslator.translate("hello world", 2, " ", " ")
u'HELLO _W'


