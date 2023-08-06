"""A module containing functions for scripts"""

import optparse
import os.path
from pkg_resources import *

from YABT import loaders, translators

def standardTranslate():
    """YABT_translate script"""
    inFile = None
    parser = optparse.OptionParser(usage="%prog [OPTIONS] INFILE", 
                                   version="%prog 2.0")
    parser.add_option("-t", "--table", dest="table", 
                      help="use the table specified for translation")
    parser.add_option("-s", "--state", dest="state", type="int",
                      help="Specify the state to use, usually 1 for grade1" +
                      "or 2 for grade2")
    parser.set_defaults(table="britishtobrl.xml", state=2)
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("You need to specify an input file")
    loader = loaders.BasicXMLStringLoader()
    translator = translators.BufferedTranslator()
    if resource_exists("YABT", "tables/" + options.table):
        loader.setInput(resource_string("YABT", "tables/" + options.table))
    elif os.path.exists(options.table):
        try:
            inFile = open(options.table, 'r')
            loader.setInput(inFile.read())
        except IOError: parser.error("Problem reading table")
        finally: inFile.close()
    else:
        parser.error("Table couldn't be found")
    if os.path.exists(args[0]):
        try:
            inFile = open(args[0], 'r')
            inText = unicode(inFile.read(), "latin1")
        except IOError: parser.error("INFILE could not be read")
        finally: inFile.close()
    else:
        parser.error("INFILE not found")
    translator.load(loader)
    print(translator.translate(inText, options.state, " ", " "))
    return 0

if "__main__" == __name__:
    standardTranslate()
