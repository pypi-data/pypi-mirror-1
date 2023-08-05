import support
from support import TODO

if __name__ == '__main__':
	support.adjust_path()
### /Bookkeeping ###

import types
import unittest

import typecheck

class Test_typecheck_return(unittest.TestCase):
	def test_success_1(self):
		from typecheck import typecheck_return
	
		@typecheck_return(int, int, int)
		def foo():
			return 5, 6, 7
		foo()
		
	def test_success_2(self):
		from typecheck import typecheck_return
		
		@typecheck_return([int])
		def foo():
			return [4,5,6]
		foo()
		
	def test_success_3(self):
		from typecheck import typecheck_return
		
		@typecheck_return([int], int, str)
		def foo():
			return [4,5,6], 5, "foo"
		foo()
		
	def test_success_4(self):
		from typecheck import typecheck_return

		@typecheck_return(int)
		def foo():
			return 7
		foo()
		
	def test_success_5(self):
		from typecheck import typecheck_return
		
		@typecheck_return( (int,) )
		def foo():
			return (7,)
		foo()
			
	def test_failure_1(self):
		from typecheck import typecheck_return, TypeCheckError, _TC_TypeError
		
		@typecheck_return(int, int, int)
		def foo():
			return 5, 6
		try:
			foo()
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_TypeError)
			assert e.internal.right == (int, int, int)
			assert e.internal.wrong == (int, int)

	def test_failure_2(self):
		from typecheck import typecheck_return, TypeCheckError, _TC_IndexTypeError

		@typecheck_return([int])
		def foo():
			return [4,5,6.0]
		try:
			foo()
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexTypeError)
			assert e.internal.index == 2
			assert e.internal.wrong == types.FloatType
			assert e.internal.right == types.IntType

	def test_failure_3(self):
		from typecheck import typecheck_return, TypeCheckError, _TC_IndexTypeError

		@typecheck_return([int], int, str)
		def foo():
			return [4,5,6], 5, ["foo"]
		try:
			foo()
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexTypeError)
			assert e.internal.index == 2
			assert e.internal.wrong == [types.StringType]
			assert e.internal.right == types.StringType

	def test_failure_4(self):
		from typecheck import typecheck_return, TypeCheckError, _TC_TypeError

		@typecheck_return( (int,) )
		def foo():
			return 7
		try:
			foo()
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_TypeError)
			assert e.internal.right == (types.IntType,)
			assert e.internal.wrong == types.IntType
			
class Test_typecheck_args(unittest.TestCase):
	def test_success_single_positional(self):
		from typecheck import typecheck_args
	
		@typecheck_args(int)
		def foo(int_1):
			return int_1

		assert foo(6) == 6

	def test_success_multiple_positional(self):
		from typecheck import typecheck_args
	
		@typecheck_args(int, int, int)
		def foo(int_1, int_2, int_3):
			return int_1, int_2, int_3

		assert foo(1, 2, 3) == (1, 2, 3)
		
	def test_success_multiple_positional_type_by_kw(self):
		from typecheck import typecheck_args
	
		@typecheck_args(int_2=int, int_1=int, int_3=int)
		def foo(int_1, int_2, int_3):
			return int_1, int_2, int_3

		assert foo(1, 2, 3) == (1, 2, 3)
		
	def test_success_multiple_keyword(self):
		from typecheck import typecheck_args
		
		@typecheck_args(kw_1=int, kw_2=int, kw_3=int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)

		assert foo() == (5, 6, 7)
		assert foo(9, 9, 9) == (9, 9, 9)
		assert foo(kw_1=33, kw_3=88) == (33, 6, 88)
		assert foo(kw_3=55, kw_2=2) == (5, 2, 55)
		
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
		
	def test_success_kwargs_form_2(self):
		from typecheck import typecheck_args

		# ...or in normal dict form
		# (in this case, full checking is done)
		@typecheck_args(kwargs={str: int})
		def foo(**kwargs):
			return kwargs 
		
		assert foo() == {}
		assert foo(int_1=5, int_2=8) == {'int_1': 5, 'int_2': 8}
		
	def test_success_vargs_form_1(self):
		from typecheck import typecheck_args

		# Type can be passed as a single type...
		@typecheck_args(vargs=int)
		def foo(*vargs):
			return vargs 
		
		assert foo() == ()
		assert foo(5, 8) == (5, 8)
		
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
		
	def test_success_pos_and_kw(self):
		from typecheck import typecheck_args
		
		@typecheck_args(int, int, foo=int)
		def foo(req_1, req_2, foo=7):
			return (req_1, req_2, foo)
		
		assert foo(5, 6, foo=88) == (5, 6, 88)
		assert foo(5, 6) == (5, 6, 7)
		assert foo(foo=5, req_2=44, req_1=99) == (99, 44, 5)
		
	def test_success_unpacked_tuples(self):
		from typecheck import typecheck_args
		
		@typecheck_args(int, (int, (int, int)), int)
		def foo(req_1, (req_2, (req_3, req_4)), req_5):
			return (req_1, req_2, req_3, req_4, req_5)
		
		assert foo(4, (5, (6, 7)), 8) == (4, 5, 6, 7, 8)

	def test_failure_single_positional(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_TypeError
	
		@typecheck_args(int)
		def foo(int_1):
			return 7

		try:
			foo(6.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_TypeError)
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_failure_multiple_positional(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_IndexTypeError
	
		@typecheck_args(int, int, int)
		def foo(int_1, int_2, int_3):
			return 7

		try:
			foo(1, 2, 3.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexTypeError)
			assert e.internal.index == 2
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_failure_multiple_positional_type_by_kw(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_IndexTypeError
	
		@typecheck_args(int_2=int, int_1=int, int_3=int)
		def foo(int_1, int_2, int_3):
			return 7

		try:
			foo(1, 2, 3.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexTypeError)
			assert e.internal.index == 2
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_failure_multiple_keyword_1(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_ValTypeError
		
		@typecheck_args(kw_1=int, kw_2=int, kw_3=int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)

		try:
			foo(9.0, 9, 9)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_ValTypeError)
			assert e.internal.key == 'kw_1'
			assert e.internal.val == 9.0
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")		

	def test_failure_multiple_keyword_2(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_ValTypeError
		
		@typecheck_args(kw_1=int, kw_2=int, kw_3=int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)
		
		try:
			foo(kw_1=9.0, kw_3=88)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_ValTypeError)
			assert e.internal.key == 'kw_1'
			assert e.internal.val == 9.0
			assert e.internal.right == int
			assert e.internal.wrong == float
			
	def test_failure_multiple_keyword_3(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_ValTypeError
		
		@typecheck_args(kw_1=int, kw_2=int, kw_3=int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)
		
		try:
			foo(kw_3=9.0, kw_1=88)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_ValTypeError)
			assert e.internal.key == 'kw_3'
			assert e.internal.val == 9.0
			assert e.internal.right == int
			assert e.internal.wrong == float

	def test_failure_multiple_keyword_type_by_pos_1(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_ValTypeError
		
		@typecheck_args(int, int, int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)

		try:
			foo(9.0, 9, 9)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_ValTypeError)
			assert e.internal.key == 'kw_1'
			assert e.internal.val == 9.0
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")		

	def test_failure_multiple_keyword_type_by_pos_2(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_ValTypeError
		
		@typecheck_args(int, int, int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)
		
		try:
			foo(kw_1=9.0, kw_3=88)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_ValTypeError)
			assert e.internal.key == 'kw_1'
			assert e.internal.val == 9.0
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")	
			
	def test_failure_multiple_keyword_type_by_pos_3(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_ValTypeError
		
		@typecheck_args(int, int, kw_3=int)
		def foo(kw_1=5, kw_2=6, kw_3=7):
			return (kw_1, kw_2, kw_3)
		
		try:
			foo(kw_3=9.0, kw_1=88)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_ValTypeError)
			assert e.internal.key == 'kw_3'
			assert e.internal.val == 9.0
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_failure_kwargs_form_1(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_ValTypeError

		# Type can be passed as a single type...
		# (in this case, the values of the dict
		# will be checked against the given type)
		@typecheck_args(kwargs=int)
		def foo(**kwargs):
			return kwargs 
		
		try:
			foo(int_1=5.0, int_2=8)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_ValTypeError)
			assert e.internal.key == 'int_1'
			assert e.internal.val == 5.0
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_failure_kwargs_form_2(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_ValTypeError

		# ...or in normal dict form
		# (in this case, full checking is done)
		@typecheck_args(kwargs={str: int})
		def foo(**kwargs):
			return kwargs 
		
		try:
			foo(int_1=5.0, int_2=99)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_ValTypeError)
			assert e.internal.key == 'int_1'
			assert e.internal.val == 5.0
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_failure_vargs_form_1(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_IndexTypeError

		# Type can be passed as a single type...
		@typecheck_args(vargs=int)
		def foo(*vargs):
			return vargs 
		
		try:
			foo(5, 8.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexTypeError)
			assert e.internal.index == 1
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_failure_vargs_form_2(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_IndexTypeError

		# ...or as an actual tuple. Note that
		# this form is useful if you want to
		# specify patterned tuples
		@typecheck_args(vargs=[int])
		def foo(*vargs):
			return vargs 
		
		try:
			foo(5, 8.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexTypeError)
			assert e.internal.index == 1
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_failure_pos_and_kw_1(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_IndexTypeError
		
		@typecheck_args(int, int, foo=int)
		def foo(req_1, req_2, foo=7):
			return (req_1, req_2, foo)
		
		try:
			foo(5, 6.0, foo=88)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexTypeError)
			assert e.internal.index == 1
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_failure_pos_and_kw_2(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_ValTypeError
		
		@typecheck_args(int, int, foo=int)
		def foo(req_1, req_2, foo=7):
			return (req_1, req_2, foo)
		
		try:
			foo(5, 6, foo=88.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_ValTypeError)
			assert e.internal.key == 'foo'
			assert e.internal.val == 88.0
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")	
		
	def test_failure_pos_and_kw_3(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_IndexTypeError
		
		@typecheck_args(int, int, foo=int)
		def foo(req_1, req_2, foo=7):
			return (req_1, req_2, foo)
		
		try:
			foo(foo=5, req_2=44, req_1=99.0)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexTypeError)
			assert e.internal.index == 0
			assert e.internal.right == int
			assert e.internal.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_failure_unpacked_tuples_1(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_IndexTypeError, _TC_TypeError
		
		@typecheck_args(int, (int, (int, int)), int)
		def foo(a, (b, (c, d)), e):
			return a, b, c, d, e
		try:
			foo(5, (6, (7, 8.0)), 9)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexTypeError)
			assert e.internal.index == 1
			assert e.internal.right == (int, (int, int))
			assert e.internal.wrong == (int, (int, float))
			assert isinstance(e.internal.inner, _TC_IndexTypeError)
			assert e.internal.inner.index == 1
			assert e.internal.inner.right == (int, int)
			assert e.internal.inner.wrong == (int, float)
			assert isinstance(e.internal.inner.inner, _TC_IndexTypeError)
			assert e.internal.inner.inner.index == 1
			assert e.internal.inner.inner.right == int
			assert e.internal.inner.inner.wrong == float
			assert isinstance(e.internal.inner.inner.inner, _TC_TypeError)
			assert e.internal.inner.inner.inner.right == int
			assert e.internal.inner.inner.inner.wrong == float
		else:
			raise AssertionError("Succeeded incorrectly")	
			
	def test_failure_unpacked_tuples_2(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_IndexTypeError
		
		@typecheck_args(int, (int, (int, int)), int)
		def foo(a, (b, (c, d)), e):
			return a, b, c, d, e
		try:
			foo(5, (6, 4), 9)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexTypeError)
			assert e.internal.index == 1
			#raise TypeError(str(e.internal.wrong))
			assert e.internal.right == (int, (int, int))
			assert e.internal.wrong == (int, int)
			assert isinstance(e.internal.inner, _TC_IndexTypeError)
			assert e.internal.inner.index == 1
			assert e.internal.inner.right == (int, int)
			assert e.internal.inner.wrong == int
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_failure_unpacked_tuples_3(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_IndexTypeError
		
		@typecheck_args(int, (int, (int, int)), int)
		def foo(a, (b, (c, d)), e):
			return a, b, c, d, e
		try:
			foo(5, (6, (7, 8)), (9, 10))
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexTypeError)
			assert e.internal.index == 2
			assert e.internal.right == int
			assert e.internal.wrong == (int, int)
		else:
			raise AssertionError("Succeeded incorrectly")	

	def test_empty_vargs_and_kwargs_implicit_success(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_IndexTypeError

		@typecheck_args(int, int, int)
		def foo(a, b, c):
			return a, b, c
			
		assert foo(2, 3, 4) == (2, 3, 4)
		
	def test_empty_vargs_explicit_success(self):
		from typecheck import typecheck_args, Empty

		@typecheck_args(int, int, int, Empty(list))
		def foo(a, b, c, *vargs):
			return a, b, c, vargs
			
		assert foo(2, 3, 4) == (2, 3, 4, ())		

	def test_empty_vargs_implicit_failure(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_LengthError

		@typecheck_args(int, int, int)
		def foo(a, b, c):
			return a, b, c
		
		try:
			foo(2, 3, 4, 5)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_LengthError)
			assert e.internal.right == 0
			assert e.internal.wrong == 1
		else:
			raise AssertionError("Succeeded incorrectly")
		
	def test_empty_vargs_explicit_failure(self):
		from typecheck import typecheck_args, Empty, TypeCheckError, _TC_LengthError

		@typecheck_args(int, int, int, Empty(list))
		def foo(a, b, c, *vargs):
			return a, b, c
		
		try:
			foo(2, 3, 4, 5, 6)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_LengthError)
			assert e.internal.right == 0
			assert e.internal.wrong == 2
		else:
			raise AssertionError("Succeeded incorrectly")
		
	def test_empty_kwargs_explicit_success(self):
		from typecheck import typecheck_args, Empty

		@typecheck_args(int, int, int, Empty(dict))
		def foo(a, b, c, **kwargs):
			return a, b, c, kwargs
			
		assert foo(2, 3, 4) == (2, 3, 4, {})		

	def test_empty_kwargs_implicit_failure(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_LengthError

		@typecheck_args(int, int, int)
		def foo(a, b, c):
			return a, b, c
		
		try:
			foo(2, 3, 4, d=5, e=6)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_LengthError)
			assert e.internal.right == 0
			assert e.internal.wrong == 2
		else:
			raise AssertionError("Succeeded incorrectly")
		
	def test_empty_kwargs_explicit_failure(self):
		from typecheck import typecheck_args, Empty, TypeCheckError, _TC_LengthError

		@typecheck_args(int, int, int, Empty(dict))
		def foo(a, b, c, **kwargs):
			return a, b, c, kwargs
		
		try:
			foo(2, 3, 4, r=5, t=6)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_LengthError)
			assert e.internal.right == 0
			assert e.internal.wrong == 2
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_bad_signature_missing_pos(self):
		from typecheck import typecheck_args, TypeSignatureError
		
		try:
			@typecheck_args(int, int, int)
			def foo(a, b, c, e):
				return a, b, c, e
		except TypeSignatureError:
			pass
		else:
			raise AssertionError("Succeeded incorrectly")	


	def test_bad_signature_missing_kw(self):
		from typecheck import typecheck_args, TypeSignatureError
		
		try:
			@typecheck_args(a=int, b=int, c=int)
			def foo(a=5, b=6, c=7, d=8):
				return a, b, c, d
		except TypeSignatureError:
			pass
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_bad_signature_extra_pos(self):
		from typecheck import typecheck_args, TypeSignatureError
		
		try:
			@typecheck_args(int, int, int, int)
			def foo(a, b, c):
				return a, b, c
		except TypeSignatureError:
			pass
		else:
			raise AssertionError("Succeeded incorrectly")

	def test_bad_signature_extra_kw(self):
		from typecheck import typecheck_args, TypeSignatureError
		
		try:
			@typecheck_args(a=int, b=int, c=int)
			def foo(a=5, b=6):
				return a, b
		except TypeSignatureError:
			pass
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_bad_signature_unpack_nonsequence(self):
		from typecheck import typecheck_args, TypeSignatureError
		
		try:
			@typecheck_args(int, int)
			def foo(a, (b, c)):
				return a, b, c
		except TypeSignatureError:
			pass
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_bad_signature_unpack_bad_sequence_1(self):
		from typecheck import typecheck_args, TypeSignatureError
		
		try:
			@typecheck_args(int, (int, int, int))
			def foo(a, (b, c)):
				return a, b, c
		except TypeSignatureError:
			pass
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_bad_signature_unpack_bad_sequence_2(self):
		from typecheck import typecheck_args, TypeSignatureError
		
		try:
			@typecheck_args(int, (int, int))
			def foo(a, (b, c, d)):
				return a, b, c, d
		except TypeSignatureError:
			pass
		else:
			raise AssertionError("Succeeded incorrectly")

class Test_Self_class(unittest.TestCase):
	def test_self_in_args_pass(self):
		from typecheck import typecheck_args, Self
		
		class Test(object):
			@typecheck_args(Self, int, Self)
			def foo(self, a, b):
				return a, b
		
		t = Test()
		assert Test().foo(4, t) == (4, t)	
	
	@TODO("Waiting on some way of detecting method-hood in decorators")
	def test_self_in_args_fail_1(self):
		from typecheck import typecheck_args, Self, TypeCheckError
		from typecheck import _TC_IndexTypeError
		
		class Test(object):
			@typecheck_args(Self, int, Self)
			def foo(self, a, b):
				return a, b
		
		try:
			assert Test().foo(4, 6) == (4, 6)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexTypeError)
			assert e.internal.index == 2
			assert e.internal.wrong == int
			assert e.internal.right == Test
		else:
			raise AssertionError("Succeeded incorrectly")
			
	@TODO("Waiting on some way of detecting method-hood in decorators")
	def test_self_in_args_fail_2(self):
		from typecheck import typecheck_args, Self, TypeSignatureError
		
		try:
			@typecheck_args(Self, int)
			def foo(self, a, b):
				return a, b
		except TypeSignatureError:
			pass
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_self_in_return_pass(self):
		from typecheck import typecheck_return, Self
		
		class Test(object):
			@typecheck_return(Self, int, Self)
			def foo(self, a, b):
				return self, a, b
		
		t = Test()
		t_1 = Test()
		assert t_1.foo(4, t) == (t_1, 4, t)	
	
	@TODO("Waiting on some way of detecting method-hood in decorators")
	def test_self_in_return_fail_1(self):
		from typecheck import typecheck_return, Self, TypeCheckError
		from typecheck import _TC_IndexTypeError
		
		class Test(object):
			@typecheck_return(Self, int, Self)
			def foo(self, a, b):
				return self, a, b
		
		try:
			t = Test()
			assert t.foo(4, 6) == (t, 4, 6)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexTypeError)
			assert e.internal.index == 2
			assert e.internal.wrong == int
			assert e.internal.right == Test
		else:
			raise AssertionError("Succeeded incorrectly")
			
	@TODO("Waiting on some way of detecting method-hood in decorators")
	def test_self_in_return_fail_2(self):
		from typecheck import typecheck_return, Self, TypeSignatureError
		
		try:
			@typecheck_return(Self, int)
			def foo(self, a, b):
				return a, b
		except TypeSignatureError:
			pass
		else:
			raise AssertionError("Succeeded incorrectly")	

### Bookkeeping ###
if __name__ == '__main__':
	support.run_all_tests(globals())
