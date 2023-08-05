from typecheck import typecheck

@typecheck(str)
def checker(aString):
    """    
    >>> print [x for x in globals().copy() if not x.startswith('__')]
    ['checker2', 'typecheck', '_[1]', 'checker', 'Rational', 'testMyClass', 'MyTestClass']
    >>> print [x for x in locals().copy() if not x.startswith('__')]
    ['checker2', 'typecheck', '_[1]', 'checker', 'Rational', 'testMyClass', 'x', 'MyTestClass']
    >>> checker('Nonsense')
    2
    """
    if aString == "":
        return 1
    else:
        return 2

def checker2(aString):
    """
    >>> print [x for x in globals().copy() if not x.startswith('__')]
    ['checker2', 'typecheck', '_[1]', 'checker', 'Rational', 'testMyClass', 'MyTestClass']
    >>> print [x for x in locals().copy() if not x.startswith('__')]
    ['checker2', 'typecheck', '_[1]', 'checker', 'Rational', 'testMyClass', 'x', 'MyTestClass']
    >>> checker2('Nonsense')
    2
    """
    if aString == "":
        return 1
    else:
        return 2

class Rational(object):
    @typecheck(object, int, int)
    def __init__(self, numerator, denumerator):
        self.p = numerator
        self.q = denumerator

class MyTestClass:
    @typecheck(object, int, Rational)
    def __init__(self, a, b):
        pass

def testMyClass():
	"""
	>>> print MyTestClass(1, Rational(1, 2)) # doctest:+ELLIPSIS
	<typecheck._unittests.doctests.MyTestClass instance at 0x...>
	"""
	pass