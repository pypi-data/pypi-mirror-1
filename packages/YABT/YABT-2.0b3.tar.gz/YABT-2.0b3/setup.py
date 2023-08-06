#!/usr/bin/python
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
import logging
import version
__version__ = version.getVersion("2.0b3")
log = logging.root
setup(name='YABT',
version=__version__,
author='Michael Whapples',
author_email='mwhapples@users.berlios.de',
url='http://yabt.berlios.de',
description='YABT: A context sensitive string manipulation tool',
long_description='''
YABT: A context sensitive string manipulation tool

YABT is a context sensitive string manipulation tool written in pure python. It has two main goals:
* Provide implementations of string manipulation for specific tasks to be used inside applications. The current 
implementation is a context matching rule system combined with a finite state machine and a table for translating text 
into British Braille. This implementation should be useful for other tasks such as preparing text for a speech 
synthesiser by providing different tables.
* To provide a framework which developers can use to create new translation algorithms which can be used by any 
application using YABT. This side of YABT could do with further development and so is most likely going t see some 
changes as YABT matures.
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
package_data={'YABT': ['tables/britishtobrl.xml']},
entry_points={'console_scripts':['yabt-trans = YABT.app:standardTranslate']},
test_suite="tests",
setup_requires=['setuptools_hg']
)

