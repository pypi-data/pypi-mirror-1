#!/usr/bin/python
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
setup(name='YABT',
version='1.0.0Update1',
author='Michael Whapples',
author_email='mwhapples@users.sourceforge.net',
url='http://brltex.sf.net',
description='YABT: Yet Another Braille Translator',
packages=['YABT'],
package_data={'YABT': ['logging.conf', 'britishtobrl.xml']},
entry_points={'console_scripts':['YABT_translate = YABT.app:standardTranslate']},
test_suite="tests.run_tests"
)

