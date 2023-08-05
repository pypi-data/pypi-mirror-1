"""Aspect Oriented Python


How to wrap a function:
	from aopython import Aspect
	def negate(x):
		return -x

	aspect = Aspect()
	negate = aspect.wrap(negate)

	negate(2) # advised function call


How to weave a class:
	from aopython import Aspect
	class MyObj(object):
		def double(self, x):
			return x * 2
		def tripple(self, x):
			return x * 3

	aspect = Aspect()
	aspect.weave(MyObj)

	myobj = MyObj()
	myobj.double(5) # advised method call
	MyObj.tripple(myobj, 5) # advised method call


Note: neither of these examples actually does anything since we just used the
base Aspect class. To do something useful, extend Aspect and override the
advise method.

See aopythonexamples.py for a more advanced overview of how to use the classes
and functions that make up AOPython.

aopythontest.py contains unit tests for the aopython module.


Copyright (c) 2007 Daniel Miller
This module is free software, and you may redistribute it and/or modify
it under the same terms as Python itself, so long as this copyright message
and disclaimer are retained in their original form.

IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
"""

__version__ = "1.0.2"

from types import FunctionType
from inspect import getmembers, ismethod, isfunction, isclass
from weakref import WeakKeyDictionary

__all__ = ["Aspect", "weave", "iswrapped", "unwrap", "MethodHasNoAdviceError"]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# public interface

class Aspect(object):
	"""Aspect base class. All aspects should extend this class.
	
	Can advise user-defined functions, lambda functions, built-in functions,
	unbound (class) methods, and bound (instance) methods."""

	def advise(self, method, *args, **kwargs):
		"""Override this method to provide advice to the method/function call
		
		This method will normaly invoke the given method/function with the
		supplied arguments and return the result. However, it is not required
		to do either of those things.
		
		All methods (n/a for functions) are unbound before being passed to
		'advise', and the first item in args is the self argument of the
		method. Note that the self argument in advise refers to the aspect
		instance, not the instance of the wrapped method."""
		return method(*args, **kwargs)
	
	def wrap(self, method, allowUnwrap=False):
		"""Return the given callable wrapped with the advice provided by this aspect
		
		This function works with any callable object. The returned function/
		method has the same __dict__ or a dictionary containing the same
		__dict__ items as the unwrapped version if possible.
		
		WARNING: the type of the returned callable may not match the type of
		the original callable.
		
		Arguments:
		method - the callable to be wrapped
		allowUnwrap - if set to True, the returned (wrapped) method can be
			unwrapped at a later time. WARNING: the current implementation
			uses a dictionary to map the wrapped method to the unwrapped
			method, and the size of that dictionary may grow very large if
			many methods are wrapped with this flag set to True.

		Raises TypeError if the given method is not callable."""
		if callable(method):
			class_ = getattr(method, 'im_class', None)
			self_ = getattr(method, 'im_self', None)
			if self_:
				unbound = method.im_func.__get__(None, type(self_))
			else:
				unbound = method

			def _method(*args, **kwargs):
				return self.advise(unbound, *args, **kwargs)
			
			# Create a new function with the correct __name__ and __dict__
			code = _method.func_code
			globals_ = getattr(_method, "func_globals", None)
			name_ = getattr(method, '__name__', None)
			defaults = getattr(getattr(method, 'im_func', method), 'func_defaults', None)
			closure = _method.func_closure
			_method = FunctionType(code, globals_, name_, defaults, closure)
			if isinstance(getattr(method, "__dict__", None), dict):
				_method.__dict__ = method.__dict__
			else:
				try:
					_method.__dict__ = dict(method.__dict__)
				except:
					pass

			if allowUnwrap:
				_unwrapDict[_method] = method

			if class_:
				return _method.__get__(self_, class_)
			else:
				return _method
		else:
			raise TypeError("cannot apply %s: %r of %s is not callable" % (type(self).__name__, method, type(method)))
		
	def weave(self, obj, includes=(), excludes=(), depth=0, allowUnwrap=False,
		wrapIfStartsWithUnderscore=False, weaveTest=None):
		"""Convenience method to weave an object with this aspect.
		
		See aopython.weave (a function in this module) for detailed usage
		instructions. Note that aopython.weave can weave more than one aspect
		in a single weave() call.
		"""
		weave(self, obj, includes, excludes, depth, allowUnwrap,
			wrapIfStartsWithUnderscore, weaveTest)
	
def weave(aspect, obj, includes=(), excludes=(), depth=0, allowUnwrap=False,
		wrapIfStartsWithUnderscore=False, weaveTest=None):
	"""Advise each method or function belonging to obj

	Arguments:
	aspect - an Aspect instance or a sequence of Aspect instances with
		which to weave obj. If this argument is a sequence, the order is
		important: aspects will be weaved in the order they are listed, and
		their advise methods will be called in the opposite order when a
		wrapped method/function is called.
	obj - an object whose methods/functions/classes will be wrapped.
		If this is a class or an instance its methods will be wrapped.
		If this is a module all of its functions will be wrapped.
	includes - a sequence of method names that will be wrapped.
		All methods will be included if this is an empty sequence (default).
	excludes - a sequence of method names that will not be wrapped.
		No methods will be excluded if this is an empty sequence (default).
		Excludes override includes (e.g. if a name is is both includes and
		excludes it will be excluded).
	depth - the maximum number of levels to be woven. The default
		behavior (depth=0) only wraps functions or methods belonging
		directly to the object being weaved.
		Example for weave(aspect, module, ...):
		module.function       # depth=0
		module.Class          # depth=0
		module.Class.method   # depth=1
		Note that if this value is less than zero, the objects on level
		zero will still be wrapped.
		Note: setting this value to more than one (1) may result in
		unpredictable results depending on the target object being wrapped.
	allowUnwrap - see the allowUnwrap argument of Aspect.wrap
	wrapIfStartsWithUnderscore - if this argument evaluates to True, all
		functions and methods with names starting with an underscore will
		be elligible to be wrapped. Otherwise they are excluded.
		Defaults to False.
	weaveTest - a function that tests the objects that are being weaved.
		The function must take a single object argument and return True if
		the object should be wrapped and False if the object should not be
		wrapped. The result of this function overrides the normal test that
		is applied to each object to determine if it is a method or
		function. includes and excludes are processed after wrapTest.
		Note: if this function returns True for a non-callable object an
		exception will be raised when the object is wrapped.

	includes and excludes may contain predicate functions that match
	method names. Each predicate function must take a single string
	argument and return True or False.
	"""
	if weaveTest is None:
		def weaveTest(obj):
			return ismethod(obj) or isfunction(obj)

	weaveTest = _MethodNameMatchingAspect(includes, excludes, wrapIfStartsWithUnderscore).wrap(weaveTest)

	if isinstance(aspect, Aspect):
		aspects = (aspect,)
	else:
		aspects = aspect

	def _weave(obj, weaveDepth):
		methods = getmembers(obj, weaveTest)
		weavables = [member for name, member in getmembers(obj)]

		if weavables and weaveDepth < depth:
			weaveDepth += 1
			for weavable in weavables:
				_weave(weavable, weaveDepth)

		for methodName, method in methods:
			for aspect in aspects:
				method = aspect.wrap(method, allowUnwrap)
				try:
					setattr(obj, methodName, method)
				except:
					pass

	_weave(obj, 0)

def iswrapped(method):
	"""Return True if the given method can be unwrapped.
	
	NOTICE: this function will only return True if the allowUnwrap flag was set
	when the method was wrapped.
	"""
	return _unwrapDict.has_key(_getFunction(method))

def unwrap(method, all=False, quiet=False):
	"""Unwrap the given method
	
	NOTICE: this function will only work if the allowUnwrap flag was set when
	the method was wrapped.
	
	Arguments:
	all - when True, unwrap all subsequently wrapped functions before
		returning. In other words, always return a function that cannot be
		unwrapped when True.
	quiet - when False (default), raise a MethodHasNoAdviceError if the method
		(or any subsequently wrapped methods if all=True) cannot be unwrapped.
		When True, return the original method without raising an exception if
		the method cannot be unwrapped.
	
	Raises MethodHasNoAdviceError if quiet=False (default).
	"""
	try:
		if not iswrapped(method): raise KeyError()
		func = _unwrapDict[_getFunction(method)]
		if all and iswrapped(func):
			return unwrap(func, all, quiet)
		else:
			return func
	except KeyError:
		if not quiet:
			raise MethodHasNoAdviceError('%s is not wrapped' % method)
		return method

def unweave(obj, all=False, depth=0):
	"""Unwrap all wrapped callables on the given object
	
	This function does the opposite of weave without all the conditions
	such as includes, excludes, and weaveTest.
	
	Arguments:
	all - see 'all' arg of 'unwrap'
	depth - see 'depth' arg of 'weave'
	"""
	def _unweave(obj, weaveDepth):
		for methodName, method in getmembers(obj, iswrapped):
			method = unwrap(method, all)
			setattr(obj, methodName, method)
		
		weavables = [member for name, member in getmembers(obj)]

		if weavables and weaveDepth < depth:
			weaveDepth += 1
			for weavable in weavables:
				_unweave(weavable, weaveDepth)

	_unweave(obj, 0)

class MethodHasNoAdviceError(Exception):
	"""Exception raised by unwrap when a method cannot be unwrapped"""
	pass


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# internals

_unwrapDict = WeakKeyDictionary()

class _MethodNameMatchingAspect(Aspect):
	"""Helper aspect used by weave to match methods by name"""
	def __init__(self, includes, excludes, wrapIfStartsWithUnderscore=False):
		def separate(litsAndPreds):
			literals, predicates = [], []
			# Separate the literal names from the predicate functions
			for obj in litsAndPreds:
				if callable(obj):
					predicates.append(obj)
				else:
					literals.append(str(obj))
			return (literals, predicates)

		self.includes, self.includesFunc = separate(includes)
		self.excludes, self.excludesFunc = separate(excludes)

		if not includes:
			# Include all methods
			self.includesFunc.append(lambda n: True)

		if not wrapIfStartsWithUnderscore:
			# Exclude methods that start with underscore
			self.excludesFunc.append(lambda n: n and n.startswith('_'))

	def isMatch(self, methodName, literals, predicates):
		# Simplest case first: check for matching literal in strings
		if literals and methodName in literals:
			return True
		elif predicates:
			# Try to match with a predicate function
			for predicate in predicates:
				if predicate(methodName):
					return True
		return False

	def isIncluded(self, methodName):
		return self.isMatch(methodName, self.includes, self.includesFunc)

	def isNotExcluded(self, methodName):
		return not self.isMatch(methodName, self.excludes, self.excludesFunc)

	def advise(self, method, *args, **kwargs):
		_name = getattr(args[0], "__name__", None)
		return method(*args, **kwargs) and self.isIncluded(_name) and self.isNotExcluded(_name)

def _getFunction(method):
	"""Helper function used by iswrapped and unwrap"""
	func = method
	while hasattr(func, 'im_func'): func = func.im_func
	return func

