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

FUTURE ENHANCEMENTS

I suppose you could add code to check the return value before it is returned
but I didn't implement it.

TERMS OF USE

If you care, this software is Copyright (C) 2005 by Iain Lowe and is released
under the terms of the MIT License.
