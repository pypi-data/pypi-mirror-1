#!/usr/bin/python
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
import logging
log = logging.root
setup(name='YABT',
version='1.0.1',
author='Michael Whapples',
author_email='mwhapples@users.sourceforge.net',
url='http://brltex.sf.net',
description='YABT: Yet Another Braille Translator',
long_description='''
YABT: Yet another Braille Translator

YABT is a general purpose Braille translation system written in pure python. It is primarily designed to be used by the 
`BrlTex Project <http://brltex.sf.net>`_, but due to its general design it may be suited to use in other projects.

Currently YABT has a table for translation in to British Braille encoded in ASCII Braille, but tables for other codes 
and other output encodings such as unicode Braille are possible.
''',
license="RPL",
classifiers=['Development Status :: 5 - Production/Stable',
	'Intended Audience :: Developers',
	'License :: OSI Approved',
	'Operating System :: OS Independent',
	'Programming Language :: Python',
	'Topic :: Adaptive Technologies',
	'Topic :: Software Development'
],
packages=['YABT'],
package_data={'YABT': ['logging.conf', 'britishtobrl.xml']},
entry_points={'console_scripts':['YABT_translate = YABT.app:standardTranslate']},
test_suite="tests.run_tests"
)

