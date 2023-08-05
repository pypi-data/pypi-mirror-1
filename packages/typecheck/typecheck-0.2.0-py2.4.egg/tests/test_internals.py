import support

if __name__ == '__main__':
	support.adjust_path()
### /Bookkeeping ###

import unittest

import typecheck

class DictTests(unittest.TestCase):
	def setUp(self):
		from typecheck import Dict
	
		self.dict = Dict(key=str, val=int)

	def test_success(self):
		self.failUnless( self.dict({ 'a': 1, 'b': 2 }) )

	def test_key_failure(self):
		from typecheck import _TC_KeyTypeError
	
		try:
			self.dict({1.0: 1, 'b': 2})
		except _TC_KeyTypeError, e:
			assert e.wrong is float
			assert e.right is str
			assert e.key == 1.0
		else:
			self.fail("Passed incorrectly")
		
	def test_val_failure(self):
		from typecheck import _TC_ValTypeError
	
		try:
			# 1.0 is not an integer
			self.dict({'a': 1.0, 'b': 2})
		except _TC_ValTypeError, e:
			assert e.wrong is float
			assert e.right is int
			assert e.key == 'a'
			assert e.val == 1.0
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
		
		dict1 = self.dict
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
			
class TupleTests(unittest.TestCase):
	def setUp(self):
		from typecheck import Tuple
	
		self.tuple = Tuple( int, float, int )

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
		from typecheck import _TC_IndexTypeError
		
		try:
			self.tuple( (5, 'a', 4) )
		except _TC_IndexTypeError, e:
			assert e.wrong is str
			assert e.right is float
			assert e.index == 1
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
	
		tup1 = self.tuple
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
	
class SingleType_ListTests(unittest.TestCase):
	def setUp(self):
		from typecheck import List
	
		self.list = List(int)

	def test_success(self):
		self.failUnless( self.list([ 4, 5, 6, 7 ]) )

	def test_index_failure(self):
		from typecheck import _TC_IndexTypeError
	
		try:
			self.list( [4,5,6,7.0] )
		except _TC_IndexTypeError, e:
			assert e.right is int
			assert e.wrong is float
			assert e.index == 3
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
	
		list1 = self.list
		list2 = List(float)
		list3 = List(int)
		tup1 = Tuple(int)
		
		assert list1 == list3
		assert list2 != list3
		assert list1 != list2
		assert list1 != tup1
		assert tup1 != list1
			
class Pattern_ListTests(unittest.TestCase):
	def setUp(self):
		from typecheck import List
	
		self.list = List(int, float)

	def test_success(self):
		assert self.list([ 4, 5.0 ])
		assert self.list([ 4, 5.0, 8, 9.0 ])
		assert self.list([ 4, 5.0, 9, 8.0, 4, 5.0 ])

	def test_index_failure(self):
		from typecheck import _TC_IndexTypeError
	
		try:
			# 5 is not a float
			self.list( [4,5,6,7.0] )
		except _TC_IndexTypeError, e:
			assert e.wrong is int
			assert e.right is float
			assert e.index == 1
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
	
		list1 = self.list
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
			
class NestedTests(unittest.TestCase):
	def test_patterned_lists_in_lists(self):
		from typecheck import _TC_IndexTypeError, List
	
		list1 = List( [int, str] )
		
		# This should pass (list of lists)
		list1( [[4,"foo"], [6,"foo",7,"bar"]] )
		
		try:
			# 6 is not list of alternating integers and strings
			list1( [[4,"foo"], 6] )
		except _TC_IndexTypeError, e:
			assert e.right == [int, str]
			assert e.wrong is int
			assert e.index == 1
		else:
			self.fail("Passed incorrectly")

	def test_patterned_lists_of_patterned_lists(self):
		from typecheck import _TC_IndexTypeError, List, Or
		
		# [[[i, s]]] (list of lists of lists of alternating ints and strs)
		list2 = List( [[int, str]] )
		
		list2( [ [[4,"foo"], [5,"bar"]], [[4,"baz",7,"foo"]] ] )
		
		try:
			# The error is in [4,[6]]; the [6] isn't a string
			list2( [[[6,"a"], [7,"r",8,"q"], [4,[6]], [6,"aaa"]]] )
		except _TC_IndexTypeError, e:
			assert e.right == [[int, str]]
			list_int_str = [int, str]
			assert e.wrong == [list_int_str, list_int_str, [int, [int]], list_int_str]
			assert e.index == 0
			assert isinstance(e.inner, _TC_IndexTypeError)
			assert e.inner.index == 2
			assert e.inner.right == [int, str]
			assert e.inner.wrong == [int, [int]]
			assert isinstance(e.inner.inner, _TC_IndexTypeError)
			assert e.inner.inner.index == 1
			assert e.inner.inner.right is str
			assert e.inner.inner.wrong == [int]
		else:
			self.fail("Passed incorrectly")

	def test_nested_monotype_lists(self):
		from typecheck import _TC_IndexTypeError, List
	
		list1 = List( [int] )
		
		# This should pass (list of lists)
		list1( [[4,5], [6,7,8]] )
		try:
			# This should raise an exception
			list1( [[4,5], 6] )
		except _TC_IndexTypeError, e:
			assert e.wrong is int
			assert e.right == [int]
			assert e.index == 1
		else:
			self.fail("Passed incorrectly")
			
	def test_doubly_nested_monotype_lists(self):
		from typecheck import _TC_IndexTypeError, List, Or
		
		# [[[i]]] (list of lists of lists of integers)
		list2 = List( [[int]] )
		
		list2( [[[4,5], [5,6]], [[4]]] )
		try:
			# The error is in [4,[6]]; the [6] isn't an integer
			list2( [[[6], [7], [4,[6]], [6]]] )
		except _TC_IndexTypeError, e:
			assert e.right == [[int]]
			assert e.wrong == [[int], [int], [int,[int]], [int]]
			assert e.index == 0
			assert isinstance(e.inner, _TC_IndexTypeError)
			assert e.inner.right == [int]
			assert e.inner.wrong == [int, [int]]
			assert e.inner.index == 2
			assert isinstance(e.inner.inner, _TC_IndexTypeError)
			assert e.inner.inner.index == 1
			assert e.inner.inner.right == int
			assert e.inner.inner.wrong == [int]
		else:
			self.fail("Passed incorrectly")
			
	def test_lists_of_tuples(self):
		from typecheck import _TC_IndexTypeError, List
		
		# lists of 2-tuples of integer x float
		list3 = List( (int, float) )
		
		list3( [(1, 2.0), (2, 3.0), (3, 4.0)] )
		try:
			# The types are flipped
			list3( [(2.0, 1), (3.0, 4)] )
		except _TC_IndexTypeError, e:
			assert e.right == (int, float)
			assert e.wrong == (float, int)
			assert e.index == 0
			assert isinstance(e.inner, _TC_IndexTypeError)
			assert e.inner.wrong is float
			assert e.inner.right is int
			assert e.inner.index == 0
		else:
			self.fail("Passed incorrectly")
			
	def test_singly_nested_tuples(self):
		from typecheck import _TC_IndexTypeError, Tuple
	
		tup1 = Tuple( (int, int), int )
		
		# This should pass
		tup1( ((4,5), 6) )
		
		try:
			# This should raise an exception
			tup1( ([4,5], 6) )
		except _TC_IndexTypeError, e:
			assert e.right == (int, int)
			assert e.wrong == [int]
			assert e.index == 0
		else:
			self.fail("Passed incorrectly")
			
	def test_doubly_nested_tuples(self):
		from typecheck import _TC_IndexTypeError, Tuple
		
		# (((i, i), i), i)
		# Triply-nested 2-tuples of integers
		tup1 = Tuple( (int, int), int )
		tup2 = Tuple(tup1, int)
		
		tup2( (((4, 5), 6), 7) )
		
		try:
			# [4,5] is not a 2-tuple of int x int
			tup2( (([4,5], 6), 7) )
		except _TC_IndexTypeError, e:
			assert e.right == ((int, int), int)
			assert e.wrong == ([int], int)
			assert e.index == 0
			assert isinstance(e.inner, _TC_IndexTypeError)
			assert e.inner.index == 0
			assert e.inner.right == (int, int)
			assert e.inner.wrong == [int]
		else:
			self.fail("Passed incorrectly")
			
	def test_tuples_of_lists(self):
		from typecheck import _TC_IndexTypeError, Tuple
		
		# 2-tuples of list of integers x list of floats
		tup3 = Tuple( [int], [str] )
		
		# Should pass
		tup3( ([4,5,6], ["a","b","c"]) )
		
		try:
			tup3( (["a","b","c"], [4,5,6]) )
		except _TC_IndexTypeError, e:
			assert e.right == [int]
			assert e.wrong == [str]
			assert e.index == 0
			assert isinstance(e.inner, _TC_IndexTypeError)
			assert e.inner.index == 0
			assert e.inner.right is int
			assert e.inner.wrong is str
		else:
			self.fail("Passed incorrectly")
			
	def test_nested_dict_as_val(self):
		from typecheck import _TC_KeyTypeError, _TC_ValTypeError, Dict
	
		# int -> {int -> float}
		dict1 = Dict( int, {int: float})
		
		# Should pass
		dict1( {6: {6: 7.0, 8: 9.0}} )
		
		try:
			# Should fail (7.0 is not an integer)
			dict1( {6: {7.0: 8.0}} )
		except _TC_ValTypeError, e:
			assert e.right == {int: float}
			assert e.wrong == {float: float}
			assert e.key == 6
			assert e.val == {7.0: 8.0}
			assert isinstance(e.inner, _TC_KeyTypeError)
			assert e.inner.right is int
			assert e.inner.wrong is float
			assert e.inner.key == 7.0
		else:
			self.fail("Passed incorrectly")

	def test_nested_tuple_as_key(self):
		from typecheck import _TC_KeyTypeError, _TC_IndexTypeError, Dict
		
		# (int, int) -> float
		dict2 = Dict( (int, int), float )
		
		dict2( {(4,5): 5.0, (9,9): 9.0} )
		
		try:
			# Should fail; 5.0 in (5.0, 5) is not an integer
			dict2( {(5.0, 5): 5.0} )
		except _TC_KeyTypeError, e:
			assert e.right == (int, int)
			assert e.wrong == (float, int)
			assert e.key == (5.0, 5)
			assert isinstance(e.inner, _TC_IndexTypeError)
			assert e.inner.right is int
			assert e.inner.wrong is float
			assert e.inner.index == 0
		else:
			self.fail("Passed incorrectly")
			
	def test_or_lists(self):
		from typecheck import _TC_TypeError, List, Or
		
		or_type = Or(List(int), List(float))
		
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
		from typecheck import _TC_IndexTypeError, List, Or
		
		or_type = List( Or(int, float) )
		
		or_type( [4,5,6] )
		or_type( [4.0, 8, 5.0] )
		
		try:
			or_type( [8, "b"] )
		except _TC_IndexTypeError, e:
			assert e.index == 1
			assert e.wrong == str
			assert e.right == Or(int, float)
		else:
			self.fail("Passed incorrectly")
			
	def test_nested_ors_ands(self):
		from typecheck import _TC_TypeError, Or, And
		
		class A: pass
		class B: pass
		class C(A, B): pass
		
		and_type = And( Or(int, A), B)
		
		and_type(C())
		
		try:
			and_type(A())
		except _TC_TypeError, e:
			assert e.wrong == A
			assert e.right == and_type
		else:
			self.fail("Passed incorrectly")
			
	def test_dict_of_ors(self):
		from typecheck import _TC_KeyTypeError, Or, Dict
		
		or_type = Or(int, float)
		dict_type = Dict(or_type, or_type)
		
		dict_type( {4:4, 4.0:4, 4:7.0} )
		
		try:
			dict_type( {'f': 5} )
		except _TC_KeyTypeError, e:
			assert e.wrong == str
			assert e.right == or_type
			assert e.key == 'f'
		else:
			self.fail("Passed incorrectly")

class OrTests(unittest.TestCase):
	def setUp(self):
		from typecheck import Or
	
		self.or_type = Or(int, float)
		
	def test_success(self):
		from typecheck import Or
	
		self.or_type(5)
		self.or_type(7.0)
		
		class A:
			pass
			
		class B:
			pass
			
		class C(A, B):
			pass
			
		or_type = Or(A, B)
		or_type(C())
		
	def test_failure(self):
		from typecheck import _TC_TypeError, Or
	
		try:
			self.or_type("foo")
		except _TC_TypeError, e:
			assert e.right == Or(int, float)
			assert e.wrong == str
		else:
			self.fail("Passed incorrectly")
			
class AndTests(unittest.TestCase):
	def test_success(self):
		from typecheck import And
	
		class A:
			pass
			
		class B:
			pass
			
		class C(A, B):
			pass
			
		and_type = And(A, B)
		and_type(C())
		
	def test_failure(self):
		from typecheck import _TC_TypeError, And
	
		and_type = And(int, float)
	
		try:
			and_type("foo")
		except _TC_TypeError, e:
			assert e.right == And(int, float)
			assert e.wrong == str
		else:
			self.fail("Passed incorrectly")
			
class EmptyTests(unittest.TestCase):
	def test_list_success(self):
		from typecheck import Empty
	
		l = Empty(list)
		l([])
	
	def test_list_failure(self):
		from typecheck import Empty, _TC_LengthError
		
		l = Empty(list)
		
		try:
			l([5, 6])
		except _TC_LengthError, e:
			assert e.wrong == 2
			assert e.right == 0
		else:
			self.fail("Passed incorrectly")
			
	def test_dict_success(self):
		from typecheck import Empty
	
		d = Empty(dict)
		d({})
	
	def test_dict_failure(self):
		from typecheck import Empty, _TC_LengthError
		
		d = Empty(dict)
		
		try:
			d({'f': 5})
		except _TC_LengthError, e:
			assert e.wrong == 1
			assert e.right == 0
		else:
			self.fail("Passed incorrectly")
			
	def test_tuple_success(self):
		from typecheck import Tuple
	
		t = Tuple()
		t(tuple())
	
	def test_tuple_failure(self):
		from typecheck import Tuple, _TC_TypeError
		
		t = Tuple()
		
		try:
			t((5, 6))
		except _TC_TypeError, e:
			assert e.wrong == (int, int)
			assert e.right == ()
		else:
			self.fail("Passed incorrectly")
			
### Bookkeeping ###
if __name__ == '__main__':
	support.run_all_tests(globals())
