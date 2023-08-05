import support
from support import TODO, TestCase

if __name__ == '__main__':
	support.adjust_path()
### /Bookkeeping ###

import types
import unittest

import typecheck

class Test_typecheck_return(TestCase):
	def test_success_1(self):
		from typecheck import typecheck_return
	
		@typecheck_return(int, int, int)
		def foo():
			return 5, 6, 7
		
		assert foo() == (5, 6, 7)
		assert foo.type_return == (int, int, int)
		
	def test_success_2(self):
		from typecheck import typecheck_return
		
		@typecheck_return([int])
		def foo():
			return [4,5,6]
		
		assert foo() == [4, 5, 6]
		assert foo.type_return == [int]
		
	def test_success_3(self):
		from typecheck import typecheck_return
		
		@typecheck_return([int], int, str)
		def foo():
			return [4,5,6], 5, "foo"
		
		assert foo() == ([4, 5, 6], 5, "foo")
		assert foo.type_return == ([int], int, str)
		
	def test_success_4(self):
		from typecheck import typecheck_return

		@typecheck_return(int)
		def foo():
			return 7
		
		assert foo() == 7
		assert foo.type_return == int
		
	def test_success_5(self):
		from typecheck import typecheck_return
		
		@typecheck_return( (int,) )
		def foo():
			return (7,)
		
		assert foo() == (7,)
		assert foo.type_return == (int,)
			
	def test_failure_1(self):
		from typecheck import typecheck_return, TypeCheckError, _TC_TypeError
		
		@typecheck_return(int, int, int)
		def foo():
			return 5, 6
			
		assert foo.type_return == (int, int, int)

		try:
			foo()
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_TypeError)
			assert e.internal.right == (int, int, int)
			assert e.internal.wrong == (int, int)
			self.assertEqual(str(e), "in (5, 6), expected (<type 'int'>, <type 'int'>, <type 'int'>), got (<type 'int'>, <type 'int'>)")
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_failure_2(self):
		from typecheck import typecheck_return, TypeCheckError
		from typecheck import _TC_TypeError, _TC_IndexError

		@typecheck_return([int])
		def foo():
			return [4,5,6.0]
		
		assert foo.type_return == [int]
			
		try:
			foo()
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 2
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.wrong == float
			assert e.internal.inner.right == int
			self.assertEqual(str(e), "in [4, 5, 6.0], at index 2, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_failure_3(self):
		from typecheck import typecheck_return, TypeCheckError
		from typecheck import _TC_TypeError, _TC_IndexError

		@typecheck_return([int], int, str)
		def foo():
			return [4,5,6], 5, ["foo"]
			
		assert foo.type_return == ([int], int, str)
			
		try:
			foo()
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 2
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.wrong == [str]
			assert e.internal.inner.right == str
			self.assertEqual(str(e), "in ([4, 5, 6], 5, ['foo']), at index 2, expected <type 'str'>, got [<type 'str'>]")
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_failure_4(self):
		from typecheck import typecheck_return, TypeCheckError, _TC_TypeError

		@typecheck_return( (int,) )
		def foo():
			return 7
			
		assert foo.type_return == (int,)
			
		try:
			foo()
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_TypeError)
			assert e.internal.right == (int,)
			assert e.internal.wrong == int
			self.assertEqual(str(e), "in 7, expected (<type 'int'>,), got <type 'int'>")
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_decorator_returns_function(self):
		from typecheck import typecheck_return

		@typecheck_return( (int,) )
		def foo():
			return 7
			
		assert isinstance(foo, types.FunctionType)

class Test_typecheck_yield(TestCase):	
	def test_pass(self):
		from typecheck import typecheck_yield
		
		@typecheck_yield(int)
		def foo(a):
			yield a
			yield a+1
			yield a+2
		
		gen = foo(5)	
			
		assert gen.next() == 5
		assert gen.next() == 6
		assert gen.next() == 7
		
		assert foo.type_yield == int
		assert gen.type_yield == foo.type_yield
		
		try:
			gen.next()
		except StopIteration:
			pass
		else:
			raise AssertionError("Failed to raise the proper exception")
	
	def test_fail(self):
		from typecheck import typecheck_yield, TypeCheckError
		from typecheck import _TC_GeneratorError, _TC_TypeError
		
		@typecheck_yield(int)
		def foo(a):
			yield a
		
		gen = foo(5.0)
		
		assert foo.type_yield == int
		assert gen.type_yield == foo.type_yield
			
		try:
			gen.next()
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_GeneratorError)
			assert e.internal.yield_no == 1
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "At yield #1: in 5.0, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")
		try:
			gen.next()
		except StopIteration:
			pass
		else:
			raise AssertionError("Failed to raise the proper exception")
			
	def test_restartable(self):
		from typecheck import typecheck_yield
		
		@typecheck_yield(int)
		def foo(a):
			yield a
			yield a+1
			yield a+2

		assert foo.type_yield == int
		assert foo(5).type_yield == foo.type_yield
			
		for _ in (1, 2):
			gen = foo(5)
			
			assert gen.type_yield == foo.type_yield

			assert gen.next() == 5
			assert gen.next() == 6
			assert gen.next() == 7
			
			try:
				gen.next()
			except StopIteration:
				pass
			else:
				raise AssertionError("Failed to raise the proper exception")
			
	def test_fails_on_non_generators(self):
		from typecheck import typecheck_yield
		
		@typecheck_yield(int)
		def foo(a):
			return a+1
		
		try:	
			assert foo(5) == 6
		except TypeError, e:
			self.assertEqual(str(e), "typecheck_yield only works for generators")
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_decorator_returns_function(self):
		from typecheck import typecheck_yield

		@typecheck_yield(int)
		def foo():
			yield 7
	
		assert isinstance(foo, types.FunctionType)

class Test_typecheck_args(TestCase):
	def test_success_single_positional(self):
		from typecheck import typecheck_args
	
		@typecheck_args(int)
		def foo(int_1):
			return int_1

		assert foo(6) == 6
		
		assert foo.type_args_pos == (int,)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}

	def test_success_multiple_positional(self):
		from typecheck import typecheck_args
	
		@typecheck_args(int, int, int)
		def foo(int_1, int_2, int_3):
			return int_1, int_2, int_3

		assert foo(1, 2, 3) == (1, 2, 3)
		assert foo.type_args_pos == (int, int, int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}

	def test_success_multiple_positional_type_by_kw(self):
		from typecheck import typecheck_args
	
		@typecheck_args(int_2=int, int_1=int, int_3=int)
		def foo(int_1, int_2, int_3):
			return int_1, int_2, int_3

		assert foo(1, 2, 3) == (1, 2, 3)
		
		assert foo.type_args_pos == (int, int, int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
	def test_success_multiple_keyword(self):
		from typecheck import typecheck_args
		
		@typecheck_args(kw_1=int, kw_2=int, kw_3=int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)

		assert foo() == (5, 6, 7)
		assert foo(9, 9, 9) == (9, 9, 9)
		assert foo(kw_1=33, kw_3=88) == (33, 6, 88)
		assert foo(kw_3=55, kw_2=2) == (5, 2, 55)
		
		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {'kw_1': int, 'kw_2': int, 'kw_3': int}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
	def test_success_multiple_keyword_type_by_pos(self):
		from typecheck import typecheck_args
		
		# Checking type-specification, not arg-passing
		@typecheck_args(int, int, int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)

		assert foo() == (5, 6, 7)
		assert foo(9, 9, 9) == (9, 9, 9)
		assert foo(kw_1=33, kw_3=88) == (33, 6, 88)
		assert foo(kw_3=55, kw_2=2) == (5, 2, 55)
		
		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {'kw_1': int, 'kw_2': int, 'kw_3': int}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
	def test_success_kwargs_form_1(self):
		from typecheck import typecheck_args

		# Type can be passed as a single type...
		# (in this case, the values of the dict
		# will be checked against the given type)
		@typecheck_args(kwargs=int)
		def foo(**kwargs):
			return kwargs 
		
		assert foo() == {}
		assert foo(int_1=5, int_2=8) == {'int_1': 5, 'int_2': 8}
		
		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {str: int}
		
	def test_success_kwargs_form_2(self):
		from typecheck import typecheck_args

		# ...or in normal dict form
		# (in this case, full checking is done)
		@typecheck_args(kwargs={str: int})
		def foo(**kwargs):
			return kwargs 
		
		assert foo() == {}
		assert foo(int_1=5, int_2=8) == {'int_1': 5, 'int_2': 8}
		
		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {str: int}
		
	def test_success_vargs_form_1(self):
		from typecheck import typecheck_args

		# Type can be passed as a single type...
		@typecheck_args(vargs=int)
		def foo(*vargs):
			return vargs 
		
		assert foo() == ()
		assert foo(5, 8) == (5, 8)
		
		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == [int]
		assert foo.type_args_kwargs == {}
		
	def test_success_vargs_form_2(self):
		from typecheck import typecheck_args

		# ...or as an actual tuple. Note that
		# this form is useful if you want to
		# specify patterned tuples
		@typecheck_args(vargs=[int])
		def foo(*vargs):
			return vargs 
		
		assert foo() == ()
		assert foo(5, 8) == (5, 8)
		
		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == [int]
		assert foo.type_args_kwargs == {}
		
	def test_success_pos_and_kw(self):
		from typecheck import typecheck_args
		
		@typecheck_args(int, int, foo=int)
		def foo(req_1, req_2, foo=7):
			return (req_1, req_2, foo)
		
		assert foo(5, 6, foo=88) == (5, 6, 88)
		assert foo(5, 6) == (5, 6, 7)
		assert foo(foo=5, req_2=44, req_1=99) == (99, 44, 5)
		
		assert foo.type_args_pos == (int, int)
		assert foo.type_args_kw == {'foo': int}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
	def test_success_unpacked_tuples(self):
		from typecheck import typecheck_args
		
		@typecheck_args(int, (int, (int, int)), int)
		def foo(req_1, (req_2, (req_3, req_4)), req_5):
			return (req_1, req_2, req_3, req_4, req_5)
		
		assert foo(4, (5, (6, 7)), 8) == (4, 5, 6, 7, 8)
		
		assert foo.type_args_pos == (int, (int, (int, int)), int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}

	def test_failure_single_positional(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_IndexError
	
		@typecheck_args(int)
		def foo(int_1):
			return 7

		assert foo.type_args_pos == (int,)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}

		try:
			foo(6.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in (6.0,), at index 0, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_failure_multiple_positional(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_IndexError
	
		@typecheck_args(int, int, int)
		def foo(int_1, int_2, int_3):
			return 7

		assert foo.type_args_pos == (int, int, int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}

		try:
			foo(1, 2, 3.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 2
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in (1, 2, 3.0), at index 2, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_failure_multiple_positional_type_by_kw(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_IndexError
	
		@typecheck_args(int_2=int, int_1=int, int_3=int)
		def foo(int_1, int_2, int_3):
			return 7

		assert foo.type_args_pos == (int, int, int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}

		try:
			foo(1, 2, 3.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 2
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in (1, 2, 3.0), at index 2, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_failure_multiple_keyword_1(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_KeyValError
		
		@typecheck_args(kw_1=int, kw_2=int, kw_3=int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)

		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {'kw_1': int, 'kw_2': int, 'kw_3': int}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}

		try:
			foo(9.0, 9, 9)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_KeyValError)
			assert e.internal.key == 'kw_1'
			assert e.internal.val == 9.0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in {'kw_1': 9.0, 'kw_2': 9, 'kw_3': 9}, at key 'kw_1', value 9.0, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")		

	def test_failure_multiple_keyword_2(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_KeyValError
		
		@typecheck_args(kw_1=int, kw_2=int, kw_3=int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)

		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {'kw_1': int, 'kw_2': int, 'kw_3': int}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
		try:
			foo(kw_1=9.0, kw_3=88)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_KeyValError)
			assert e.internal.key == 'kw_1'
			assert e.internal.val == 9.0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in {'kw_1': 9.0, 'kw_3': 88}, at key 'kw_1', value 9.0, expected <type 'int'>, got <type 'float'>")
			
	def test_failure_multiple_keyword_3(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_KeyValError
		
		@typecheck_args(kw_1=int, kw_2=int, kw_3=int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)

		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {'kw_1': int, 'kw_2': int, 'kw_3': int}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
		try:
			foo(kw_3=9.0, kw_1=88)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_KeyValError)
			assert e.internal.key == 'kw_3'
			assert e.internal.val == 9.0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in {'kw_1': 88, 'kw_3': 9.0}, at key 'kw_3', value 9.0, expected <type 'int'>, got <type 'float'>")

	def test_failure_multiple_keyword_type_by_pos_1(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_KeyValError
		
		@typecheck_args(int, int, int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)

		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {'kw_1':int, 'kw_2': int, 'kw_3': int}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}

		try:
			foo(9.0, 9, 9)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_KeyValError)
			assert e.internal.key == 'kw_1'
			assert e.internal.val == 9.0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in {'kw_1': 9.0, 'kw_2': 9, 'kw_3': 9}, at key 'kw_1', value 9.0, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")		

	def test_failure_multiple_keyword_type_by_pos_2(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_KeyValError
		
		@typecheck_args(int, int, int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)

		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {'kw_1':int, 'kw_2': int, 'kw_3': int}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
		try:
			foo(kw_1=9.0, kw_3=88)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_KeyValError)
			assert e.internal.key == 'kw_1'
			assert e.internal.val == 9.0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in {'kw_1': 9.0, 'kw_3': 88}, at key 'kw_1', value 9.0, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")	
			
	def test_failure_multiple_keyword_type_by_pos_3(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_KeyValError
		
		@typecheck_args(int, int, kw_3=int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)

		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {'kw_1':int, 'kw_2': int, 'kw_3': int}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
		try:
			foo(kw_3=9.0, kw_1=88)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_KeyValError)
			assert e.internal.key == 'kw_3'
			assert e.internal.val == 9.0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in {'kw_1': 88, 'kw_3': 9.0}, at key 'kw_3', value 9.0, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_failure_kwargs_form_1(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_KeyValError

		# Type can be passed as a single type...
		# (in this case, the values of the dict
		# will be checked against the given type)
		@typecheck_args(kwargs=int)
		def foo(**kwargs):
			return kwargs
			
		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {str: int}
		
		try:
			foo(int_1=5.0, int_2=8)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_KeyValError)
			assert e.internal.key == 'int_1'
			assert e.internal.val == 5.0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in {'int_1': 5.0, 'int_2': 8}, at key 'int_1', value 5.0, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_failure_kwargs_form_2(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_KeyValError

		# ...or in normal dict form
		# (in this case, full checking is done)
		@typecheck_args(kwargs={str: int})
		def foo(**kwargs):
			return kwargs
			
		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {str: int}
		
		try:
			foo(int_1=5.0, int_2=99)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_KeyValError)
			assert e.internal.key == 'int_1'
			assert e.internal.val == 5.0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in {'int_1': 5.0, 'int_2': 99}, at key 'int_1', value 5.0, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_failure_vargs_form_1(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_IndexError

		# Type can be passed as a single type...
		@typecheck_args(vargs=int)
		def foo(*vargs):
			return vargs
			
		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == [int]
		assert foo.type_args_kwargs == {}
		
		try:
			foo(5, 8.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 1
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in [5, 8.0], at index 1, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_failure_vargs_form_2(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_IndexError

		# ...or as an actual list. Note that
		# this form is useful if you want to
		# specify patterned lists
		@typecheck_args(vargs=[int])
		def foo(*vargs):
			return vargs
			
		assert foo.type_args_pos == ()
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == [int]
		assert foo.type_args_kwargs == {}
		
		try:
			foo(5, 8.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 1
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in [5, 8.0], at index 1, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_failure_pos_and_kw_1(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_IndexError
		
		@typecheck_args(int, int, foo=int)
		def foo(req_1, req_2, foo=7):
			return (req_1, req_2, foo)
			
		assert foo.type_args_pos == (int, int)
		assert foo.type_args_kw == {'foo': int}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
		try:
			foo(5, 6.0, foo=88)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 1
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in (5, 6.0), at index 1, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_failure_pos_and_kw_2(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_KeyValError
		
		@typecheck_args(int, int, foo=int)
		def foo(req_1, req_2, foo=7):
			return (req_1, req_2, foo)
			
		assert foo.type_args_pos == (int, int)
		assert foo.type_args_kw == {'foo': int}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
		try:
			foo(5, 6, foo=88.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_KeyValError)
			assert e.internal.key == 'foo'
			assert e.internal.val == 88.0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in {'foo': 88.0}, at key 'foo', value 88.0, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")	
		
	def test_failure_pos_and_kw_3(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_IndexError
		
		@typecheck_args(int, int, foo=int)
		def foo(req_1, req_2, foo=7):
			return (req_1, req_2, foo)
			
		assert foo.type_args_pos == (int, int)
		assert foo.type_args_kw == {'foo': int}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
		try:
			foo(foo=5, req_2=44, req_1=99.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in (99.0, 44), at index 0, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_failure_unpacked_tuples_1(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_IndexError, _TC_TypeError
		
		@typecheck_args(int, (int, (int, int)), int)
		def foo(a, (b, (c, d)), e):
			return a, b, c, d, e
			
		assert foo.type_args_pos == (int, (int, (int, int)), int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
			
		try:
			foo(5, (6, (7, 8.0)), 9)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 1
			assert isinstance(e.internal.inner, _TC_IndexError)
			assert e.internal.inner.index == 1
			assert isinstance(e.internal.inner.inner, _TC_IndexError)
			assert e.internal.inner.inner.index == 1
			assert isinstance(e.internal.inner.inner.inner, _TC_TypeError)
			assert e.internal.inner.inner.inner.right == int
			assert e.internal.inner.inner.inner.wrong == float
			self.assertEqual(str(e), "in (5, (6, (7, 8.0)), 9), at index 1, at index 1, at index 1, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")	
			
	def test_failure_unpacked_tuples_2(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_IndexError
		
		@typecheck_args(int, (int, (int, int)), int)
		def foo(a, (b, (c, d)), e):
			return a, b, c, d, e
			
		assert foo.type_args_pos == (int, (int, (int, int)), int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
			
		try:
			foo(5, (6, 4), 9)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 1
			assert isinstance(e.internal.inner, _TC_IndexError)
			assert e.internal.inner.index == 1
			assert isinstance(e.internal.inner.inner, _TC_TypeError)
			assert e.internal.inner.inner.right == (int, int)
			assert e.internal.inner.inner.wrong == int
			self.assertEqual(str(e), "in (5, (6, 4), 9), at index 1, at index 1, expected (<type 'int'>, <type 'int'>), got <type 'int'>")
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_failure_unpacked_tuples_3(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_TypeError, _TC_IndexError
		
		@typecheck_args(int, (int, (int, int)), int)
		def foo(a, (b, (c, d)), e):
			return a, b, c, d, e
			
		assert foo.type_args_pos == (int, (int, (int, int)), int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
			
		try:
			foo(5, (6, (7, 8)), (9, 10))
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 2
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == (int, int)
			self.assertEqual(str(e), "in (5, (6, (7, 8)), (9, 10)), at index 2, expected <type 'int'>, got (<type 'int'>, <type 'int'>)")
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_empty_vargs_and_kwargs_implicit_success(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_IndexError

		@typecheck_args(int, int, int)
		def foo(a, b, c):
			return a, b, c
			
		assert foo.type_args_pos == (int, int, int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
			
		assert foo(2, 3, 4) == (2, 3, 4)
		
	def test_empty_vargs_explicit_success(self):
		from typecheck import typecheck_args, Empty

		@typecheck_args(int, int, int, Empty(list))
		def foo(a, b, c, *vargs):
			return a, b, c, vargs
			
		assert foo.type_args_pos == (int, int, int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
			
		assert foo(2, 3, 4) == (2, 3, 4, ())		

	def test_empty_vargs_implicit_failure(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_LengthError

		@typecheck_args(int, int, int)
		def foo(a, b, c):
			return a, b, c
			
		assert foo.type_args_pos == (int, int, int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
		try:
			foo(2, 3, 4, 5)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_LengthError)
			assert e.internal.right == 0
			assert e.internal.wrong == 1
			self.assertEqual(str(e), "in [5], length was 1, expected 0")
		else:
			raise AssertionError("Succeeded incorrectly")
		
	def test_empty_vargs_explicit_failure(self):
		from typecheck import typecheck_args, Empty, TypeCheckError, _TC_LengthError

		@typecheck_args(int, int, int, Empty(list))
		def foo(a, b, c, *vargs):
			return a, b, c
			
		assert foo.type_args_pos == (int, int, int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
		try:
			foo(2, 3, 4, 5, 6)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_LengthError)
			assert e.internal.right == 0
			assert e.internal.wrong == 2
			self.assertEqual(str(e), "in [5, 6], length was 2, expected 0")
		else:
			raise AssertionError("Succeeded incorrectly")
		
	def test_empty_kwargs_explicit_success(self):
		from typecheck import typecheck_args, Empty

		@typecheck_args(int, int, int, Empty(dict))
		def foo(a, b, c, **kwargs):
			return a, b, c, kwargs
			
		assert foo.type_args_pos == (int, int, int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
			
		assert foo(2, 3, 4) == (2, 3, 4, {})		

	def test_empty_kwargs_implicit_failure(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_LengthError
		from typecheck import _TC_DictError

		@typecheck_args(int, int, int)
		def foo(a, b, c):
			return a, b, c
			
		assert foo.type_args_pos == (int, int, int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
		try:
			foo(2, 3, 4, d=5, e=6)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_DictError)
			assert isinstance(e.internal.inner, _TC_LengthError)
			assert e.internal.inner.right == 0
			assert e.internal.inner.wrong == 2
			self.assertEqual(str(e), "in {'d': 5, 'e': 6}, length was 2, expected 0")
		else:
			raise AssertionError("Succeeded incorrectly")
		
	def test_empty_kwargs_explicit_failure(self):
		from typecheck import typecheck_args, Empty, TypeCheckError, _TC_LengthError
		from typecheck import _TC_DictError

		@typecheck_args(int, int, int, Empty(dict))
		def foo(a, b, c, **kwargs):
			return a, b, c, kwargs
			
		assert foo.type_args_pos == (int, int, int)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
		try:
			foo(2, 3, 4, r=5, t=6)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_DictError)
			assert isinstance(e.internal.inner, _TC_LengthError)
			assert e.internal.inner.right == 0
			assert e.internal.inner.wrong == 2
			self.assertEqual(str(e), "in {'r': 5, 't': 6}, length was 2, expected 0")
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_generators_pass(self):
		from typecheck import typecheck_args
		
		@typecheck_args(int)
		def foo(a):
			yield a
			yield a+1
			yield a+2
			
		gen = foo(5)	
			
		assert gen.next() == 5
		assert gen.next() == 6
		assert gen.next() == 7
		
		assert foo.type_args_pos == (int,)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
		
	def test_generators_fail(self):
		from typecheck import typecheck_args, TypeCheckError
		from typecheck import _TC_IndexError, _TC_TypeError
		
		@typecheck_args(int)
		def foo(a):
			yield a
			yield a+1
			yield a+2
			
		assert foo.type_args_pos == (int,)
		assert foo.type_args_kw == {}
		assert foo.type_args_vargs == []
		assert foo.type_args_kwargs == {}
			
		try:
			foo(5.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.right == int
			assert e.internal.inner.wrong == float
			self.assertEqual(str(e), "in (5.0,), at index 0, expected <type 'int'>, got <type 'float'>")
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_bad_signature_missing_pos(self):
		from typecheck import typecheck_args, TypeSignatureError
		from typecheck import _TS_MissingTypeError
		
		try:
			@typecheck_args(int, int, int)
			def foo(a, b, c, e):
				return a, b, c, e
		except TypeSignatureError, e:
			assert isinstance(e.internal, _TS_MissingTypeError)
			assert e.internal.parameter == 'e'
			self.assertEqual(str(e), "parameter 'e' lacks a type")
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_bad_signature_missing_kw(self):
		from typecheck import typecheck_args, TypeSignatureError
		from typecheck import _TS_MissingTypeError
		
		try:
			@typecheck_args(a=int, b=int, c=int)
			def foo(a=5, b=6, c=7, d=8):
				return a, b, c, d
		except TypeSignatureError, e:
			assert isinstance(e.internal, _TS_MissingTypeError)
			assert e.internal.parameter == 'd'
			self.assertEqual(str(e), "parameter 'd' lacks a type")
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_bad_signature_duplicate_kw(self):
		from typecheck import typecheck_args, TypeSignatureError
		from typecheck import _TS_TwiceTypedError
		
		try:
			@typecheck_args(int, a=int, b=int, c=int)
			def foo(a=5, b=6, c=7):
				return a, b, c
		except TypeSignatureError, e:
			assert isinstance(e.internal, _TS_TwiceTypedError)
			assert e.internal.parameter == 'a'
			assert e.internal.kw_type == int
			assert e.internal.pos_type == int
			self.assertEqual(str(e), "parameter 'a' is provided two types (<type 'int'> and <type 'int'>)")
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_bad_signature_extra_pos(self):
		from typecheck import typecheck_args, TypeSignatureError
		from typecheck import _TS_ExtraPositionalError
		
		try:
			@typecheck_args(int, int, int, int)
			def foo(a, b, c):
				return a, b, c
		except TypeSignatureError, e:
			assert isinstance(e.internal, _TS_ExtraPositionalError)
			assert e.internal.type == int
			self.assertEqual(str(e), "an extra positional type has been supplied")
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_bad_signature_extra_kw(self):
		from typecheck import typecheck_args, TypeSignatureError
		from typecheck import _TS_ExtraKeywordError
		
		try:
			@typecheck_args(a=int, b=int, c=int)
			def foo(a=5, b=6):
				return a, b
		except TypeSignatureError, e:
			assert isinstance(e.internal, _TS_ExtraKeywordError)
			assert e.internal.keyword == 'c'
			self.assertEqual(str(e), "the keyword 'c' in the signature is not in the function")
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_bad_signature_unpack_nonsequence(self):
		from typecheck import typecheck_args, TypeSignatureError
		from typecheck import _TS_TupleError
		
		try:
			@typecheck_args(int, int)
			def foo(a, (b, c)):
				return a, b, c
		except TypeSignatureError, e:
			assert isinstance(e.internal, _TS_TupleError)
			assert e.internal.parameters == ('b', 'c')
			assert e.internal.types == int
			self.assertEqual(str(e), "the signature type <type 'int'> does not match ('b', 'c')")
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_bad_signature_unpack_bad_sequence_1(self):
		from typecheck import typecheck_args, TypeSignatureError
		from typecheck import _TS_TupleError
		
		try:
			@typecheck_args(int, (int, int, int))
			def foo(a, (b, c)):
				return a, b, c
		except TypeSignatureError, e:
			assert isinstance(e.internal, _TS_TupleError)
			assert e.internal.parameters == ('b', 'c')
			assert e.internal.types == (int, int, int)
			self.assertEqual(str(e), "the signature type (<type 'int'>, <type 'int'>, <type 'int'>) does not match ('b', 'c')")
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_bad_signature_unpack_bad_sequence_2(self):
		from typecheck import typecheck_args, TypeSignatureError
		from typecheck import _TS_TupleError
		
		try:
			@typecheck_args(int, (int, int))
			def foo(a, (b, c, d)):
				return a, b, c, d
		except TypeSignatureError, e:
			assert isinstance(e.internal, _TS_TupleError)
			assert e.internal.parameters == ('b', 'c', 'd')
			assert e.internal.types == (int, int)
			self.assertEqual(str(e), "the signature type (<type 'int'>, <type 'int'>) does not match ('b', 'c', 'd')")
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_bad_signature_unpack_bad_sequence_3(self):
		from typecheck import typecheck_args, TypeSignatureError
		from typecheck import _TS_TupleError
		
		try:
			@typecheck_args(int, (int, (int, int), (int, int)))
			def foo(a, (b, (c, d, e), (f, g))):
				return a, b, c, d, e, f, g
		except TypeSignatureError, e:
			assert isinstance(e.internal, _TS_TupleError)
			assert e.internal.parameters == ('b', ('c', 'd', 'e'), ('f', 'g'))
			assert e.internal.types == (int, (int, int), (int, int))
			self.assertEqual(str(e), "the signature type (<type 'int'>, (<type 'int'>, <type 'int'>), (<type 'int'>, <type 'int'>)) does not match ('b', ('c', 'd', 'e'), ('f', 'g'))")
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_decorator_returns_function(self):
		from typecheck import typecheck_args

		@typecheck_args(int)
		def foo(a):
			return 7
			
		assert isinstance(foo, types.FunctionType)

class Test_cooperation(TestCase):
	def test_args_pass_return_pass(self):
		from typecheck import typecheck_args, typecheck_return

		def run_test(dec_1, dec_2):
			@dec_1(int, int)
			@dec_2(int, int)
			def foo(a, b):
				return a, b

			assert foo(5, 6) == (5, 6)

			assert foo.type_return == (int, int)
			assert foo.type_args_pos == (int, int)
			assert foo.type_args_kw == {}
			assert foo.type_args_vargs == []
			assert foo.type_args_kwargs == {}
			
		run_test(typecheck_args, typecheck_return)
		run_test(typecheck_return, typecheck_args)
		
	def test_args_pass_return_fail(self):
		from typecheck import typecheck_args, typecheck_return
		from typecheck import TypeCheckError, _TC_IndexError, _TC_TypeError

		def run_test(dec_1, dec_2):
			@dec_1(int, int)
			@dec_2(int, int)
			def foo(a, b):
				return a, float(b)

			assert foo.type_return == (int, int)
			assert foo.type_args_pos == (int, int)
			assert foo.type_args_kw == {}
			assert foo.type_args_vargs == []
			assert foo.type_args_kwargs == {}

			try:
				foo(5, 6)
			except TypeCheckError, e:
				assert isinstance(e.internal, _TC_IndexError)
				assert e.internal.index == 1
				assert isinstance(e.internal.inner, _TC_TypeError)
				assert e.internal.inner.right == int
				assert e.internal.inner.wrong == float
				self.assertEqual(str(e), "in (5, 6.0), at index 1, expected <type 'int'>, got <type 'float'>")
			else:
				raise AssertionError("Succeeded incorrectly")
				
		run_test(typecheck_args, typecheck_return)
		run_test(typecheck_return, typecheck_args)
		
	def test_args_return_builds_function(self):
		from typecheck import typecheck_args, typecheck_return
		
		def run_test(dec_1, dec_2):
			@dec_1(int, int)
			@dec_2(int, int)
			def foo(a, b):
				return a, float(b)

			assert isinstance(foo, types.FunctionType)
				
		run_test(typecheck_args, typecheck_return)
		run_test(typecheck_return, typecheck_args)

	def test_args_pass_yield_pass(self):
		from typecheck import typecheck_args, typecheck_yield

		def run_test(dec_1, dec_2):
			@dec_1(int, int)
			@dec_2(int, int)
			def foo(a, b):
				yield a, b
				yield a+1, b
				yield a, b+1

			assert foo.type_yield == (int, int)
			assert foo.type_args_pos == (int, int)
			assert foo.type_args_kw == {}
			assert foo.type_args_vargs == []
			assert foo.type_args_kwargs == {}		

			gen = foo(5, 6)
			assert gen.next() == (5, 6)
			assert gen.next() == (6, 6)
			assert gen.next() == (5, 7)

			assert gen.type_yield == foo.type_yield
			
			try:
				gen.next()
			except StopIteration:
				pass
			else:
				raise AssertionError("Failed to raise the proper exception")
			
		run_test(typecheck_args, typecheck_yield)
		run_test(typecheck_yield, typecheck_args)
			
	def test_args_pass_yield_fail(self):
		from typecheck import typecheck_args, typecheck_yield
		from typecheck import TypeCheckError, _TC_IndexError, _TC_TypeError
		from typecheck import _TC_GeneratorError

		def run_test(dec_1, dec_2):
			@dec_1(int, int)
			@dec_2(int, int)
			def foo(a, b):
				yield a, b
				yield a, float(b)

			assert foo.type_yield == (int, int)
			assert foo.type_args_pos == (int, int)
			assert foo.type_args_kw == {}
			assert foo.type_args_vargs == []
			assert foo.type_args_kwargs == {}

			gen = foo(5, 6)
			assert gen.type_yield == foo.type_yield
			assert gen.next() == (5, 6)

			try:
				gen.next()
			except TypeCheckError, e:
				assert isinstance(e.internal, _TC_GeneratorError)
				assert e.internal.yield_no == 2
				assert isinstance(e.internal.inner, _TC_IndexError)
				assert e.internal.inner.index == 1
				assert isinstance(e.internal.inner.inner, _TC_TypeError)
				assert e.internal.inner.inner.right == int
				assert e.internal.inner.inner.wrong == float
				self.assertEqual(str(e), "At yield #2: in (5, 6.0), at index 1, expected <type 'int'>, got <type 'float'>")
			else:
				raise AssertionError("Succeeded incorrectly")
			
			try:
				gen.next()
			except StopIteration:
				pass
			else:
				raise AssertionError("Failed to raise the proper exception")
				
		run_test(typecheck_args, typecheck_yield)
		run_test(typecheck_yield, typecheck_args)
		
	def test_args_yield_builds_function(self):
		from typecheck import typecheck_args, typecheck_yield
		
		def run_test(dec_1, dec_2):
			@dec_1(int, int)
			@dec_2(int, int)
			def foo(a, b):
				yield a, float(b)

			assert isinstance(foo, types.FunctionType)
				
		run_test(typecheck_args, typecheck_yield)
		run_test(typecheck_yield, typecheck_args)

	def __test_doubler(self, decorator):
		try:
			@decorator(int, int)
			@decorator(int, int)
			def foo(a, b):
				return a, b
		except RuntimeError, e:
			self.assertEqual(str(e), 'Cannot use the same typecheck_* function more than once on the same function')
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_double_typecheck_args(self):
		from typecheck import typecheck_args
		
		self.__test_doubler(typecheck_args)
			
	def test_double_typecheck_return(self):
		from typecheck import typecheck_return
		
		self.__test_doubler(typecheck_return)
		
	def test_double_typecheck_yield(self):
		from typecheck import typecheck_yield
		
		self.__test_doubler(typecheck_yield)
		
	def test_return_and_yield(self):
		from typecheck import typecheck_yield, typecheck_return
		
		try:
			@typecheck_yield(int, int)
			@typecheck_return(int, int)
			def foo(a, b):
				return a, b
		except RuntimeError, e:
			self.assertEqual(str(e), 'Cannot use typecheck_return and typecheck_yield on the same function')
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_no_double_execution_return(self):
		from typecheck import typecheck_args, typecheck_return

		def double_execution(dec_1, dec_2):
			# We need to make sure that the function only gets executed once,
			# even if it's wrapped by two decorators
			usage_counter = [0]

			@dec_1(int)
			@dec_2(int)
			def foo(a):
				usage_counter[0] += 1

				return a

			assert foo(5) == 5
			assert usage_counter[0] == 1
		
		double_execution(typecheck_args, typecheck_return)
		double_execution(typecheck_return, typecheck_args)
		
	def test_no_double_execution_yield(self):
		from typecheck import typecheck_args, typecheck_yield
		
		def double_execution(dec_1, dec_2):
			# We need to make sure that the function only gets executed once,
			# even if it's wrapped by two decorators
			usage_counter = [0]

			@dec_1(int)
			@dec_2(int)
			def foo(a):
				usage_counter[0] += 1

				yield a

			gen = foo(5)
			assert gen.next() == 5
			assert usage_counter[0] == 1
			
			try:
				gen.next()
			except StopIteration:
				pass
			else:
				raise AssertionError("Failed to raise the proper exception")
		
		double_execution(typecheck_args, typecheck_yield)
		double_execution(typecheck_yield, typecheck_args)
		
	def test_verify_args_checked_first__return(self):
		from typecheck import typecheck_args, typecheck_return
		from typecheck import TypeCheckError, _TC_IndexError, _TC_TypeError
		
		def run_test(dec_1, dec_2):
			@dec_1
			@dec_2
			def foo(a, b):
				return 'a'
				
			try:
				assert foo(5.0, 6.0) == 5.0
			except TypeCheckError, e:
				assert isinstance(e.internal, _TC_IndexError)
				assert e.internal.index == 0
				assert isinstance(e.internal.inner, _TC_TypeError)
				assert e.internal.inner.right == int
				assert e.internal.inner.wrong == float
				self.assertEqual(str(e), "in (5.0, 6.0), at index 0, expected <type 'int'>, got <type 'float'>")
			else:
				raise AssertionError("Failed to raise the proper exception")
		
		run_test(typecheck_args(int, int), typecheck_return(float))
		run_test(typecheck_return(float), typecheck_args(int, int))
		
	def test_verify_args_checked_first__yield(self):
		from typecheck import typecheck_args, typecheck_yield
		from typecheck import TypeCheckError, _TC_IndexError, _TC_TypeError
		
		def run_test(dec_1, dec_2):
			@dec_1
			@dec_2
			def foo(a, b):
				yield 'a'
				
			try:
				assert foo(5.0, 6.0).next() == 5.0
			except TypeCheckError, e:
				assert isinstance(e.internal, _TC_IndexError)
				assert e.internal.index == 0
				assert isinstance(e.internal.inner, _TC_TypeError)
				assert e.internal.inner.right == int
				assert e.internal.inner.wrong == float
				self.assertEqual(str(e), "in (5.0, 6.0), at index 0, expected <type 'int'>, got <type 'float'>")
			else:
				raise AssertionError("Failed to raise the proper exception")
		
		run_test(typecheck_args(int, int), typecheck_yield(float))
		run_test(typecheck_yield(float), typecheck_args(int, int))

class Test_Self_class(TestCase):
	def test_self_in_args_pass(self):
		from typecheck import typecheck_args, Self
		
		class Test(object):
			@typecheck_args(Self(), int, Self())
			def foo(self, a, b):
				return a, b
		
		t = Test()
		assert Test().foo(4, t) == (4, t)
		
		assert Test.foo.type_args_pos == (Self(), int, Self())
		assert Test.foo.type_args_kw == {}
		assert Test.foo.type_args_vargs == []
		assert Test.foo.type_args_kwargs == {}
	
	def test_self_in_args_fail_1(self):
		from typecheck import typecheck_args, Self, TypeCheckError
		from typecheck import _TC_IndexError, _TC_TypeError
		
		class Test(object):
			@typecheck_args(Self(), int, Self())
			def foo(self, a, b):
				return a, b
				
		assert Test.foo.type_args_pos == (Self(), int, Self())
		assert Test.foo.type_args_kw == {}
		assert Test.foo.type_args_vargs == []
		assert Test.foo.type_args_kwargs == {}
		
		try:
			assert Test().foo(4, 6) == (4, 6)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 2
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.wrong == int
			assert e.internal.inner.right == Test
		else:
			raise AssertionError("Succeeded incorrectly")
			
	@TODO("Waiting on some way of detecting method-hood in decorators")
	def test_self_in_args_fail_2(self):
		from typecheck import typecheck_args, Self, TypeSignatureError
		
		try:
			@typecheck_args(Self(), int)
			def foo(a, b):
				return a, b
		except TypeSignatureError:
			pass
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_self_in_return_pass(self):
		from typecheck import typecheck_return, Self
		
		class Test(object):
			@typecheck_return(Self(), int, Self())
			def foo(self, a, b):
				return self, a, b
		
		t = Test()
		t_1 = Test()
		assert t_1.foo(4, t) == (t_1, 4, t)
		
		assert Test.foo.type_return == (Self(), int, Self())
	
	def test_self_in_return_fail_1(self):
		from typecheck import typecheck_return, Self, TypeCheckError
		from typecheck import _TC_IndexError, _TC_TypeError
		
		class Test(object):
			@typecheck_return(Self(), int, Self())
			def foo(self, a, b):
				return self, a, b
		
		try:
			t = Test()
			assert t.foo(4, 6) == (t, 4, 6)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 2
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.wrong == int
			assert e.internal.inner.right == Test
		else:
			raise AssertionError("Succeeded incorrectly")
			
		assert Test.foo.type_return == (Self(), int, Self())
		
	@TODO("Waiting on some way of detecting method-hood in decorators")
	def test_self_in_return_fail_2(self):
		from typecheck import typecheck_return, Self, TypeSignatureError
		
		try:
			@typecheck_return(Self(), int)
			def foo(self, a, b):
				return a, b
		except TypeSignatureError:
			pass
		else:
			raise AssertionError("Succeeded incorrectly")

	@TODO("Waiting on some way of detecting method-hood in decorators")
	def test_self_in_return_fail_3(self):
		from typecheck import typecheck_return, Self, TypeCheckError
		from typecheck import _TC_IndexError, _TC_TypeError
		
		class Test(object):
			@typecheck_return(Self(), int, Self())
			def foo(self, a, b):
				return a, a, b
		
		try:
			t = Test()
			assert t.foo(4, 6) == (4, 4, 6)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.wrong == int
			assert e.internal.inner.right == Test
		else:
			raise AssertionError("Succeeded incorrectly")
			
		assert Test.foo.type_return == (Self(), int, Self())
		
	def test_self_in_yield_pass(self):
		from typecheck import typecheck_yield, Self, TypeCheckError
		from typecheck import _TC_IndexError, _TC_TypeError
		from typecheck import _TC_GeneratorError
		
		class Test(object):
			@typecheck_yield(Self(), int, Self())
			def foo(self, a, b):
				yield self, a, self

		t = Test()
		assert t.foo(4, 6).next() == (t, 4, t)
		assert Test.foo.type_yield == (Self(), int, Self())

	@TODO("Waiting on some way of detecting method-hood in decorators")
	def test_self_in_yield_fail(self):
		from typecheck import typecheck_yield, Self, TypeCheckError
		from typecheck import _TC_IndexError, _TC_TypeError
		from typecheck import _TC_GeneratorError
		
		class Test(object):
			@typecheck_yield(Self(), int, Self())
			def foo(self, a, b):
				yield b, a, b
		
		try:
			assert Test().foo(4, 6).next() == (6, 4, 6)
		except TypeCheckError, e:
			assert isinstance(e.internal. _TC_GeneratorError)
			assert e.internal.yield_no == 0
			assert isinstance(e.internal.inner, _TC_IndexError)
			assert e.internal.inner.index == 0
			assert isinstance(e.internal.inner.inner, _TC_TypeError)
			assert e.internal.inner.inner.wrong == int
			assert e.internal.inner.inner.right == Test
		else:
			raise AssertionError("Succeeded incorrectly")
			
		assert Test.foo.type_yield == (Self(), int, Self())
		
	def test_self_in_args_yield_pass(self):
		from typecheck import typecheck_yield, Self, TypeCheckError
		from typecheck import _TC_IndexError, _TC_TypeError
		from typecheck import _TC_GeneratorError, typecheck_args
		
		class Test(object):
			@typecheck_args(Self(), int, int)
			@typecheck_yield(Self(), int, Self())
			def foo(self, a, b):
				yield self, a, self

		t = Test()
		assert t.foo(4, 6).next() == (t, 4, t)
		
		assert Test.foo.type_yield == (Self(), int, Self())
		assert Test.foo.type_args_pos == (Self(), int, int)
		assert Test.foo.type_args_kw == {}
		assert Test.foo.type_args_vargs == []
		assert Test.foo.type_args_kwargs == {}

	def test_self_in_args_yield_fail(self):
		from typecheck import typecheck_yield, Self, TypeCheckError
		from typecheck import _TC_IndexError, _TC_TypeError
		from typecheck import _TC_GeneratorError, typecheck_args
		
		class Test(object):
			@typecheck_args(Self(), int, int)
			@typecheck_yield(Self(), int, Self())
			def foo(self, a, b):
				yield b, a, b

		assert Test.foo.type_yield == (Self(), int, Self())
		assert Test.foo.type_args_pos == (Self(), int, int)
		assert Test.foo.type_args_kw == {}
		assert Test.foo.type_args_vargs == []
		assert Test.foo.type_args_kwargs == {}
		
		try:
			assert Test().foo(4, 6).next() == (6, 4, 6)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_GeneratorError)
			assert e.internal.yield_no == 1
			assert isinstance(e.internal.inner, _TC_IndexError)
			assert e.internal.inner.index == 0
			assert isinstance(e.internal.inner.inner, _TC_TypeError)
			assert e.internal.inner.inner.wrong == int
			assert e.internal.inner.inner.right == Test
		else:
			raise AssertionError("Succeeded incorrectly")
			
class Test_enable_checking_global(TestCase):
	def tearDown(self):
		import typecheck
		
		typecheck.enable_checking = True

	def test_typecheck_args(self):
		from typecheck import typecheck_args, TypeCheckError
		import typecheck
		
		@typecheck_args(int)
		def foo(a):
			return a
		
		typecheck.enable_checking = True
		assert foo(5) == 5
		
		typecheck.enable_checking = False
		assert foo(5.0) == 5.0
		
		typecheck.enable_checking = True
		try:
			assert foo(5.0) == 5.0
		except TypeCheckError:
			pass # We don't need to look at this
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_typecheck_return(self):
		from typecheck import typecheck_return, TypeCheckError
		import typecheck
		
		@typecheck_return(int)
		def foo(a):
			return a
		
		typecheck.enable_checking = True
		assert foo(5) == 5
		
		typecheck.enable_checking = False
		assert foo(5.0) == 5.0
		
		typecheck.enable_checking = True
		try:
			assert foo(5.0) == 5.0
		except TypeCheckError:
			pass # We don't need to look at this
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_typecheck_yield(self):
		from typecheck import typecheck_yield, TypeCheckError
		import typecheck
		
		@typecheck_yield(int)
		def foo(a):
			yield a
		
		typecheck.enable_checking = True
		gen = foo(5)
		assert gen.next() == 5
		try:
			gen.next()
		except StopIteration:
			pass
		else:
			raise AssertionError("Failed to raise the proper exception")
		
		typecheck.enable_checking = False
		gen = foo(5.0)
		assert gen.next() == 5.0
		try:
			gen.next()
		except StopIteration:
			pass
		else:
			raise AssertionError("Failed to raise the proper exception")
		
		typecheck.enable_checking = True
		gen = foo(5.0)
		try:
			assert gen.next() == 5.0
		except TypeCheckError:
			pass # We don't need to look at this
		else:
			raise AssertionError("Succeeded incorrectly")
		try:
			gen.next()
		except StopIteration:
			pass
		else:
			raise AssertionError("Failed to raise the proper exception")
			
class Test_typecheck_alias(TestCase):
	def test_alias(self):
		from typecheck import typecheck_args, typecheck
		
		assert typecheck is typecheck_args
		
class Test_signature_checking_hooks(TestCase):
	def setUp(self):
		from typecheck import register_type
		import types
	
		flags = {'start': [], 'stop': []}
		
		def appender(flag, function):
			if isinstance(function, types.GeneratorType):
				flags[flag].append("gen_%s" % function.gi_frame.f_code.co_name)
			else:
				flags[flag].append(function.__name__)
		
		class Test(object):
			@classmethod
			def __typesig__(cls, obj):
				pass
			
			# This is invoked when we start checking the function
			@classmethod	
			def __startchecking__(cls, function):
				appender('start', function)
				
			@classmethod
			def __switchchecking__(cls, from_func, to_func):
				appender('stop', from_func)
				appender('start', to_func)
			
			# This is invoked when we stop checking the function
			@classmethod	
			def __stopchecking__(cls, function):
				appender('stop', function)
				
		register_type(Test)
		self.Test = Test
		self.flags = flags
	
	def tearDown(self):
		from typecheck import is_registered_type, unregister_type
		
		if is_registered_type(self.Test):
			unregister_type(self.Test)

	def __test_single(self, decorator):
		@decorator(int)
		def foo(a):
			return a
			
		assert foo(5) == 5
		
		assert self.flags['start'] == ['foo']
		assert self.flags['stop'] == ['foo']
		
	def test_args(self):
		from typecheck import typecheck_args
		
		self.__test_single(typecheck_args)
		
	def test_return(self):
		from typecheck import typecheck_return
		
		self.__test_single(typecheck_return)
		
	def test_yield(self):
		from typecheck import typecheck_yield
		
		@typecheck_yield(int)
		def foo(a):
			yield a
		
		gen = foo(5)
		assert self.flags['start'] == ['foo', 'gen_foo']
		assert self.flags['stop'] == ['foo']
		
		assert gen.next() == 5
		assert self.flags['start'] == ['foo' ,'gen_foo']
		assert self.flags['stop'] == ['foo']
		try:
			gen.next()
		except StopIteration:
			assert self.flags['start'] == ['foo' ,'gen_foo']
			assert self.flags['stop'] == ['foo', 'gen_foo']
		else:
			raise AssertionError("Failed to raise StopIteration at the right point")
	
	def test_args_return(self):
		from typecheck import typecheck_return, typecheck_args

		def test_double(dec_1, dec_2):
			self.flags['start'] = []
			self.flags['stop'] = []
		
			@dec_1(int)
			@dec_2(int)
			def foo(a):
				return a

			assert foo(5) == 5

			assert self.flags['start'] == ['foo']
			assert self.flags['stop'] == ['foo']
		
		test_double(typecheck_return, typecheck_args)
		test_double(typecheck_args, typecheck_return)

	def test_args_yield(self):
		from typecheck import typecheck_yield, typecheck_args

		def test_double(dec_1, dec_2):
			self.flags['start'] = []
			self.flags['stop'] = []
		
			@dec_1(int)
			@dec_2(int)
			def foo(a):
				yield a

			gen = foo(5)
			assert self.flags['start'] == ['foo', 'gen_foo']
			assert self.flags['stop'] == ['foo']

			assert gen.next() == 5
			assert self.flags['start'] == ['foo', 'gen_foo']
			assert self.flags['stop'] == ['foo']
			try:
				gen.next()
			except StopIteration:
				assert self.flags['start'] == ['foo', 'gen_foo']
				assert self.flags['stop'] == ['foo', 'gen_foo']
			else:
				raise AssertionError("Failed to raise StopIteration at the right point")
		
		test_double(typecheck_yield, typecheck_args)
		test_double(typecheck_args, typecheck_yield)
	
	def test_handles_exceptions_return(self):
		from typecheck import typecheck_return, typecheck_args
		
		def test_double(dec_1, dec_2):
			self.flags['start'] = []
			self.flags['stop'] = []
		
			@dec_1(int)
			@dec_2(int)
			def foo(a):
				raise RuntimeError()

			try:
				assert foo(5) == 5
			except RuntimeError:
				pass
			else:
				raise AssertionError("Failed to allow RuntimeError through")

			assert self.flags['start'] == ['foo']
			assert self.flags['stop'] == ['foo']
		
		test_double(typecheck_return, typecheck_args)
		test_double(typecheck_args, typecheck_return)

	def test_handles_exceptions_yield(self):
		from typecheck import typecheck_yield, typecheck_args
		
		def test_double(dec_1, dec_2):
			self.flags['start'] = []
			self.flags['stop'] = []
		
			@dec_1(int)
			@dec_2(int)
			def foo(a):
				yield a
				raise RuntimeError()

			gen = foo(5)
			assert self.flags['start'] == ['foo', 'gen_foo']
			assert self.flags['stop'] == ['foo']

			assert gen.next() == 5
			assert self.flags['start'] == ['foo', 'gen_foo']
			assert self.flags['stop'] == ['foo']
			try:
				gen.next()
			except RuntimeError:
				# Note that gen_foo hasn't stopped checking yet
				assert self.flags['start'] == ['foo', 'gen_foo']
				assert self.flags['stop'] == ['foo']
			else:
				raise AssertionError("Failed to raise RuntimeError at the right point")
				
			try:
				gen.next()
			except StopIteration:
				assert self.flags['start'] == ['foo', 'gen_foo']
				assert self.flags['stop'] == ['foo', 'gen_foo']
			else:
				raise AssertionError("Failed to raise StopIteration at the right point")
		
		test_double(typecheck_yield, typecheck_args)
		test_double(typecheck_args, typecheck_yield)
		
	def test_nested_functions(self):
		from typecheck import typecheck_return, typecheck_args
		
		def test_double(dec_1, dec_2):
			self.flags['start'] = []
			self.flags['stop'] = []
		
			@dec_1(int)
			@dec_2(int)
			def bar(a):
				return a
		
			@dec_1(int)
			@dec_2(int)
			def foo(a):
				return bar(a)

			assert foo(5) == 5

			assert self.flags['start'] == ['foo', 'bar']
			assert self.flags['stop'] == ['bar', 'foo']
		
		test_double(typecheck_return, typecheck_args)
		test_double(typecheck_args, typecheck_return)
			
	def test_nested_functions_with_exceptions(self):
		from typecheck import typecheck_return, typecheck_args
		
		def test_double(dec_1, dec_2):
			self.flags['start'] = []
			self.flags['stop'] = []
		
			@dec_1(int)
			@dec_2(int)
			def bar(a):
				raise RuntimeError()
		
			@dec_1(int)
			@dec_2(int)
			def foo(a):
				return bar(a)

			assert foo(5) == 5
		
		for funcs in ((typecheck_return, typecheck_args), (typecheck_args, typecheck_return)):
			try:
				test_double(*funcs)
			except RuntimeError:
				assert self.flags['start'] == ['foo', 'bar']
				assert self.flags['stop'] == ['bar', 'foo']
			else:
				raise AssertionError("Failed to raise the proper exception")
				
	def test_incorrect_generator_usage(self):
		from typecheck import typecheck_yield
		
		@typecheck_yield(int)
		def foo():
			yield 5
			
		def contain_scope():
			assert foo().next() == 5
			
		for i in range(1, 3):
			contain_scope()
			assert self.flags['start'] == ['foo', 'gen_foo'] * i
			assert self.flags['stop'] == ['foo', 'gen_foo'] * i

# We inherit everything else from Test_signature_checking_hooks		
class Test_hooks_ignore_enable_checking(Test_signature_checking_hooks):
		def setUp(self):
			Test_signature_checking_hooks.setUp(self)
			
			typecheck.enable_checking = False
			
		def tearDown(self):
			Test_signature_checking_hooks.tearDown(self)
			
			typecheck.enable_checking = True

def convert_mapping(mapping):
	if mapping is None:
		return None
	return dict([(k, v.type) for k, v in mapping.items()])

def active_mapping():
	from typecheck import TypeVariables as TV
	return convert_mapping(TV._TypeVariables__active_mapping)
		
class TypeVariableTests(TestCase):
	def test_args_and_return_pass(self):
		from typecheck import typecheck_args, typecheck_return
		from typecheck import TypeVariables
		
		def run_test(dec):
			@dec('a', int, 'a')
			def foo(a, b, c):
				return a, b, c

			class A: pass
			a = A()
			for args in ((5, 5, 5), (5.0, 5, 7.0), ([4, 5], 5, [8, 9, 10]), (a, 5, a)):
				assert foo(*args) == args
				assert TypeVariables._TypeVariables__mapping_stack == []
				assert TypeVariables._TypeVariables__active_mapping is None
				assert len(TypeVariables._TypeVariables__gen_mappings) == 0
			
		run_test(typecheck_args)
		run_test(typecheck_return)
		
	def test_args_and_return_fail(self):
		from typecheck import typecheck_args, typecheck_return, calculate_type
		from typecheck import TypeCheckError, _TC_IndexError, _TC_TypeError
		from typecheck import TypeVariables
		
		class Bad: pass
		bad = Bad()
		
		def run_test(dec):
			@dec('a', int, 'a')
			def foo(a, b, c):
				return a, b, c

			class A: pass
			a = A()

			for args in ((5, 5, bad), (5.0, 5, bad), ([4, 5], 5, bad), (a, 5, bad)):
				try:
					foo(*args)
				except TypeCheckError, e:
					assert isinstance(e.internal, _TC_IndexError)
					assert e.internal.index == 2
					assert isinstance(e.internal.inner, _TC_TypeError)
					assert e.internal.inner.right == calculate_type(args[0])
					assert e.internal.inner.wrong == Bad

					assert TypeVariables._TypeVariables__mapping_stack == []
					assert TypeVariables._TypeVariables__active_mapping is None
					assert len(TypeVariables._TypeVariables__gen_mappings) == 0
				else:
					raise AssertionError("Failed to raise TypeCheckError at the proper place")
					
		run_test(typecheck_args)
		run_test(typecheck_return)
		
	def test_yield_pass(self):
		from typecheck import typecheck_yield
		from typecheck import TypeVariables
		
		@typecheck_yield('a', int, 'a')
		def foo(a, b, c):
			yield a, b, c
			
		class A: pass
		a = A()
		for args in ((5, 5, 5), (5.0, 5, 7.0), ([4, 5], 5, [8, 9, 10]), (a, 5, a)):
			g = foo(*args)
			assert g.next() == args
			try:
				g.next()
			except StopIteration:
				pass
			else:
				raise AssertionError("Failed to raise StopIteration at the right place")

		assert TypeVariables._TypeVariables__mapping_stack == []
		assert TypeVariables._TypeVariables__active_mapping is None
		assert len(TypeVariables._TypeVariables__gen_mappings) == 0
		
	def test_yield_fail(self):
		from typecheck import typecheck_yield
		from typecheck import TypeCheckError, _TC_IndexError, _TC_TypeError
		from typecheck import calculate_type, _TC_GeneratorError
		from typecheck import TypeVariables
		
		gen_mappings = TypeVariables._TypeVariables__gen_mappings
		
		class Bad: pass
		bad = Bad()
		
		@typecheck_yield('a', int, 'a')
		def foo(a, b, c):
			yield a, b, bad
			
		class A: pass
		a = A()
		for args in ((5, 5, 5), (5.0, 5, 7.0), ([4, 5], 5, [8, 9, 10]), (a, 5, a)):
			g = foo(*args)
			
			try:
				assert g.next() == args
			except TypeCheckError, e:
				assert isinstance(e.internal, _TC_GeneratorError)
				assert e.internal.yield_no == 1
				assert isinstance(e.internal.inner, _TC_IndexError)	
				assert e.internal.inner.index == 2
				assert isinstance(e.internal.inner.inner, _TC_TypeError)
				assert e.internal.inner.inner.right == calculate_type(args[0])
				assert e.internal.inner.inner.wrong == Bad
				
				assert len(gen_mappings) == 1
				assert convert_mapping(gen_mappings.values()[0]) == {'a': calculate_type(args[0])}
			else:
				raise AssertionError("Failed to raise TypeCheckError at the right place")

			try:
				g.next()
			except StopIteration:
				assert TypeVariables._TypeVariables__mapping_stack == []
				assert TypeVariables._TypeVariables__active_mapping is None	
				assert len(gen_mappings) == 0
			else:
				raise AssertionError("Failed to raise StopIteration at the right place")

		assert TypeVariables._TypeVariables__mapping_stack == []
		assert TypeVariables._TypeVariables__active_mapping is None
		assert len(gen_mappings) == 0
		
	def test_args_return_pass(self):
		from typecheck import typecheck_return, typecheck_args
		from typecheck import TypeVariables
		
		def run_test(dec_1, dec_2):
			@dec_1('a', 'b', int, 'a', 'b')
			@dec_2('a', 'b', int, 'a', 'b')
			def foo(a, b, c, d, e):
				return a, b, c, d, e
			
			class A: pass
			class B: pass
			a = A()
			b = B()
			for args in ((5, 5.0, 6, 7, 7.0), ('a', 4, 6, 'b', 6), (a, b, 5, a, b)):
				assert foo(*args) == args
				assert TypeVariables._TypeVariables__mapping_stack == []
				assert TypeVariables._TypeVariables__active_mapping is None
				assert len(TypeVariables._TypeVariables__gen_mappings) == 0
			
		run_test(typecheck_return, typecheck_args)
		run_test(typecheck_args, typecheck_return)
		
	def test_args_return_fail(self):
		from typecheck import typecheck_args, typecheck_return, calculate_type
		from typecheck import TypeCheckError, _TC_IndexError, _TC_TypeError
		from typecheck import TypeVariables
		
		class Bad: pass
		bad = Bad()
		
		def run_test(dec_1, dec_2):
			@dec_1
			@dec_2
			def foo(a, b, c, d, e):
				return a, b, c, bad, e
			
			class A: pass
			class B: pass
			a = A()
			b = B()
			for args in ((5, 5.0, 6, 7, 7.0), ('a', 4, 6, 'b', 6), (a, b, 5, a, b)):
				try:
					foo(*args)
				except TypeCheckError, e:
					assert isinstance(e.internal, _TC_IndexError)
					assert e.internal.index == 3
					assert isinstance(e.internal.inner, _TC_TypeError)
					assert e.internal.inner.right == calculate_type(args[0])
					assert e.internal.inner.wrong == Bad

					assert TypeVariables._TypeVariables__mapping_stack == []
					assert TypeVariables._TypeVariables__active_mapping is None
					assert len(TypeVariables._TypeVariables__gen_mappings) == 0
				else:
					raise AssertionError("Failed to raise TypeCheckError at the proper place")
		
		t_r = typecheck_return('a', 'b', int, 'a', 'b')
		t_a = typecheck_args('a', 'b', int, 'a', 'b')
			
		run_test(t_r, t_a)
		run_test(t_a, t_r)
		
	def test_args_yield_pass(self):
		from typecheck import typecheck_yield, typecheck_args
		from typecheck import TypeVariables
		
		gen_mappings = TypeVariables._TypeVariables__gen_mappings
		
		def run_test(dec_1, dec_2):
			@dec_1('a', 'b', int, 'a', 'b')
			@dec_2('a', 'b', int, 'a', 'b')
			def foo(a, b, c, d, e):
				yield a, b, c, d, e
				
			class A: pass
			class B: pass
			a = A()
			b = B()
			
			problem_set = [0]*3
			problem_set[0] = ((5, 5.0, 6, 7, 7.0), {'a': int, 'b': float})
			problem_set[1] = (('a', 4, 6, 'b', 6), {'a': str, 'b': int})
			problem_set[2] = ((a, b, 5, a, b), {'a': A, 'b': B})
			
			for args, mapping in problem_set:
				gen = foo(*args)
				assert gen.next() == args
				assert TypeVariables._TypeVariables__mapping_stack == []
				assert TypeVariables._TypeVariables__active_mapping == None
				assert len(gen_mappings) == 1
				assert convert_mapping(gen_mappings.values()[0]) == mapping
				try:
					gen.next()
				except StopIteration:
					pass
				else:
					raise AssertionError("Failed to raise StopIteration at the right time")
				assert TypeVariables._TypeVariables__mapping_stack == []
				assert TypeVariables._TypeVariables__active_mapping is None
				assert len(gen_mappings) == 0
			
		run_test(typecheck_yield, typecheck_args)
		run_test(typecheck_args, typecheck_yield)
		
		assert TypeVariables._TypeVariables__mapping_stack == []
		assert TypeVariables._TypeVariables__active_mapping is None
		assert len(TypeVariables._TypeVariables__gen_mappings) == 0

	def test_args_yield_fail(self):
		from typecheck import typecheck_yield, typecheck_args
		from typecheck import TypeCheckError, _TC_IndexError, _TC_TypeError
		from typecheck import calculate_type, _TC_GeneratorError
		from typecheck import TypeVariables
		
		gen_mappings = TypeVariables._TypeVariables__gen_mappings
		
		class Bad: pass
		bad = Bad()
		
		def run_test(dec_1, dec_2):
			@dec_1('a', 'b', int, 'a', 'b')
			@dec_2('a', 'b', int, 'a', 'b')
			def foo(a, b, c, d, e):
				yield bad, b, c, bad, e
				
			class A: pass
			class B: pass
			a = A()
			b = B()
			
			problem_set = [0]*3
			problem_set[0] = ((5, 5.0, 6, 7, 7.0), {'a': int, 'b': float})
			problem_set[1] = (('a', 4, 6, 'b', 6), {'a': str, 'b': int})
			problem_set[2] = ((a, b, 5, a, b), {'a': A, 'b': B})
			
			for args, mapping in problem_set:
				gen = foo(*args)
				
				try:
					assert gen.next() == args
				except TypeCheckError, e:
					assert isinstance(e.internal, _TC_GeneratorError)
					assert e.internal.yield_no == 1
					assert isinstance(e.internal.inner, _TC_IndexError)
					assert e.internal.inner.index == 0
					assert isinstance(e.internal.inner.inner, _TC_TypeError)
					assert e.internal.inner.inner.wrong == Bad
					assert e.internal.inner.inner.right == calculate_type(args[0])
				
					assert TypeVariables._TypeVariables__mapping_stack == []
					assert TypeVariables._TypeVariables__active_mapping == None
					assert len(gen_mappings) == 1
					assert convert_mapping(gen_mappings.values()[0]) == mapping
				try:
					gen.next()
				except StopIteration:
					assert TypeVariables._TypeVariables__mapping_stack == []
					assert TypeVariables._TypeVariables__active_mapping is None
					assert len(gen_mappings) == 0
				else:
					raise AssertionError("Failed to raise StopIteration at the right time")
				
			
		run_test(typecheck_yield, typecheck_args)
		run_test(typecheck_args, typecheck_yield)
		
		assert TypeVariables._TypeVariables__mapping_stack == []
		assert TypeVariables._TypeVariables__active_mapping is None
		assert len(TypeVariables._TypeVariables__gen_mappings) == 0
		
	def test_recursive_functions(self):
		from typecheck import typecheck_return, typecheck_args
		from typecheck import TypeVariables
		
		mapping_stack = TypeVariables._TypeVariables__mapping_stack
		
		mappings = [None, {'a': str}, {'a': (int, int)}, {'a': float}, None]
		stack = list(mappings)
		stack.reverse()
		stack.pop()
		
		def check(n):
			assert active_mapping() == mappings[n]
			assert [convert_mapping(m) for m in mapping_stack] == stack[:-n]
		
		def run_test(dec_1, dec_2):
			@dec_1
			@dec_2
			def foo(obj_1, obj_2, n):
				if n == 1:
					check(n)
					return [obj_1, obj_2]
				elif n == 2:
					check(n)
					foo('jabber', 'wocky', n-1)
					check(n)
					
					return [(4, 5), (6, 7)]
				elif n == 3:
					check(n)
					foo((5, 6), (7, 8), n-1)
					check(n)
					
					return [obj_1, obj_2]
	
			assert foo(6.0, 7.0, 3) == [6.0, 7.0]
			assert mapping_stack == []
			assert TypeVariables._TypeVariables__active_mapping == None
			assert len(TypeVariables._TypeVariables__gen_mappings) == 0
				
		t_r = typecheck_return(['a'])
		t_a = typecheck_args('a', 'a', int)
		run_test(t_r, t_a)
		run_test(t_a, t_r)
		
	def test_incorrect_generator_usage(self):
		from typecheck import typecheck_yield, typecheck_args
		from typecheck import TypeVariables
		
		gen_mappings = TypeVariables._TypeVariables__gen_mappings
		
		@typecheck_args('a')
		@typecheck_yield('a')
		def gen(obj):
			yield obj
			
		assert gen.type_yield == 'a'
		assert gen.type_args_pos == ('a',)
		assert gen.type_args_kw == {}
		assert gen.type_args_vargs == []
		assert gen.type_args_kwargs == {}
			
		for i in range(1, 4):
			g = gen(5)
			
			assert gen.type_yield == g.type_yield
			
			assert g.next() == 5
			del g
			
			assert TypeVariables._TypeVariables__mapping_stack == []
			assert TypeVariables._TypeVariables__active_mapping == None
			assert len(gen_mappings) == 0
			
	def test_args_yield_on_method_fail(self):
		from typecheck import typecheck_yield, TypeCheckError
		from typecheck import _TC_IndexError, _TC_TypeError
		from typecheck import _TC_GeneratorError, typecheck_args
		from typecheck import TypeVariables
		
		class Test(object):
			@typecheck_args('a', int, int)
			@typecheck_yield('a', int, 'a')
			def foo(self, a, b):
				yield b, a, b

		assert Test.foo.type_yield == ('a', int, 'a')
		assert Test.foo.type_args_pos == ('a', int, int)
		assert Test.foo.type_args_kw == {}
		assert Test.foo.type_args_vargs == []
		assert Test.foo.type_args_kwargs == {}
		
		def run_test():
			try:
				assert Test().foo(4, 6).next() == (6, 4, 6)
			except TypeCheckError, e:
				assert isinstance(e.internal, _TC_GeneratorError)
				assert e.internal.yield_no == 1
				assert isinstance(e.internal.inner, _TC_IndexError)
				assert e.internal.inner.index == 0
				assert isinstance(e.internal.inner.inner, _TC_TypeError)
				assert e.internal.inner.inner.wrong == int
				assert e.internal.inner.inner.right == Test
			else:
				raise AssertionError("Failed to raise TypeCheckError")

		run_test()
		assert TypeVariables._TypeVariables__mapping_stack == []
		assert TypeVariables._TypeVariables__active_mapping == None
		assert len(TypeVariables._TypeVariables__gen_mappings) == 0
		
### Bookkeeping ###
if __name__ == '__main__':
	import __main__
	support.run_all_tests(__main__)
