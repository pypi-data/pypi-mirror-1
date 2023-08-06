# Copyright (C) 2007 Michael Whapples, All Rights Reserved.
# Original Author: Michael Whapples, mwhapples@users.sourceforge.net
# Unless linsor has explicitly granted you any other licensing terms, the contents of this file is subject to the RPL 1.1,
# available at the BrlTex website (http://brltex.sourceforge.net).
# All software distributed under the Licenses is provided strictly on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, AND the licensor
# HEREBY DISCLAIMS ALL SUCH WARRANTIES, INCLUDING WITHOUT LIMITATION, ANY WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, QUIET ENJOYMENT, OR NON-INFRINGEMENT.
# Licensor reserves the right to change the Venue stated in the license to the UK.
# 

import sys
import YABT
from pkg_resources import resource_string
def standardTranslate():
	# Check we have two arguments
	if len(sys.argv) != 3:
		print('USAGE: YABT_translate file_to_translate state\nfile_to_translate should be a text file and state should be 1 for grade 1 or 2 for grade 2.')
		sys.exit(2)
	# First load the data in the file specified on the command line
	try:
		f = open(sys.argv[1])
		input_text = unicode(f.read(), 'Latin1')
		f.close()
	except:
		print('There seems to be a problem with the file.')
	# Now do the translation
	mytrans = YABT.Translator()
	mytrans.loadConfigString(resource_string('YABT','tables/britishtobrl.xml'))
	print(mytrans.translateText(input_text, int(sys.argv[2]), ' ', ' ', True).encode('Latin1'))
