A type-checking module for Python

This module only exports the type-checking decorator and the TypeCheckException
so you can do:

from typecheck import *

Then use the typecheck decorator on methods that should be typesafe. You can
combine positional and keyword arguments.

@typecheck(int, str, list)
def f(a, b, c):
	pass
	
This will check that a, b and c are of type int, str and list respectively.
The unit tests show some more permutations of the concept. In earlier versions
of Python (prior to 2.4) you will need to use old-style decoration techniques:

def f(a, b, c):
	pass
	
f = typecheck(int, int, int)(f)

Note that you can also assert that certain parameters are instances of
user-defined classes:

class MyClass:
	pass
	
@typecheck(MyClass)
def f(myClass_instance):
	pass

You can use doctest on typechecked functions by importing the
typecheck.doctest_support module in your code before accessing any of the
doctest classes or functions:

import typecheck.doctest_support

CONTRIBUTORS

- Knut Hartmann contributed doctest tests (2005/09/28)

CHANGES

- 20050928 Added typecheck.doctest_support

FUTURE ENHANCEMENTS

I suppose you could add code to check the return value before it is returned
but I didn't implement it.

TERMS OF USE

If you care, this software is Copyright (C) 2005 by Iain Lowe and is released
under the terms of the MIT License.