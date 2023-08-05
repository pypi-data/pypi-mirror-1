import support
from support import TODO, TestCase

if __name__ == '__main__':
	support.adjust_path()
### /Bookkeeping ###

import types
import unittest

import typecheck

def check_type(typ, obj):
	typecheck.check_type(typ, None, obj)

class Test_Or(TestCase):
	def setUp(self):
		from typecheck import Or
	
		def or_type(obj):
			check_type(Or(int, float), obj)
	
		self.or_type = or_type
		
	def test_constructor(self):
		from typecheck import Or
		
		try:
			Or()
		except TypeError, e:
			assert str(e) == "__init__() takes at least 2 arguments (1 given)"
		else:
			raise AssertionError("Failed to raise TypeError")
		
	def test_success(self):
		from typecheck import Or, And
	
		# Built-in types
		self.or_type(5)
		self.or_type(7.0)
		
		class A(object): pass # New-style classes
		class B: pass # Old-style classes
		class C(A, B): pass
			
		check_type(Or(A, B), C())
		check_type(Or(A), A())
		check_type(Or(B), B())
		
		# Nested extension classes
		check_type(Or(A, And(A, B)), C())
		
		# Complex-er types
		check_type(Or((int, int), [int, float]), (5, 6))
		
	def test_failure(self):
		from typecheck import _TC_TypeError, Or
	
		try:
			self.or_type("foo")
		except _TC_TypeError, e:
			assert e.right == Or(int, float)
			assert e.wrong == str
		else:
			self.fail("Passed incorrectly")
			
	def test_equality(self):
		from typecheck import Or
		
		assert Or(int, float) == Or(int, float)
		assert Or(int, float) == Or(int, int, int, float)
		assert Or(int, int, int, float) == Or(int, float)
		assert not Or(int, float) != Or(int, float)
		assert Or(float, str) != Or(int, float)
		assert Or(int, float) == Or(int, float, str)
		assert Or(int, float, str) != Or(int, float)
		assert Or(int, float) == Or(float, int)
		assert not Or(int, float) != Or(float, int)
			
class Test_And(TestCase):
	def test_success(self):
		from typecheck import And
	
		class A: pass
		class B: pass
		class C(A, B): pass
			
		check_type(And(A, B), C())
		
	def test_failure(self):
		from typecheck import _TC_TypeError, And
	
		try:
			check_type(And(int, float), "foo")
		except _TC_TypeError, e:
			assert e.right == And(int, float)
			assert e.wrong == str
		else:
			self.fail("Passed incorrectly")
			
	def test_equality(self):
		from typecheck import And
		
		assert And(int, float) == And(int, int, int, float)
		assert And(int, int, int, float) == And(int, float)
		assert And(int, float) == And(int, float)
		assert And(int, float) == And(float, int)
		assert not And(int, float) == And(float, float)
		assert And(int, float) != And(float, float)
		assert And(int, float) != And(int, int)
		assert And(int, float) == And(int, float, str)

class Test_Not(TestCase):
	def test_success(self):
		from typecheck import Not
	
		check_type(Not(int), 4.0)
		check_type(Not(int, float), 'four')
		
		class A: pass
		class B: pass
		class C: pass
			
		check_type(Not(A, B, int), C())
		
	def test_failure_1(self):
		from typecheck import _TC_TypeError, Not
	
		try:
			check_type(Not(int), 4)
		except _TC_TypeError, e:
			assert e.right == Not(int)
			assert e.wrong == int
		else:
			self.fail("Passed incorrectly")
			
	def test_failure_2(self):
		from typecheck import _TC_TypeError, Not
	
		try:
			check_type(Not(int, float), 4.0)
		except _TC_TypeError, e:
			assert e.right == Not(int, float)
			assert e.wrong == float
		else:
			self.fail("Passed incorrectly")
			
	def test_failure_3(self):
		from typecheck import _TC_TypeError, Not
	
		class A: pass
		class B: pass
		class C(A, B): pass
			
		try:
			check_type(Not(A, B, int), C())	
		except _TC_TypeError, e:
			assert e.right == Not(A, B, int)
			assert e.wrong == C
		else:
			self.fail("Passed incorrectly")
			
	def test_equality(self):
		from typecheck import Not
		
		assert Not(int, int, int) == Not(int)
		assert Not(int) == Not(int, int, int)
		assert Not(int) == Not(int)
		assert not Not(int) == Not(float)
		assert Not(int) != Not(float)
		assert Not(int, float) == Not(float, int)
		assert Not([int], (int, int)) == Not((int, int), [int])
		
class Test_Any(TestCase):
	def test_args_and_return_pass(self):
		from typecheck import typecheck_args, typecheck_return, Any
		
		def run_test(dec):
			@dec(Any())
			def foo(a):
				return a

			assert foo(foo) == foo
			assert foo(5) == 5
			assert foo(([], [], 5)) == ([], [], 5)
			
		run_test(typecheck_args)
		run_test(typecheck_return)
		
	def test_yield_pass(self):
		from typecheck import typecheck_yield, Any
		
		@typecheck_yield(Any())
		def foo(a):
			yield a
			
		assert foo(5).next() == 5
		assert foo({}).next() == {}
		assert foo(foo).next() == foo
		
	def test_equality(self):
		from typecheck import Any
		
		assert Any() == Any()
		assert not Any() != Any()
		assert Any() != []
		assert not Any() == []
		
class Test_Empty(TestCase):
	def test_bad_empty_type(self):
		from typecheck import Empty
		
		for t in (int, set, float):
			try:
				Empty(int)
			except TypeError:
				pass
			else:
				raise AssertionError("Failed to raise TypeError for %s" % t)

	def test_list_success(self):
		from typecheck import Empty
	
		check_type(Empty(list), [])
	
	def test_list_failure(self):
		from typecheck import Empty, _TC_LengthError
		
		try:
			check_type(Empty(list), [5, 6])
		except _TC_LengthError, e:
			assert e.wrong == 2
			assert e.right == 0
		else:
			self.fail("Passed incorrectly")
			
	def test_dict_success(self):
		from typecheck import Empty
	
		check_type(Empty(dict), {})
	
	def test_dict_failure(self):
		from typecheck import Empty, _TC_LengthError, _TC_DictError
		
		try:
			check_type(Empty(dict), {'f': 5})
		except _TC_DictError, e:
			assert isinstance(e.inner, _TC_LengthError)
			assert e.inner.wrong == 1
			assert e.inner.right == 0
		else:
			self.fail("Passed incorrectly")
			
	def test_inappropriate_type(self):
		from typecheck import Empty, _TC_TypeError
		
		for t in (dict, list):
			try:
				check_type(Empty(t), 5)
			except _TC_TypeError, e:
				assert e.right == t
				assert e.wrong == int
			else:
				raise AssertionError("Failed to raise _TC_TypeError")
			
	def test_equality(self):
		from typecheck import Empty
		
		assert Empty(list) == Empty(list)
		assert Empty(dict) == Empty(dict)
		assert Empty(list) != Empty(dict)
		assert Empty(dict) != Empty(list)
		assert not Empty(list) != Empty(list)
		assert not Empty(list) == Empty(dict)

class Test_IsCallable(TestCase):
	def test_args_and_return_pass(self):
		from typecheck import typecheck_args, typecheck_return, IsCallable
		
		def run_test(dec):
			@dec(IsCallable())
			def foo(a):
				return a

			assert foo(foo) == foo
			
		run_test(typecheck_args)
		run_test(typecheck_return)
		
	def test_args_fail(self):
		from typecheck import typecheck_args, IsCallable
		from typecheck import TypeCheckError, _TC_IndexError, _TC_TypeError
		
		@typecheck_args(IsCallable())
		def foo(a):
			return a

		try:
			foo(5)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == 'a callable'
			assert e.internal.inner.wrong == int
			
			self.assertEquals(str(e), "in (5,), at index 0, expected a callable, got <type 'int'>")
		else:
			raise AssertionError("Failed to raise TypeCheckError")
			
	def test_return_fail(self):
		from typecheck import typecheck_return, IsCallable
		from typecheck import TypeCheckError, _TC_IndexError, _TC_TypeError
		
		@typecheck_return(IsCallable())
		def foo(a):
			return a

		try:
			foo(5)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_TypeError)
			assert e.internal.right == 'a callable'
			assert e.internal.wrong == int
			
			self.assertEquals(str(e), "in 5, expected a callable, got <type 'int'>")
		else:
			raise AssertionError("Failed to raise TypeCheckError")
		
	def test_yield_pass(self):
		from typecheck import typecheck_yield, IsCallable
		
		@typecheck_yield(IsCallable())
		def foo(a):
			yield a

		assert foo(foo).next() == foo
		
	def test_yield_fail(self):
		from typecheck import typecheck_yield, IsCallable
		from typecheck import TypeCheckError, _TC_GeneratorError, _TC_TypeError
		
		@typecheck_yield(IsCallable())
		def foo(a):
			yield a

		g = foo(5)

		try:
			g.next()
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_GeneratorError)
			assert e.internal.yield_no == 1
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == 'a callable'
			assert e.internal.inner.wrong == int
			
			self.assertEquals(str(e), "At yield #1: in 5, expected a callable, got <type 'int'>")
		else:
			raise AssertionError("Failed to raise TypeCheckError")
			
class Test_HasAttr(TestCase):
	def test_empty(self):
		from typecheck import HasAttr
		
		try:
			HasAttr()
		except TypeError, e:
			self.assertEqual(str(e), "__init__() takes at least 2 arguments (1 given)")
		else:
			raise AssertionError("Failed to raise TypeError")
			
	def test_success_named_only(self):
		from typecheck import HasAttr
		
		class A(object):
			def __init__(self):
				self.foo = 5
				self.bar = 6
				
		check_type(HasAttr(['foo', 'bar']), A())
		
	def test_success_typed_only(self):
		from typecheck import HasAttr
		
		class A(object):
			def __init__(self):
				self.foo = 5
				self.bar = 6
				
		check_type(HasAttr({'foo':int, 'bar':int}), A())
		
	def test_success_named_and_typed(self):
		from typecheck import HasAttr
		
		class A(object):
			def __init__(self):
				self.foo = 5
				self.bar = 6
				
		check_type(HasAttr(['foo'], {'bar': int}), A())
		check_type(HasAttr({'bar': int}, ['foo']), A())
		
	def test_failure_missing_attr(self):
		from typecheck import HasAttr, _TC_MissingAttrError
		
		class A(object):
			def __init__(self):
				self.foo = 5
				
			def __str__(self):
				return "A()"
				
		try:
			check_type(HasAttr(['foo', 'bar']), A())
		except _TC_MissingAttrError, e:
			assert e.attr == 'bar'
			self.assertEqual(e.message(), "missing attribute bar")
		else:
			raise AssertionError("Did not raise _TC_MissingAttrError")
			
	def test_failure_badly_typed_attr(self):
		from typecheck import HasAttr, _TC_AttrError, _TC_TypeError
		
		class A(object):
			def __init__(self):
				self.foo = 5
				self.bar = 7.0
				
			def __str__(self):
				return "A()"
				
		for args in ((['foo'], {'bar': int}), ({'bar': int}, ['foo'])):		
			try:
				check_type(HasAttr(*args), A())
			except _TC_AttrError, e:
				assert e.attr == 'bar'
				assert isinstance(e.inner, _TC_TypeError)
				assert e.inner.right == int
				assert e.inner.wrong == float
				self.assertEqual(e.message(), "as for attribute bar, expected <type 'int'>, got <type 'float'>")
			else:
				raise AssertionError("Did not raise _TC_AttrError")

class Test_IsIterable(TestCase):
	def test_success_builtins(self):
		from typecheck import IsIterable
		
		for t in (list, tuple, set, dict):
			check_type(IsIterable(), t())
			
	def test_success_generator(self):
		from typecheck import IsIterable
		
		def foo():
			yield 5
			yield 6
			
		check_type(IsIterable(), foo())
			
	def test_success_user_newstyle(self):
		from typecheck import IsIterable
		
		class A(object):
			def __iter__(self):
				yield 5
				yield 6
				
		class B(object):
			def __iter__(self):
				return self
				
			def next(self):
				return 5
				
		for c in (A, B):
			check_type(IsIterable(), c())
			
	def test_success_user_oldstyle(self):
		from typecheck import IsIterable
		
		class A:
			def __iter__(self):
				yield 5
				yield 6
				
		class B:
			def __iter__(self):
				return self
				
			def next(self):
				return 5
				
		for c in (A, B):
			check_type(IsIterable(), c())
			
	def test_failure(self):
		from typecheck import IsIterable, _TC_TypeError
		
		class A(object):
			def __str__(self):
				return "A()"
			
		try:
			check_type(IsIterable(), A())
		except _TC_TypeError, e:
			assert e.right == "an iterable"
			assert e.wrong == A
		else:
			raise AssertionError("Failed to raise _TC_TypeError")


### Bookkeeping ###
if __name__ == '__main__':
	import __main__
	support.run_all_tests(__main__)
