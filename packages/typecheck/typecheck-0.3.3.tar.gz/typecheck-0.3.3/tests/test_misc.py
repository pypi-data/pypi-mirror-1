import support
from support import TODO, TestCase, test_hash, test_equality

if __name__ == '__main__':
	support.adjust_path()
### /Bookkeeping ###

import types
import unittest

import typecheck

class TypeVariables_persist_from_one_func_to_another(TestCase):
	def test(self):
		from typecheck import typecheck_args, Self, Or, Any
		
		Self = Self()
		prop_t = {str: str}
		
		class MockEntry(object):
			@typecheck_args(Self, Any(), str, Any(), prop_t)
			def __init__(self, repository, path, revision, property={}):
				pass

		class MockFileEntry(MockEntry):
			@typecheck_args(Self, Any(), str, Any(), str, prop_t)
			def __init__(self, repository, path, revision, data="", property={}):
				print "\tHeading into MockEntry.__init__"
				MockEntry.__init__(self, repository, path, revision, property)

		class MockDirEntry(MockEntry):
			@typecheck_args(Self, Any(), str, Any(), [Or(MockFileEntry, Self)], prop_t)
			def __init__(self, repository, path, revision, entries=[], property={}):
				print "\tHeading into MockEntry.__init__"
				MockEntry.__init__(self, repository, path, revision, property)

		print "Creating MockFileEntry"
		f = MockFileEntry('repo', 'foo.bar', 'rev')
		print "Finished with MockFileEntry"
		entries = [f]
		
		print "Creating MockDirEntry"
		d = MockDirEntry('repo', 'test', 'rev', entries)
		print "Finished with MockDirEntry"

### Bookkeeping ###
if __name__ == '__main__':
	import __main__
	support.run_all_tests(__main__)
