"""AOPython examples

Copyright (c) 2007 Daniel Miller
Code in this file may be used freely in your own projects.

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Setup logging and test aspects to be used in the following doctests

>>> log = LoggerAspect(hideAddresses=True)
>>> ta = TestAspect()
>>> ta2 = TestAspect2()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Wrap an instance method with Aspect

>>> ta3 = Aspect()
>>> test3 = Test()
>>> test3.func = ta3.wrap(test3.func, allowUnwrap=True)

>>> test3.func(23)
23

>>> test3.func.exposed
True

>>> test3.func = unwrap(test3.func)

>>> test3.func(23)
23

>>> test3.func.exposed
True

>>> del ta3

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Wrap an instance method with multiple aspects

>>> test = Test()
>>> test.func = log.wrap(test.func, allowUnwrap=True)
>>> test.func = ta.wrap(test.func, allowUnwrap=True)
>>> test.func = ta2.wrap(test.func, allowUnwrap=True)

>>> test.func(x=2)
TestAspect2.advise change last arg from <Test object> to 'TestAspect2 replaced arg'
TestAspect2.advise fall back to original args due to exception: instance: unbound method func() must be called with Test instance as first argument (got str instance instead)
TestAspect.advise checking attribute func.exposed = True
Test.func(<Test object>, x=2)
2

>>> test.func.exposed
True

>>> test.func = unwrap(test.func, all=True)

>>> test.func(x=2)
2

>>> test.func.exposed
True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Wrap a class method with multiple aspects

>>> Test.func2 = log.wrap(Test.func2, allowUnwrap=True)
>>> Test.func2 = ta.wrap(Test.func2, allowUnwrap=True)
>>> Test.func2 = ta2.wrap(Test.func2, allowUnwrap=True)

>>> test.func2(5)
TestAspect2.advise change last arg from 5 to 'TestAspect2 replaced arg'
TestAspect.advise checking attribute func2.exposed = False
Test.func2(<Test object>, 'TestAspect2 replaced arg')
'TestAspect2 replaced arg + 100'

>>> test.func2.exposed
False

>>> Test.func2 = unwrap(Test.func2, all=True)

>>> test.func2(5)
'5 + 100'

>>> test.func2.exposed
False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Weave an instance with multiple aspects

>>> test = Test()
>>> weave((log, ta, ta2), test, [lambda n: n and n.startswith('func')], ['func3'], allowUnwrap=True)

>>> test.func(x=2)
TestAspect2.advise change last arg from <Test object> to 'TestAspect2 replaced arg'
TestAspect2.advise fall back to original args due to exception: instance: unbound method func() must be called with Test instance as first argument (got str instance instead)
TestAspect.advise checking attribute func.exposed = True
Test.func(<Test object>, x=2)
2

>>> test.func.exposed
True

>>> test.func2(2)
TestAspect2.advise change last arg from 2 to 'TestAspect2 replaced arg'
TestAspect.advise checking attribute func2.exposed = False
Test.func2(<Test object>, 'TestAspect2 replaced arg')
'TestAspect2 replaced arg + 100'

>>> test.func2.exposed
False

>>> test.func3(x=2)
2

>>> test._func(x=2)
Traceback (most recent call last):
	...
Exception: _func should not be wrapped


>>> unweave(test, all=True)

>>> test.func(x=2)
2

>>> test.func.exposed
True

>>> test.func2(2)
'2 + 100'

>>> test.func2.exposed
False

>>> test.func3(x=2)
2

>>> test._func(x=2)
Traceback (most recent call last):
	...
Exception: _func should not be wrapped

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Wrap a user-defined function

>>> def bar(x):
... 	return x
... 
>>> bar.exposed = True

>>> bar = log.wrap(bar, allowUnwrap=True)
>>> bar = ta2.wrap(bar, allowUnwrap=True)
>>> bar = ta.wrap(bar, allowUnwrap=True)

>>> bar(3)
TestAspect.advise checking attribute bar.exposed = True
TestAspect2.advise change last arg from 3 to 'TestAspect2 replaced arg'
aopythonexamples.bar('TestAspect2 replaced arg')
'TestAspect2 replaced arg'

>>> bar.exposed
True

>>> bar = unwrap(bar, all=True)
>>> bar(3)
3

>>> bar.exposed
True

>>> del bar

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Wrap a lambda function

>>> f = lambda x: x + 500
>>> f = log.wrap(f, allowUnwrap=True)
>>> f = ta2.wrap(f, allowUnwrap=True)
>>> f = ta.wrap(f, allowUnwrap=True)

>>> f.exposed = True

>>> f(3)
TestAspect.advise checking attribute <lambda>.exposed = True
TestAspect2.advise change last arg from 3 to 'TestAspect2 replaced arg'
aopythonexamples.<lambda>('TestAspect2 replaced arg')
TestAspect2.advise fall back to original args due to exception: instance: cannot concatenate 'str' and 'int' objects
aopythonexamples.<lambda>(3)
503

>>> f.exposed
True

>>> f = unwrap(f, all=True)

>>> f(3)
503

>>> f.exposed
True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Wrap list.append

>>> lst = []
>>> listAppend = lst.append
>>> listAppend = log.wrap(listAppend, allowUnwrap=True)
>>> listAppend = ta2.wrap(listAppend, allowUnwrap=True)
>>> listAppend = ta.wrap(listAppend, allowUnwrap=True)

>>> listAppend('something')
TestAspect.advise checking attribute append.exposed = <undefined>
TestAspect2.advise change last arg from 'something' to 'TestAspect2 replaced arg'
?.append('TestAspect2 replaced arg')

>>> lst
['TestAspect2 replaced arg']

>>> lst.append('something else')

>>> lst
['TestAspect2 replaced arg', 'something else']

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Something that will not turn out the way you expected

>>> Test = log.wrap(Test, allowUnwrap=True)
>>> Test = ta.wrap(Test, allowUnwrap=True)
>>> Test.gerryrigged = True # Set an attribute on the class after the wrap

>>> t = Test()
TestAspect.advise checking attribute Test.exposed = <undefined>
aopythonexamples.Test()

>>> t.func(5) # This works...
5

>>> Test.func(t, 5) # So does this...
5

>>> t.gerryrigged
Traceback (most recent call last):
	...
AttributeError: 'Test' object has no attribute 'gerryrigged'

# Explanataion: at this point Test is not a class; it is a function that
# returns instances of Test. Consequently, instances returned by Test
# do not have any of the attributes added to Test after it was wrapped.

>>> Test = unwrap(Test, all=True)


# One possible workaround: wrap __init__ instead of the class
>>> Test.__init__ = log.wrap(Test.__init__, allowUnwrap=True)
>>> Test.__init__ = ta.wrap(Test.__init__, allowUnwrap=True)
>>> Test.gerryrigged = True # Set an attribute after the wrap

>>> t = Test() # Notice logger advice output
TestAspect.advise checking attribute __init__.exposed = <undefined>
?.__init__(<Test object>)

>>> t.func(5) # This works...
5

>>> Test.func(t, 5) # So does this...
5

>>> t.gerryrigged
True

>>> Test.__init__ = unwrap(Test.__init__, all=True)
>>> del t, Test.gerryrigged

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Things you can't do
>>> ta.wrap(4)
Traceback (most recent call last):
	...
TypeError: cannot apply TestAspect: 4 of <type 'int'> is not callable


>>> lst = []
>>> lst.append = ta.wrap(lst.append)
Traceback (most recent call last):
	...
AttributeError: 'list' object attribute 'append' is read-only


>>> lst.append2 = ta.wrap(lst.append)
Traceback (most recent call last):
	...
AttributeError: 'list' object has no attribute 'append2'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Non-wrapped instance method
# Sanity check to make sure we haven't wrapped things we didn't intend to wrap

>>> test2 = Test()

>>> test2.func3(6)
6

>>> test2.func2.exposed
False

>>> test2.func(2)
2

>>> test2.func.exposed
True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import doctest
import re

from aopython import Aspect, weave, iswrapped, unwrap, unweave

# Example aspects
class LoggerAspect(Aspect):
	# A logger aspect that prints method invokation details
	def __init__(self, verbose=False, hideAddresses=False):
		self.verbose = verbose
		self.hideAddresses = hideAddresses
		self.memAddrRe = re.compile(r' at 0x[0123456789ABCDEF]+>')

	def getArgStr(self, args, kwargs={}):
		return ', '.join([self.repr_(arg) for arg in args] + ['%s=%s' % (key, repr(val)) for key, val in kwargs.items()])
	
	def repr_(self, obj):
		if self.hideAddresses:
			# Remove memory addresses from representation
			return self.memAddrRe.sub('>', repr(obj))
		return repr(obj)

	def printFunctionDetails(self, function, indent=1):
		def attrRepr(obj, attrs, level=0):
			results = []
			for attr in attrs:
				results.append(('\t' * (indent + level)) + attr + ' = ' + str(getattr(obj, attr, None)))
			return '\n'.join(results)
		try:
			print '\t%s' % inspect.formatargspec(inspect.getargspec(function))
		except:
			pass
		print '\t' * indent + 'repr =', self.repr_(function)
		print '\t' * indent + 'dir =', dir(function)
		print '\t' * indent + 'class =', getattr(function, 'im_class', type(function)).__name__
		attrs = ('__class__', '__name__', '__module__', '__dict__', 'func_code')
		print attrRepr(function, attrs)
		if getattr(function, 'func_code', False):
			attrs = ('co_name', 'co_argcount', 'co_nlocals', 'co_varnames', 'co_cellvars', 'co_freevars', 'co_consts', 'co_names', 'co_stacksize', 'co_flags')
			print attrRepr(function.func_code, attrs, 1)
		attrs = ('func_closure', 'func_defaults', 'func_globals', 'func_name') #, 'func_doc'
		print attrRepr(function, attrs)

	def advise(self, method, *args, **kwargs):
		if getattr(method, 'im_class', False):
			name = type(args[0]).__name__
		elif hasattr(method, "__module__") and method.__module__ is not None:
			name = method.__module__
		else:
			name = '?'
		argStr = ', '.join([self.repr_(arg) for arg in args] + ['%s=%s' % (key, self.repr_(val)) for key, val in kwargs.items()])
		call = '%s.%s(%s)' % (name, method.__name__, argStr)
		print call
		if self.verbose:
			self.printFunctionDetails(method)
			try:
				rvalue = method(*args, **kwargs)
				print 'exec %s -> %s' % (call, rvalue)
				return rvalue
			except Exception, e:
				print 'exec %s -> %s: %s' % (call, type(e).__name__, e)
				raise
		else:
			return method(*args, **kwargs)

class FunctionResultLoggerAspect(LoggerAspect):
	# A logger aspect that can be used to wrap __getattribute__
	def advise(self, method, *args, **kwargs):
		rvalue = method(*args, **kwargs)
		print '%s returned %s' % (method.__name__, rvalue)
		if self.verbose:
			self.printFunctionDetails(rvalue)
		return rvalue

class TestAspect(Aspect):
	# Test aspect prints method signature before and after method execution
	def advise(self, method, *args, **kwargs):
		print 'TestAspect.advise checking attribute %s.exposed = %s' % (method.__name__, getattr(method, 'exposed', '<undefined>'))
		return method(*args, **kwargs)

class TestAspect2(Aspect):
	def advise(self, method, *args, **kwargs):
		newArgs = args[0:-1] + ('TestAspect2 replaced arg',)
		try:
			print "TestAspect2.advise change last arg from %s to %s" % (repr(args[-1]), repr(newArgs[-1]))
			return method(*newArgs, **kwargs)
		except Exception, e:
			print "TestAspect2.advise fall back to original args due to exception: %s: %s" % (type(e).__name__, e)
			return method(*args, **kwargs)

class Test(object):
	def __repr__(self):
		return '<Test object>'
	def __str__(self):
		return 'Test'
	def func(self, x=1):
		return x
	def func2(self, x):
		return '%s + 100' % x
	def func3(self, x):
		return x
	def _func(self, x):
		raise Exception('_func should not be wrapped')
	func.exposed = True
	func2.exposed = False

def _test():
	import doctest, aopythonexamples
	return doctest.testmod(aopythonexamples)

if __name__ == "__main__":
	_test()
