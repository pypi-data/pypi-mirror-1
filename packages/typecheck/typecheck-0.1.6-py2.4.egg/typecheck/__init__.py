"""A type-checking module for Python

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

TERMS OF USE

If you care, this software is Copyright (C) 2005 by Iain Lowe and is released
under the terms of the MIT License.
"""

def typecheck(*types, **kwtypes):
	"""This decorator performs type-checking on decorated functions.
	
	When supplied with a combination of positional and/or keyword
	arguments, the decorated method's parameters are verified each
	time it is called. Any parameters that do not match the supplied
	types cause a TypeCheckException to be raised.
	"""
	
	import inspect
	
	for _param_list in types, kwtypes.values():
		for _type in _param_list:
			if not (isinstance(_type, type) or inspect.isclass(_type)):
				raise Exception('Only instances types are allowed as parameters, you supplied an instance of %s' % _type.__class__)
	
	def __checkType(object, _type):
		if not isinstance(object, _type):
			raise TypeCheckException('%s is not of type %s' % (object, _type))
	
	def __typeCheckingDecorator(f):
		argspec = inspect.getargspec(f)
		
		def __typeCheckingFunction(*runtime_args, **runtime_kwargs):			
			for name, value in runtime_kwargs.items():
				__checkType(value, kwtypes[name])
			
			for argument, expectedType in zip(runtime_args, types):
				__checkType(argument, expectedType)
				
			return apply(f, runtime_args, runtime_kwargs)
		
		__typeCheckingFunction.__doc__ = f.__doc__
		__typeCheckingFunction.__name__ = f.__name__
		__typeCheckingFunction.__module__ = f.__module__
		
		return __typeCheckingFunction
	return __typeCheckingDecorator
	
class TypeCheckException(Exception):
	"""Raised when a type-check fails"""	
	pass