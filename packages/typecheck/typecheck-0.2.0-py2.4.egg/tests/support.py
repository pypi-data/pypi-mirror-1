import types
import unittest
import sys
import os.path

def find_tests(globals_dict):
	globals_list = globals_dict.values()
	return [unittest.makeSuite(c) for c in globals_list
				if isinstance(c, types.TypeType)
				and unittest.TestCase in c.__bases__]

def run_all_tests(globals_dict):
	all_tests = unittest.TestSuite( find_tests(globals_dict) )

	unittest.TextTestRunner(verbosity=2).run(all_tests)

def adjust_path():
	parent_dir = os.path.split(sys.path[0])[0]
	sys.path.append(parent_dir)

class ToDoException(Exception):
	def __init__(self, message, exception):
		Exception.__init__(self, message, exception)
		
		self.message = message
		self.exception = exception
	
	def __str__(self):
		exc = self.exception
		text = [self.message, ": ", exc.__class__, exc.args]

		return "".join(map(str, text))
	
def TODO(message="TODO"):
	def decorator(func):
		def __todo_func(*args, **kwargs):
			try:
				ret_val = func(*args, **kwargs)
			except AssertionError, e:
				raise ToDoException(message, e)
			
			raise RuntimeWarning("TODO test succeeded unexpectedly")
			return ret_val
		return __todo_func
	return decorator
