'''This module contains useful functions which may be run over the text before translating it using YABT.'''
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

import string
def addCapMarks(intext):
	'''addCapMarks(intext) - adds capital markers in intext and returns the new string.'''
	# We add two types of capital markers, letter and word given by $CL and $CW
	counter = 0
	outtext = []
	intextlen = len(intext)
	while counter < intextlen:
		counter2 = 0
		while counter2 < len(intext):
			if not intext[counter2] in string.uppercase:
				break
			else:
				counter2 += 1
		if counter2 == 1:
			outtext.append(u'$CL ' + intext[0])
			counter +=1
			intext = intext[1:]
		elif counter2 > 1:
			outtext.append(u'$CW ' + intext[:counter2] + u'$EW ')
			counter += counter2
			intext = intext[counter2:]
		else:
			outtext.append(intext[0])
			counter +=1
			intext = intext[1:]
	return u''.join(outtext)
