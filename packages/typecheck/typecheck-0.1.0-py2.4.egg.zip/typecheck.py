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

FUTURE ENHANCEMENTS

I suppose you could add code to check the return value before it is returned
but I didn't implement it.

TERMS OF USE

This software is released under the MIT License.
"""

__revision__ = '$Revision: 1.2 $'

def typecheck(*types, **kwtypes):
	"""This decorator performs type-checking on decorated functions.
	
	When supplied with a combination of positional and/or keyword
	arguments, the decorated method's parameters are verified each
	time it is called. Any parameters that do not match the supplied
	types cause a TypeCheckException to be raised.
	"""
	
	def __typeCheckingDecorator(f):
		def __typeCheckingFunction(*objects, **kwobjects):
			for argument, expectedType in zip(objects, types):
				if not isinstance(argument, expectedType):
					raise TypeCheckException('%s is not of type %s' % (argument, expectedType))
					
			for name in kwobjects.keys():
				if not isinstance(kwobjects[name], kwtypes[name]):
					raise TypeCheckException('%s is not of type %s' % (name, kwtypes[name]))
					
			return apply(f, objects, kwobjects)
		
		__typeCheckingFunction.__doc__ = f.__doc__
		__typeCheckingFunction.__name__ = f.__name__
		
		return __typeCheckingFunction
	return __typeCheckingDecorator
	
class TypeCheckException(Exception):
	"""Raised when a type-check fails"""
	
	pass
	
import unittest as _unittest

class _TestSuite(_unittest.TestCase):
	def testCreateTypeCheckedMethod(self):
		@typecheck(int)
		def f(a):
			return 1
			
		self.assertEquals(1, f(5))
		
		try:
			f('a')
			self.fail()
		except TypeCheckException:
			pass
			
	def testCreateTypeCheckedMethodPositional(self):
		@typecheck(int, int, str)
		def f(a, b, c):
			return 1
			
		self.assertEquals(1, f(5, 6, '7'))
		
		for a, b, c in [(5, 6, 7), ('5', 6, '7'), (8, '9', 10), (8, '9', '10')]:
			try:
				f(a, b, c)
				self.fail('Failed with values (%s, %s, %s)' % (a, b, c))
			except TypeCheckException:
				pass
				
	def testCreateTypeCheckedMethodKeyword(self):
		@typecheck(a=int, c=str)
		def f(a=None, b=None, c=None):
			return 1

		self.assertEquals(1, f(5, 6, '7'))
		self.assertEquals(1, f(5, [], '7'))

		for a, b, c in [(5, 6, 7), ('11', 12, '13'), (8, '9', 10)]:
			try:
				self.assertEquals(1, f(a=a, b=b, c=c))
				self.fail('Failed with values (%s, %s, %s)' % (a, b, c))
			except TypeCheckException:
				pass
				
	def testCreateTypeCheckedMethodCombined(self):
		@typecheck(int, b=int, c=str)
		def f(a, b=None, c=None):
			return 1

		self.assertEquals(1, f(5, 6, '7'))
		self.assertEquals(1, f(5, 13, 'hello'))

		for a, b, c in [(5, 6, 7), ('11', 12, '13'), (8, '9', 10)]:
			try:
				self.assertEquals(1, f(a, b=b, c=c))
				self.fail('Failed with values (%s, %s, %s)' % (a, b, c))
			except TypeCheckException:
				pass
		
if __name__ == '__main__':
	_unittest.main()
