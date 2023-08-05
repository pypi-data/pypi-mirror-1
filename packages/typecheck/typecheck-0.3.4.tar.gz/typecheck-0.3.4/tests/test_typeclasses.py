import support
from support import TODO, TestCase

if __name__ == '__main__':
	support.adjust_path()
### /Bookkeeping ###

import unittest

import typecheck
import typecheck.typeclasses

def check_type(typ, obj):
    typecheck.check_type(typ, None, obj)

class TestTypeClass(TestCase): 
    def _test_types(self, typeclass):
        for typ in self.types:
            check_type(typeclass(), typ)
            check_type(typeclass, typ)
  
class Test_Number(TestTypeClass):
    types = (complex, long, float, int, bool)

    def test_numerics(self):
        from typecheck.typeclasses import Number
    
        self._test_types(Number)
            
    def test_decimal(self):
        try:
            from decimal import Decimal
            
            check_type(Number(), Decimal(5))
            check_type(Number, Decimal(5))
        except:
            pass

class Test_MSequence(TestTypeClass):
    types = (list,)
    
    def test_msequence(self):
        from typecheck.typeclasses import MSequence
        
        self._test_types(MSequence)

class Test_ImSequence(TestTypeClass):
    types = (tuple, buffer, xrange)
    
    def test_imsequence(self):
        from typecheck.typeclasses import ImSequence
        
        self._test_types(ImSequence)

class Test_String(Test_ImSequence):
    types = (str, unicode)

    def test_string(self):
        from typecheck.typeclasses import String
        
        self._test_types(String)
        
class Test_Mapping(TestTypeClass):
    types = (dict,)

    def test_mapping(self):
        from typecheck.typeclasses import Mapping
        
        self._test_types(Mapping)

### Bookkeeping ###
if __name__ == '__main__':
	import __main__
	support.run_all_tests(__main__)
