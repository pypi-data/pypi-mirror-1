import inspect
import types

enable_checking = True

### Internal exception classes (these MUST NOT get out to the user)
### typecheck_{args,return} should catch these and convert them to
### appropriate AssertionError instances

# We can't inherit from object because raise doesn't like new-style classes
# We can't use super() because we can't inherit from object
class _TC_AssertionError(Exception):
	pass

class _TC_LengthError(_TC_AssertionError):
	def __init__(self, wrong, right=None):
		_TC_AssertionError.__init__(self)
	
		self.wrong = wrong
		self.right = right

class _TC_TypeError(_TC_AssertionError):
	def __init__(self, wrong, right):
		_TC_AssertionError.__init__(self)
	
		self.wrong = calculate_type(wrong)
		self.right = right

class _TC_NestedTypeError(_TC_TypeError):
	def __init__(self, wrong, right, inner_exception=None):
		_TC_TypeError.__init__(self, wrong, right)
	
		self.inner = inner_exception	

class _TC_IndexTypeError(_TC_NestedTypeError):
	def __init__(self, wrong, right, index, inner_exception=None):
		_TC_NestedTypeError.__init__(self, wrong, right, inner_exception)
	
		self.index = index

class _TC_KeyTypeError(_TC_NestedTypeError):
	def __init__(self, wrong, right, key, inner_exception=None):
		_TC_NestedTypeError.__init__(self, wrong, right, inner_exception)
		
		self.key = key
		
class _TC_ValTypeError(_TC_KeyTypeError):
	def __init__(self, wrong, right, key, val, inner_exception=None):
		_TC_KeyTypeError.__init__(self, wrong, right, key, inner_exception)

		self.val = val
	
### Factory function; this is what should be used to dispatch
### type-checker class requests

def Type(obj):
	if isinstance(obj, CheckType):
		return obj
	elif isinstance(obj, list):
		if len(obj) == 0:
			return Empty(list)
		return List( *[Type(t) for t in obj] )
	elif isinstance(obj, tuple):
		#if len(obj) == 0:
		#	return Empty(tuple)
		return Tuple( *[Type(t) for t in obj] )
	elif isinstance(obj, dict):
		if len(obj) == 0:
			return Empty(dict)
		return Dict(obj.keys()[0], obj.values()[0])
	elif isinstance(obj, (types.ClassType, types.TypeType)):
		return Single(obj)
	raise AssertionError("Object is of type '%s'; not a type" % str(type(obj)))

### Deduce the type of a data structure

def calculate_type(obj):
	if isinstance(obj, types.InstanceType):
		return obj.__class__
	elif isinstance(obj, types.DictType):
		if len(obj) == 0:
			return {}

		key_types = set()
		val_types = set()
		
		for (k,v) in obj.items():
			key_types.add( calculate_type(k) )
			val_types.add( calculate_type(v) )
			
		if len(key_types) == 1:
			key_types = key_types.pop()
		else:
			key_types = Or(*key_types)
			
		if len(val_types) == 1:
			val_types = val_types.pop()
		else:
			val_types = Or(*val_types)
			
		return {key_types: val_types}
	elif isinstance(obj, types.TupleType):
		return tuple([calculate_type(t) for t in obj])
	elif isinstance(obj, types.ListType):
		length = len(obj)
		if length == 0:
			return []
		obj = [calculate_type(o) for o in obj]

		partitions = [1]
		partitions.extend([i for i in range(2, int(length/2)+1) if length%i==0])
		partitions.append(length)

		def evaluate(items_per):
			parts = length / items_per

			for i in range(0, parts):
				for j in range(0, items_per):
					if obj[items_per * i + j] != obj[j]:
						raise StopIteration
			return obj[0:items_per]

		for items_per in partitions:
			try:
				return evaluate(items_per)
			except StopIteration:
				continue
	else:
		return type(obj)

### The following classes are the work-horses of the typechecker

class CheckType(object):
	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		return type(self).name + '(' + ', '.join([str(t) for t in self._types]) + ')'

	def __eq__(self, other):
		return not self != other
		
	def __ne__(self, other):
		return not self == other

class Any(CheckType):
	name = "Any"
	
	def __init__(self):
		self.type = object
	
	def __call__(self, to_check):
		return True
		
	def __str__(self):
		return "Any()"
		
	def __repr__(self):
		return "Any()"
		
	def __eq__(self, other):
		return other.__class__ is self.__class__

class Single(CheckType):
	name = "Single"

	def __init__(self, type):
		if isinstance(type, CheckType):
			self.type = type.type
		elif not isinstance(type, (types.ClassType, types.TypeType)):
			raise TypeError("Cannot type-check a %s" % type(type))
		else:
			self.type = type
			
		self._types = [self.type]

	def __call__(self, to_check):
		if not isinstance(to_check, self.type):
			raise _TC_TypeError(to_check, self.type)
		return True
		
	def __eq__(self, other):
		if other.__class__ is not self.__class__:
			return False
		return self.type == other.type
		
class Empty(Single):
	name = "Empty"
	
	def __init__(self, type):
		Single.__init__(self, type)
		
		if type not in (dict, list):
			raise TypeError("Can only assert emptyness for dicts and lists")

	def __call__(self, to_check):
		Single.__call__(self, to_check)
		
		if len(to_check) > 0:
			raise _TC_LengthError(len(to_check), 0)
		return True
		

class Dict(CheckType):
	name = "Dict"

	def __init__(self, key, val):
		self.__check_key = Type(key)
		self.__check_val = Type(val)
		
		self.type = { key: val }
		self._types = [key, val]
		
	def __call__(self, to_check):
		if not isinstance(to_check, types.DictType):
			raise _TC_TypeError(to_check, self.type)
		
		for (k, v) in to_check.items():
			# Check the key
			try:
				self.__check_key(k)
			except _TC_TypeError, inner:
				raise _TC_KeyTypeError(k, self.__check_key.type, k, inner)

			# Check the value
			try:
				self.__check_val(v)
			except _TC_TypeError, inner:
				raise _TC_ValTypeError(v, self.__check_val.type, k, v, inner)
		return True
		
	def __eq__(self, other):
		if other.__class__ is not self.__class__:
			return False
		return self.type == other.type

class List(CheckType):
	name = "List"

	def __init__(self, *type):
		self._types = [Type(t) for t in type]
		self.type = [t.type for t in self._types]

	def __call__(self, to_check):
		if not isinstance(to_check, types.ListType):
			raise _TC_TypeError(to_check, self.type)
		if len(to_check) % len(self._types):
			raise _TC_LengthError(len(to_check))
			
		pat_len = len(self._types)
		type_tuples = [(i, val, self._types[i % pat_len]) for (i, val)
					in enumerate(to_check)]
		for (i, val, check_type) in type_tuples:
			try:
				check_type(val)
			except _TC_TypeError, inner:
				raise _TC_IndexTypeError(val, check_type.type, i, inner)
		return True
		
	def __eq__(self, other):
		if other.__class__ is not self.__class__:
			return False
			
		if len(self._types) != len(other._types):
			return False
		
		for (s, o) in zip(self._types, other._types):
			if s != o:
				return False
		return True

class Tuple(List):
	name = "Tuple"

	def __init__(self, *type):
		List.__init__(self, *type)
		
		self.type = tuple(self.type)

	def __call__(self, to_check):
		if not isinstance(to_check, types.TupleType) or len(to_check) != len(self._types):
			raise _TC_TypeError(to_check, self.type)

		for (i, (val, check_type)) in enumerate(zip(to_check, self._types)):
			try:
				check_type(val)
			except _TC_TypeError, inner:
				raise _TC_IndexTypeError(val, check_type.type, i, inner)
				
		return True

class Or(CheckType):
	name = "Or"

	def __init__(self, *types):
		self._types = set([Type(t) for t in types])
		self.type = self

	def __call__(self, to_check):
		for check_type in self._types:
			try:
				check_type(to_check)
				return True
			except _TC_TypeError:
				pass

		raise _TC_TypeError(to_check, self)
		
	def __eq__(self, other):
		if other.__class__ is not self.__class__:
			return False
		return self._types == self._types

class And(Or):
	name = "And"

	def __call__(self, to_check):
		for check_type in self._types:
			try:
				check_type(to_check)
			except _TC_TypeError, e:
				raise _TC_TypeError(to_check, self)
		return True
		
### This is the public side of the module
#########################################

# This is for compatibility with the typechecker from
# http://www.ilowe.net/software/typecheck/
class TypeCheckException(Exception):
	pass

class TypeCheckError(TypeCheckException):
	def __init__(self, bad_object, exception):
		TypeCheckException.__init__(self)
		
		self.internal = exception
		self.bad_object = bad_object
		
		message = "In %s" % str(self.bad_object)

		while exception:
			if isinstance(exception, _TC_NestedTypeError):
				if isinstance(exception, _TC_ValTypeError):
					message += ", at key '%s', value '%s'" % (exception.key, exception.val)
				elif isinstance(exception, _TC_KeyTypeError):
					message += ", for key '%s'" % str(exception.key)
				else:
					message += ", at index %d" % exception.index
				exception = exception.inner
			else:
				if isinstance(exception, _TC_LengthError):
					if exception.right is not None:
						m = ", expected %d" % exception.right
					message += ", length was %d%s" % (exception.wrong, m or "")
				elif isinstance(exception, _TC_TypeError):
					message += ", expected %s, got %s" % (exception.right, exception.wrong)
				break
		self.__message = message
		
	def __str__(self):
		return self.__message
		
class TypeSignatureError(Exception):
	def __str__(self):
		return "The signature does not match the shape of the function's arguments"

# The current implementation of Self always returns True
Self = Any()

### Begin helper classes/functions for typecheck_args
#####################################################
class __InternalError(Exception):
	pass

# ref_tup is ignored; it's there so tuplize
# has the same signature as tuplize_and_check
def tuplize(lst, ref_tup=None):
	def __worker(e):
		if isinstance(e, list):
			e = tuplize(e)
		return e
	return tuple(__worker(e) for e in lst)		

def tuplize_and_check(lst, ref_tup):
	if not(isinstance(ref_tup, tuple) and len(lst) == len(ref_tup)):
		raise __InternalError()

	def __worker(elem, ref):
		if isinstance(elem, list):
			return tuplize_and_check(elem, ref)
		return elem
	return tuple(__worker(*e_r_tup) for e_r_tup in zip(lst, ref_tup))

def curry(func, *args):
	curried_args = list(args)
	def __curried_func(*vargs, **kwargs):
		return func(*(curried_args + list(vargs)), **kwargs)
	return __curried_func

def analyse_params(pos_names, kw_names, vargs, kwargs, handle_missing_kw, tuplizer):
	vargs = list(vargs)
	kwargs = dict(kwargs)

	names = {}

	for name in pos_names:
		if len(vargs) == 0:
			if name not in kwargs:
				raise TypeSignatureError()
			names[name] = kwargs.pop(name)
		else:
			if isinstance(name, list):
				if not isinstance(vargs[0], tuple):
					raise __InternalError("unpack non-sequence")
				name = tuplizer(name, vargs[0])
			names[name] = vargs.pop(0)

	for name in kw_names:
		if name in names:
			raise __InternalError("got two values for %s" % name)
		if len(vargs) > 0:
			t = vargs.pop(0)
		elif name in kwargs:
			t = kwargs.pop(name)
		else:
			try:
				handle_missing_kw()
			except StopIteration: # XXX Ewwww!
				continue
		names[name] = t

	reconstructed = []
	for name in pos_names:
		if isinstance(name, list):
			name = tuplize(name)
		reconstructed.append(names.pop(name))

	return tuple(reconstructed), names, vargs, kwargs

def fix_fake_func(fake_func, real_func):
	fake_func.__module__ = real_func.__module__
	fake_func.__name__ = real_func.__name__
	fake_func.__doc__ = real_func.__doc__

###################################################
### End helper classes/functions for typecheck_args

def typecheck_args(*v_sig, **kw_sig):
	# typecheck_args is run to obtain the real decorator
	def decorator(func):
		(param_list, varg_name, kwarg_name, defaults)  = inspect.getargspec(func)

		# Normalise the lists of keyword and positional argument names
		if defaults is None:
			kw_names = []
			pos_names = param_list
		else:
			kw_names = param_list[-len(defaults):]
			pos_names = param_list[:-len(defaults)]

		# Curry pos_names and kw_names into analyse_params
		analyse = curry(analyse_params, pos_names, kw_names)

		# This will be invoked when analyse comes upon a keyword argument
		# that it can't find a value for
		def types__missing_kw():
			raise TypeSignatureError()

		# Try to find a type for each argument
		# If anything is amiss, consider the entire signature invalid
		# and inform the user
		try:
			types, kw_types, t_vargs, t_kwargs = analyse(v_sig, kw_sig, types__missing_kw, tuplize_and_check)
		except __InternalError:
			raise TypeSignatureError()
		
		# We need to fix-up the types of the *vargs and **kwargs parameters
		fix = (
			(varg_name, list, lambda t: [t]),
			(kwarg_name, dict, lambda t: {str: t}) )

		fixed_dict = {}
		for (name, typ, action) in fix:
			if name is not None:
				if len(t_vargs):
					t = t_vargs.pop(0)
				elif name in t_kwargs:
					t = t_kwargs.pop(name)
				else:
					raise TypeSignatureError()
				if not isinstance(t, (typ, CheckType)):
					t = action(t)
				fixed_dict[name] = t
		
		# If we're using *vargs or **kwargs, make the switch to the
		# fixed-up types. If there are no *vargs or **kwargs parameters
		# in use, but there are leftover positional or keyword arguments,
		# consider the signature invalid
		if kwarg_name is not None:
			t_kwargs = fixed_dict.pop(kwarg_name)
		elif len(t_kwargs) > 0:
				raise TypeSignatureError()
		if varg_name is not None:
			t_vargs = fixed_dict.pop(varg_name)
		elif len(t_vargs) > 0:
				raise TypeSignatureError()

		# Like types__handle_missing (above), but uses StopIteration
		# to signal that the keyword-examiner should `continue`
		#
		# XXX Come up with a better way of signalling this than
		# StopIteration
		def args__handle_missing():
			raise StopIteration
			
		def _fake_func(*__vargs, **__kwargs):
			global enable_checking
			
			# Type-checking can be turned on and off by toggling the
			# value of the global enable_checking variable
			if enable_checking:
				args, kw_args, a_vargs, a_kwargs = analyse(__vargs, __kwargs, args__handle_missing, tuplize)

				# Type-check the keyword arguments
				for (name, val) in kw_args.items():
					try:
						check_type = Type(kw_types[name])
						check_type(val)
					except _TC_AssertionError, e:
						middle_exc = _TC_ValTypeError(val, check_type.type, name, val, e)
						raise TypeCheckError(kw_args, middle_exc)

				# Type-check everything else
				for (arg, typ) in ((args, types), (a_vargs, t_vargs), (a_kwargs, t_kwargs)):
					try:
						Type(typ)(arg)
					except _TC_AssertionError, e:
						raise TypeCheckError(arg, e)
			
			return func(*__vargs, **__kwargs)
		fix_fake_func(_fake_func, func)
		return _fake_func
	return decorator
	
# Add an alias for compatibility with the typechecker found at
# http://www.ilowe.net/software/typecheck/
typecheck = typecheck_args
	
def typecheck_return(*signature):
	if len(signature) == 1:
		check_type = Type(signature[0])
	else:
		check_type = Type(signature)

	def decorator(func):
		def fake_function(*args, **kwargs):
			return_vals = func(*args, **kwargs)
		
			if enable_checking:
				try:
					check_type(return_vals)
				except _TC_AssertionError, e:
					raise TypeCheckError(return_vals, e)

			# Everything checks out. Return the results
			return return_vals
		fix_fake_func(fake_function, func)
		return fake_function
	return decorator

