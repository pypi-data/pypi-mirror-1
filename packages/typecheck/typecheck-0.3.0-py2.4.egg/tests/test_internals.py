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
			
	def test_or_lists(self):
		from typecheck import _TC_TypeError, List, Or
		
		def or_type(obj):
			check_type(Or(List(int), List(float)), obj)
		
		or_type( [4,5,6] )
		or_type( [4.0, 5.0] )
		
		try:
			or_type( ["a", "b"] )
		except _TC_TypeError, e:
			assert e.wrong == [str]
			assert e.right == Or( [int], [float] )
		else:
			self.fail("Passed incorrectly")
			
	def test_lists_of_ors(self):
		from typecheck import _TC_IndexError, List, Or
		from typecheck import _TC_TypeError
		
		def or_type(obj):
			check_type(List( Or(int, float) ), obj)
		
		or_type( [4,5,6] )
		or_type( [4.0, 8, 5.0] )
		
		try:
			or_type( [8, "b"] )
		except _TC_IndexError, e:
			assert e.index == 1
			assert isinstance(e.inner, _TC_TypeError)
			assert e.inner.wrong == str
			assert e.inner.right == Or(int, float)
		else:
			self.fail("Passed incorrectly")
			
	def test_nested_ors_ands(self):
		from typecheck import _TC_TypeError, Or, And
		
		class A: pass
		class B: pass
		class C(A, B): pass
		
		and_type = And(Or(int, A), B)
		
		check_type(and_type, C())
		
		try:
			check_type(and_type, A())
		except _TC_TypeError, e:
			assert e.wrong == A
			assert e.right == And(Or(int, A), B)
		else:
			self.fail("Passed incorrectly")
			
	def test_dict_of_ors(self):
		from typecheck import _TC_KeyError, Or, Dict, _TC_TypeError
		from typecheck import _TC_DictError
		
		or_type = Or(int, float)
		def dict_type(obj):
			check_type(Dict(or_type, or_type), obj)
		
		dict_type( {4:4, 4.0:4, 4:7.0} )
		
		try:
			dict_type( {'f': 5} )
		except _TC_KeyError, e:
			assert e.key == 'f'
			assert isinstance(e.inner, _TC_TypeError)
			assert e.inner.wrong == str
			assert e.inner.right == or_type
		else:
			self.fail("Passed incorrectly")

class OrTests(TestCase):
	def setUp(self):
		from typecheck import Or
	
		def or_type(obj):
			check_type(Or(int, float), obj)
	
		self.or_type = or_type
		
	def test_success(self):
		from typecheck import Or
	
		self.or_type(5)
		self.or_type(7.0)
		
		class A: pass
		class B: pass
		class C(A, B): pass
			
		check_type(Or(A, B), C())
		check_type(Or(A), A())
		
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
			
class AndTests(TestCase):
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

class NotTests(TestCase):
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
			
class EmptyTests(TestCase):
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
			
	def test_tuple_success(self):
		from typecheck import Tuple
	
		check_type(Tuple(), tuple())
	
	def test_tuple_failure(self):
		from typecheck import Tuple, _TC_TypeError
		
		try:
			check_type(Tuple(), (5, 6))
		except _TC_TypeError, e:
			assert e.wrong == (int, int)
			assert e.right == ()
		else:
			self.fail("Passed incorrectly")
			
	def test_equality(self):
		from typecheck import Empty
		
		assert Empty(list) == Empty(list)
		assert Empty(list) != Empty(dict)
		assert Empty(dict) != Empty(list)
		assert not Empty(list) != Empty(list)
		assert not Empty(list) == Empty(dict)
			
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
