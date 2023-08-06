#!/usr/bin/python

# This script will run the doctests

import os
import sys
import unittest
import doctest

# first of all set the correct directory

rootDir = os.path.join(os.path.dirname(__file__), os.pardir)
#sys.path.insert(0, os.getcwd())
suite = unittest.TestSuite()
# Have a module to run all tests in a directory
def getTests(testDir):
	global suite
	#Set the directories not to be checked for tests
	noTestDirs = ['test_data', '.svn']
	for root, dirs, files in os.walk(testDir):
		for f in files:
			suite.addTest(doctest.DocFileSuite(os.path.join(root, f), module_relative=False))
		for removeDir in noTestDirs:
			if removeDir in dirs:
				dirs.remove(removeDir)

def additional_tests():
	global suite
	# Now actually run some of the tests
	getTests(os.path.join(rootDir, 'docs'))
	#getTests(os.path.join(rootDir, 'tests/bugs'))
	return suite
