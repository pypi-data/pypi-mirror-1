This is for the module YABT.contextTypes, which is not for general use but is used internally by YABT. It is purely 
being documented here for those who may want to do further development of YABT.

The purpose of this module is to generate Context objects for YABT. If you wish to add a new way for YABT to identify 
the context for the rules then here is the right place to add that functionality.

None of the actual context object classes are accessed directly, so they won't be tested here. All usage should be 
through the ContextTypeFactory class which will generate the correct objects for you.

The usage of the ContextTypeFactory class is as follows

First of all the module needs importing.

>>> from YABT.contextTypes import ContextTypeFactory

Now we can access the class create an object.

>>> contextFactory = ContextTypeFactory()
>>> contextFactory.__class__.__name__
'ContextTypeFactory'

Now we have the object, we may wish to set some values for particular types. At the moment only the custom match type 
requires some values to be set. For this we need to call the setCustomMatches method. This method takes a dictionary, 
where keys are the names of the groups and the values are the characters belonging to the group.

>>> contextFactory.setCustomMatches({'lowercase': 'abcdefghijklmnopqrstuvwxyz'})

Once this has been done, we can start creating the context objects. For the context object creation we use the 
getContext method. This method takes three parameters, the type string, the pattern and a boolean indicating if the 
context is for before (True for before and False for after). A use of the method might be

>>> matchAny = contextFactory.getContext('^a', '', True)

In that case above, the second and third parameters don't actually matter as the ^a type should always match, so is not 
context sensitive. The below shows some of this.

>>> matchAny2 = contextFactory.getContext('^a', 'ffdk', False)
>>> matchAny.search('hello world')
True
>>> matchAny2.search('hello world')
True
>>> matchAny.search(' ')
True
>>> matchAny2.search(' ')
True
>>> matchAny.search('')
True

And we could go on, but it would be pointless as for a ^a context its search method should always return True.

You have already met one context type, but there are others and they are much more interesting.

The next we will introduce, you have heard mentioned earlier in this document, is the custom match or ^c type. This type 
works by having defined groups of characters and tests whether the character adjacent  is a member of the group. The 
pattern for the ^c type is the name of the group of characters. We could do something like the following to demostrate 
this.

>>> lowercaseBefore = contextFactory.getContext('^c', 'lowercase', True)
>>> lowercaseBefore.search('hello')
True
>>> lowercaseBefore.search('.12h')
True
>>> lowercaseBefore.search('123.,')
False

As you can see, the ^c type does not always match, but it is also direction sensitive. We can do the previous on a after 
defined version.

>>> lowercaseAfter = contextFactory.getContext('^c', 'lowercase', False)
>>> lowercaseAfter.search('hello')
True
>>> lowercaseAfter.search('.12h')
False
>>> lowercaseAfter.search('123..,')
False

The remaining types do not need any special set up.

The next type we will introduce is the text match or ^t type. This simply matches the text in the context in the 
direction specified.

>>> textBefore = contextFactory.getContext('^t', 'hello ', True)
>>> textBefore.search('hello ')
True

The match must be exact, so the following doesn't work.

>>> textBefore.search('hello')
False

Neither does

>>> textBefore.search('Say " hello')
False

We also have the same sort of behaviour for the after version of this.

>>> textAfter = contextFactory.getContext('^t', ' hello ', False)
>>> textAfter.search(' hello world')
True
>>> textAfter.search(' hello ')
True
>>> textAfter.search(' hello')
False
>>> textAfter.search('hello world')
False

The remaining type is the regular expression or ^r type. This takes a regular expression as the pattern. The matching on 
this is complicated and is best explained else where where regular expressions are discussed. The only thing you should 
be aware of is that regular expressions have a way to specify whether it should match at the beginning or end of the 
text, but this should not be given in the pattern as it is automatically inserted for you according to the before 
setting. Some examples are given below.

>>> reAfter = contextFactory.getContext('^r', r'[0-9]+\.[0-9]+', False)
>>> reAfter.search('0.5')
True
>>> reAfter.search('90.2113')
True
>>> reAfter.search('1.788965')
True
>>> reAfter.search('.09')
False
>>> reAfter.search('x.098')
False

