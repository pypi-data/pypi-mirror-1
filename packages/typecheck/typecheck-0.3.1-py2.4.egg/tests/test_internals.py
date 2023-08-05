import support
from support import TODO, TestCase

if __name__ == '__main__':
	support.adjust_path()
### /Bookkeeping ###

import unittest

import typecheck

def check_type(typ, obj):
	typecheck.check_type(typ, None, obj)

class SingleTests(TestCase):
	def test_success_builtin_types(self):
		from typecheck import Single
		
		check_type(Single(int), 7)
		check_type(Single(float), 7.0)

	def test_success_userdef_classes_oldstyle(self):
		from typecheck import Single
			
		class A: pass
		class B(A): pass
		
		check_type(Single(A), A())
		check_type(Single(A), B())
		check_type(Single(B) ,B())
		
	def test_success_userdef_classes_newstyle(self):
		from typecheck import Single
			
		class A(object): pass
		class B(A): pass
		
		check_type(Single(A), A())
		check_type(Single(A), B())
		check_type(Single(B), B())
		
	def test_failure(self):
		from typecheck import Single, _TC_TypeError
		
		try:
			check_type(Single(int), 7.0)
		except _TC_TypeError, e:
			assert e.right == int
			assert e.wrong == float
		else:
			raise AssertionError("Failed to raise the proper exception")
			
	def test_equality(self):
		from typecheck import Single
		
		int_1 = Single(int)
		int_2 = Single(int)
		flt_1 = Single(float)
		flt_2 = Single(float)
		
		assert int_1 == int_2
		assert not int_1 != int_2
		assert int_1 != flt_1
		assert not int_1 == flt_1

class DictTests(TestCase):
	def setUp(self):
		from typecheck import Dict
	
		def dic(obj):
			check_type(Dict(key=str, val=int), obj)
	
		self.dict = dic

	def test_success(self):
		self.dict({})
		self.dict({ 'a': 1, 'b': 2 })

	def test_key_failure(self):
		from typecheck import _TC_KeyError, _TC_TypeError
	
		try:
			self.dict({1.0: 1, 'b': 2})
		except _TC_KeyError, e:
			assert e.key == 1.0
			assert isinstance(e.inner, _TC_TypeError)
			assert e.inner.wrong == float
			assert e.inner.right == str
		else:
			self.fail("Passed incorrectly")
		
	def test_val_failure(self):
		from typecheck import _TC_KeyValError, _TC_TypeError
	
		try:
			# 1.0 is not an integer
			self.dict({'a': 1.0, 'b': 2})
		except _TC_KeyValError, e:
			assert e.key == 'a'
			assert e.val == 1.0
			assert isinstance(e.inner, _TC_TypeError)
			assert e.inner.wrong == float
			assert e.inner.right == int
		else:
			self.fail("Passed incorrectly")
			
	def test_type_failure(self):
		from typecheck import _TC_TypeError
	
		try:
			self.dict( 5.0 )
		except _TC_TypeError, e:
			assert e.wrong is float
			assert e.right == { str: int }
		else:
			self.fail("Passed incorrectly")
			
	def test_eq_ne_operators(self):
		from typecheck import Dict, Tuple, List
		
		dict1 = Dict(str, int)
		dict2 = Dict(int, int)
		dict3 = Dict(str, int)
		tup1 = Tuple(str, int)
		list1 = List(str, int)

		assert dict1 == dict3
		assert dict1 != dict2
		assert dict1 != tup1
		assert tup1 != dict1
		assert dict1 != list1
		assert list1 != dict1
		assert dict2 != tup1
		assert dict2 != list1
		assert tup1 != dict2
		assert list1 != dict2
			
class TupleTests(TestCase):
	def setUp(self):
		from typecheck import Tuple
	
		def tup(obj):
			check_type(Tuple(int, float, int), obj)
	
		self.tuple = tup

	def test_success(self):
		self.tuple( (4, 5.0, 4) )

	def test_type_failure(self):
		from typecheck import _TC_TypeError
	
		try:
			self.tuple( [4, 5, 6] )
		except _TC_TypeError, e:
			assert e.right == (int, float, int)
			assert e.wrong == [int]
		else:
			self.fail("Passed incorrectly")
			
	def test_index_failure(self):
		from typecheck import _TC_IndexError, _TC_TypeError
		
		try:
			self.tuple( (5, 'a', 4) )
		except _TC_IndexError, e:
			assert e.index == 1
			assert isinstance(e.inner, _TC_TypeError)
			assert e.inner.wrong == str
			assert e.inner.right == float
		else:
			self.fail("Passed incorrectly")
			
	def test_length_error(self):
		from typecheck import _TC_TypeError
		
		try:
			self.tuple( (3, 4) )
		except _TC_TypeError, e:
			assert e.wrong == (int, int)
			assert e.right == (int, float, int)
		else:
			self.fail("Passed incorrectly")
			
	def test_eq_ne_operators(self):
		from typecheck import List, Tuple
	
		tup1 = Tuple(int, float, int)
		tup2 = Tuple(float, int, float)
		tup3 = Tuple(int, float, int)
		tup4 = Tuple(float)
		list1 = List(int, float, int)
		
		assert tup1 != tup2
		assert tup1 == tup3
		assert tup1 != tup4
		assert tup1 != list1
		assert tup2 != tup3
		assert tup2 != tup4
		assert list1 != tup1
		
	def test_empty_tuple_success(self):
		from typecheck import Tuple
	
		check_type(Tuple(), tuple())
	
	def test_empty_tuple_failure(self):
		from typecheck import Tuple, _TC_TypeError
		
		try:
			check_type(Tuple(), (5, 6))
		except _TC_TypeError, e:
			assert e.wrong == (int, int)
			assert e.right == ()
		else:
			self.fail("Passed incorrectly")
	
class SingleType_ListTests(TestCase):
	def setUp(self):
		from typecheck import List
	
		def lis(obj):
			check_type(List(int), obj)
	
		self.list = lis

	def test_success(self):
		self.list([])
		self.list([ 4, 5, 6, 7 ])

	def test_index_failure(self):
		from typecheck import _TC_IndexError, _TC_TypeError
	
		try:
			self.list( [4,5,6,7.0] )
		except _TC_IndexError, e:
			assert e.index == 3
			assert isinstance(e.inner, _TC_TypeError)
			assert e.inner.right == int
			assert e.inner.wrong == float
		else:
			self.fail("Passed incorrectly")
			
	def test_type_failure(self):
		from typecheck import _TC_TypeError
		
		try:
			self.list( { 'f': 4 } )
		except _TC_TypeError, e:
			assert e.right == [int]
			assert e.wrong == {str: int}
		else:
			self.fail("Passed incorrectly")
			
	def test_eq_ne_operators(self):
		from typecheck import List, Tuple
	
		list1 = List(int)
		list2 = List(float)
		list3 = List(int)
		tup1 = Tuple(int)
		
		assert list1 == list3
		assert list2 != list3
		assert list1 != list2
		assert list1 != tup1
		assert tup1 != list1
			
class Pattern_ListTests(TestCase):
	def setUp(self):
		from typecheck import List
	
		def lis(obj):
			check_type(List(int, float), obj)

		self.list = lis

	def test_success(self):
		self.list([])
		self.list([ 4, 5.0 ])
		self.list([ 4, 5.0, 8, 9.0 ])
		self.list([ 4, 5.0, 9, 8.0, 4, 5.0 ])

	def test_index_failure(self):
		from typecheck import _TC_IndexError, _TC_TypeError
	
		try:
			# 5 is not a float
			self.list( [4,5,6,7.0] )
		except _TC_IndexError, e:
			assert e.index == 1
			assert isinstance(e.inner, _TC_TypeError)
			assert e.inner.wrong == int
			assert e.inner.right == float
		else:
			self.fail("Passed incorrectly")
			
	def test_type_failure(self):
		from typecheck import _TC_TypeError
		
		try:
			self.list( { 'f': 4 } )
		except _TC_TypeError, e:
			assert e.right == [int, float]
			assert e.wrong == {str: int}
		else:
			self.fail("Passed incorrectly")
			
	def test_length_failure(self):
		from typecheck import _TC_LengthError
	
		try:
			self.list( [4,5.0,6,7.0, 6] )
		except _TC_LengthError, e:
			assert e.wrong == 5
		else:
			self.fail("Passed incorrectly")
			
	def test_eq_ne_operators(self):
		from typecheck import List, Tuple
	
		list1 = List(int, float)
		list2 = List(float, int)
		list3 = List(int)
		list4 = List(int, float)
		tup1 = Tuple(int, float)
		
		assert list1 != list2
		assert list1 != list3
		assert list1 == list4
		assert list2 != list3
		assert list2 != list4
		assert list1 != tup1
		assert tup1 != list1
			
class NestedTests(TestCase):
	def test_patterned_lists_in_lists(self):
		from typecheck import _TC_IndexError, List, _TC_TypeError
	
		def list1(obj):
			check_type(List( [int, str] ), obj)
		
		# This should pass (list of lists)
		list1( [[4,"foo"], [6,"foo",7,"bar"]] )
		
		try:
			# 6 is not list of alternating integers and strings
			list1( [[4,"foo"], 6] )
		except _TC_IndexError, e:
			assert e.index == 1
			assert isinstance(e.inner, _TC_TypeError)
			assert e.inner.right == [int, str]
			assert e.inner.wrong == int
		else:
			self.fail("Passed incorrectly")

	def test_patterned_lists_of_patterned_lists(self):
		from typecheck import _TC_IndexError, List, Or, _TC_TypeError
		
		# [[[i, s]]] (list of lists of lists of alternating ints and strs)
		def list2(obj):
			check_type(List( [[int, str]] ), obj)
		
		list2( [ [[4,"foo"], [5,"bar"]], [[4,"baz",7,"foo"]] ] )
		
		try:
			# The error is in [4,[6]]; the [6] isn't a string
			list2( [[[6,"a"], [7,"r",8,"q"], [4,[6]], [6,"aaa"]]] )
		except _TC_IndexError, e:
			assert e.index == 0
			assert isinstance(e.inner, _TC_IndexError)
			assert e.inner.index == 2
			assert isinstance(e.inner.inner, _TC_IndexError)
			assert e.inner.inner.index == 1
			assert isinstance(e.inner.inner.inner, _TC_TypeError)
			assert e.inner.inner.inner.right == str
			assert e.inner.inner.inner.wrong == [int]
		else:
			self.fail("Passed incorrectly")

	def test_nested_monotype_lists(self):
		from typecheck import _TC_IndexError, List, _TC_TypeError
	
		def list1(obj):
			check_type(List( [int] ), obj)
		
		# This should pass (list of lists)
		list1( [[4,5], [6,7,8]] )
		try:
			# This should raise an exception
			list1( [[4,5], 6] )
		except _TC_IndexError, e:
			assert e.index == 1
			assert isinstance(e.inner, _TC_TypeError)
			assert e.inner.wrong == int
			assert e.inner.right == [int]
		else:
			self.fail("Passed incorrectly")
			
	def test_doubly_nested_monotype_lists(self):
		from typecheck import _TC_IndexError, List, Or
		from typecheck import _TC_TypeError
		
		# [[[i]]] (list of lists of lists of integers)
		def list2(obj):
			check_type(List( [[int]] ), obj)
		
		list2( [[[4,5], [5,6]], [[4]]] )
		try:
			# The error is in [4,[6]]; the [6] isn't an integer
			list2( [[[6], [7], [4,[6]], [6]]] )
		except _TC_IndexError, e:
			assert e.index == 0
			assert isinstance(e.inner, _TC_IndexError)
			assert e.inner.index == 2
			assert isinstance(e.inner.inner, _TC_IndexError)
			assert e.inner.inner.index == 1
			assert isinstance(e.inner.inner.inner, _TC_TypeError)
			assert e.inner.inner.inner.right == int
			assert e.inner.inner.inner.wrong == [int]
		else:
			self.fail("Passed incorrectly")
			
	def test_lists_of_tuples(self):
		from typecheck import _TC_IndexError, List, _TC_TypeError
		
		# lists of 2-tuples of integer x float
		def list3(obj):
			check_type(List( (int, float) ), obj)
		
		list3( [(1, 2.0), (2, 3.0), (3, 4.0)] )
		try:
			# The types are flipped
			list3( [(2.0, 1), (3.0, 4)] )
		except _TC_IndexError, e:
			assert e.index == 0
			assert isinstance(e.inner, _TC_IndexError)
			assert e.index == 0
			assert isinstance(e.inner.inner, _TC_TypeError)
			assert e.inner.inner.right == int
			assert e.inner.inner.wrong == float
		else:
			self.fail("Passed incorrectly")
			
	def test_singly_nested_tuples(self):
		from typecheck import _TC_IndexError, Tuple, _TC_TypeError
	
		def tup1(obj):
			check_type(Tuple( (int, int), int ), obj)
		
		# This should pass
		tup1( ((4,5), 6) )
		
		try:
			# This should raise an exception
			tup1( ([4,5], 6) )
		except _TC_IndexError, e:
			assert e.index == 0
			assert isinstance(e.inner, _TC_TypeError)
			assert e.inner.right == (int, int)
			assert e.inner.wrong == [int]
		else:
			self.fail("Passed incorrectly")
			
	def test_doubly_nested_tuples(self):
		from typecheck import _TC_IndexError, Tuple, _TC_TypeError
		
		# (((i, i), i), i)
		# Triply-nested 2-tuples of integers
		tup1 = Tuple( (int, int), int )
		def tup2(obj):
			check_type(Tuple(tup1, int), obj)
		
		tup2( (((4, 5), 6), 7) )
		
		try:
			# [4,5] is not a 2-tuple of int x int
			tup2( (([4,5], 6), 7) )
		except _TC_IndexError, e:
			assert e.index == 0
			assert isinstance(e.inner, _TC_IndexError)
			assert e.inner.index == 0
			assert isinstance(e.inner.inner, _TC_TypeError)
			assert e.inner.inner.right == (int, int)
			assert e.inner.inner.wrong == [int]
		else:
			self.fail("Passed incorrectly")
			
	def test_tuples_of_lists(self):
		from typecheck import _TC_IndexError, Tuple, _TC_TypeError
		
		# 2-tuples of list of integers x list of strs
		def tup3(obj):
			check_type(Tuple( [int], [str] ), obj)
		
		# Should pass
		tup3( ([4,5,6], ["a","b","c"]) )
		
		try:
			tup3( (["a","b","c"], [4,5,6]) )
		except _TC_IndexError, e:
			assert e.index == 0
			assert isinstance(e.inner, _TC_IndexError)
			assert e.index == 0
			assert isinstance(e.inner.inner, _TC_TypeError)
			assert e.inner.inner.right == int
			assert e.inner.inner.wrong == str
		else:
			self.fail("Passed incorrectly")
			
	def test_nested_dict_as_val(self):
		from typecheck import _TC_KeyError, _TC_KeyValError, Dict, _TC_TypeError
	
		# int -> {int -> float}
		def dict1(obj):
			check_type(Dict( int, {int: float}), obj)
		
		# Should pass
		dict1( {6: {6: 7.0, 8: 9.0}} )
		
		try:
			# Should fail (7.0 is not an integer)
			dict1( {6: {7.0: 8.0}} )
		except _TC_KeyValError, e:
			assert e.key == 6
			assert e.val == {7.0: 8.0}
			assert isinstance(e.inner, _TC_KeyError)
			assert e.inner.key == 7.0
			assert isinstance(e.inner.inner, _TC_TypeError)
			assert e.inner.inner.right == int
			assert e.inner.inner.wrong == float
		else:
			self.fail("Passed incorrectly")

	def test_nested_tuple_as_key(self):
		from typecheck import _TC_KeyError, _TC_IndexError, Dict
		from typecheck import _TC_TypeError
		
		# (int, int) -> float
		def dict2(obj):
			check_type(Dict( (int, int), float ), obj)
		
		dict2( {(4,5): 5.0, (9,9): 9.0} )
		
		try:
			# Should fail; 5.0 in (5.0, 5) is not an integer
			dict2( {(5.0, 5): 5.0} )
		except _TC_KeyError, e:
			assert e.key == (5.0, 5)
			assert isinstance(e.inner, _TC_IndexError)
			assert e.inner.index == 0
			assert isinstance(e.inner.inner, _TC_TypeError)
			assert e.inner.inner.right == int
			assert e.inner.inner.wrong == float
		else:
			self.fail("Passed incorrectly")
			
class ExtensibleSigTests(TestCase):
	def setUp(self):
		from typecheck import register_type, _TC_TypeError, unregister_type
		import types

		class ExactValue(object):
			def __init__(self, value):
				self.type = value
		
			def __typecheck__(self, func, to_check):
				if to_check != self.type:
					raise _TC_TypeError(to_check, self.type)
				
			@classmethod
			def __typesig__(cls, obj):
				# Note that you can either include this test
				# or your classes (like ExactValue) can inherit
				# from CheckType; either works, but you have
				# to do one or the other.
				if isinstance(obj, cls):
					return obj
				if isinstance(obj, int):
					return cls(obj)
		
		self.ExactValue = ExactValue
		register_type(ExactValue)
		
	def tearDown(self):
		from typecheck import unregister_type, is_registered_type
	
		if is_registered_type(self.ExactValue):
			unregister_type(self.ExactValue)

	def test_register(self):
		from typecheck import typecheck_args, TypeCheckError, _TC_IndexError, _TC_TypeError

		@typecheck_args(5, 6)
		def foo(a, b):
			return a, b

		assert foo(5, 6) == (5, 6)

		try:
			foo('a', 5)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.wrong == str
			assert e.internal.inner.right == 5
		else:
			raise AssertionError("Succeeded incorrectly")
	
	def test_double_register(self):
		from typecheck import register_type
		
		register_type(self.ExactValue)
		
	def test_unregister_def(self):
		from typecheck import register_type, typecheck_args
		from typecheck import unregister_type

		@typecheck_args(5, 6)
		def foo(a, b):
			return a, b

		assert foo(5, 6) == (5, 6)

		unregister_type(self.ExactValue)

		try:
			@typecheck_args(5, 6)
			def foo(a, b):
				return a, b
		except AssertionError:
			pass
		else:
			raise AssertionError("Succeeded incorrectly")
			
	def test_unregister_call_again(self):
		from typecheck import typecheck_args, unregister_type, TypeCheckError, _TC_IndexError
		from typecheck import _TC_TypeError
		
		@typecheck_args(5, 6)
		def foo(a, b):
			return a, b
			
		assert foo(5, 6) == (5, 6)
		
		unregister_type(self.ExactValue)
		
		try:
			foo('a', 5)
		except TypeCheckError, e:
			assert isinstance(e.internal, _TC_IndexError)
			assert e.internal.index == 0
			assert isinstance(e.internal.inner, _TC_TypeError)
			assert e.internal.inner.wrong == str
			assert e.internal.inner.right == 5
		else:
			raise AssertionError("Succeeded incorrectly")
			
### Bookkeeping ###
if __name__ == '__main__':
	import __main__
	support.run_all_tests(__main__)
