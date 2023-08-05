import unittest as _unittest
from typecheck import *

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
				
	def testTypeCheckedMethodRetainsName(self):
		@typecheck(int)
		def f(a):
			pass
			
		self.assertEquals('f', f.__name__)
		
	def testTypeCheckedMethodRetainsDocstring(self):
		@typecheck(int)
		def f(a):
			'docstring'
			pass
		
		self.assertEquals('docstring', f.__doc__)	
	
	def testTypeCheckedDocstringGetsFoundByDoctest(self):
		import doctest
		import doctests
		
		finder = doctest.DocTestFinder(verbose=True)
		tests = finder.find(doctests)

		self.assertEquals(3, len(tests))
		
		runner = doctest.DocTestRunner(doctest.OutputChecker())
		
		for test in tests:
			runner.run(test)
		
		self.assertEquals(7, runner.summarize()[1])
		self.assertEquals(0, runner.summarize()[0])