"""A module containing functions for scripts"""

import sys
import optparse
import os.path
from pkg_resources import *

from YABT import loaders, translators

distro = get_distribution("YABT")

def standardTranslate():
    """YABT_translate script"""
    global distro
    inFile = None
    parser = optparse.OptionParser(usage="%prog [OPTIONS] INFILE",
                                   version="%prog " + distro.version)
    parser.add_option("-t", "--table", dest="table", 
                      help="use the table specified for translation " +
                           "[DEFAULT: %default]")
    parser.add_option("-s", "--state", dest="state", type="int",
                      help="Specify the state to use, usually 1 for grade1" +
                      "or 2 for grade2 [DEFAULT: %default]")
    parser.add_option("-o", "--output", dest="outfile",
                      help="Output to a file instead of STDOUT " +
                      "[DEFAULT %default]")
    parser.add_option("-d", "--dictionary", dest="dictionary",
                      help="use the specified word substitution " +
                      "dictionary as well as the standard rules " +
                      "[default: %default]")
    parser.set_defaults(table="britishtobrl.xml", state=2, outfile=None,
                        dictionary=None)
    options, args = parser.parse_args()
    loader = loaders.BasicXMLStringLoader()
    translator = translators.BufferedTranslator()
    if options.dictionary is not None:
        wdl = loaders.BasicWordDictLoader()
        try:
            wdl.setInput(open(options.dictionary))
        except IOError:
            parser.error("Word dictionary couldn't be opened")
        translator.load(wdl)
        wdl.getInput().close()
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
    inText = ""
    if len(args) == 0:
        line = sys.stdin.readline()
        while line != "":
            inText += unicode(line, 'latin1')
            line = sys.stdin.readline()
    elif len(args) > 1:
        parser.error("Only one input file should be specified")
    elif os.path.exists(args[0]):
        try:
            inFile = open(args[0], 'r')
            inText = unicode(inFile.read(), "latin1")
        except IOError: parser.error("INFILE could not be read")
        finally: inFile.close()
    else:
        parser.error("INFILE not found")
    translator.load(loader)
    output = translator.translate(inText, options.state, " ", " ")
    if options.outfile is None:
        sys.stdout.write(output)
    else:
        try:
            f = open(options.outfile, 'w')
            f.write(output)
            f.close()
        except:
            parser.error("Can't write output file")
    return 0

if "__main__" == __name__:
    standardTranslate()
