"""Unit tests for aopython module


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
import unittest, inspect
import aopython

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvisedFunctionTests(unittest.TestCase):
	"""Tests for aopython.Aspect, aopython.iswrapped, and aopython.unwrap for functions"""

	class CallCounterAspect(aopython.Aspect):
		"""Aspect that counts the number of times it advises other methods"""
		def __init__(self):
			self.advisedCalls = 0
		def advise(self, method, *args, **kwargs):
			self.advisedCalls += 1
			return method(*args, **kwargs)

	def setUp(self):
		def foo(x):
			return x + 1
		self.foo = foo
		self.bar = foo
		self.a = aopython.Aspect()
		self.bar = self.a.wrap(self.foo, allowUnwrap=True)

	def testFunctions(self):
		"""sanity check: make sure we're working with functions"""
		self.assert_(inspect.isfunction(self.foo), 'foo should be a function')
		self.assert_(inspect.isfunction(self.bar), 'bar should be a function')

	def testDetectNonwrappedFunction(self):
		"""iswrapped should return false given a function that was never wrapped"""
		self.failIf(aopython.iswrapped(self.foo), 'function should not have advice, but iswrapped returned true')

	def testDetectWrappedFunction(self):
		"""iswrapped should return True given a wrapped function"""
		self.assert_(aopython.iswrapped(self.bar), 'function should have advice, but iswrapped returned false')

	def testDetectUnwrappedFunction(self):
		"""iswrapped should return False given a function that been unwrapped"""
		func = aopython.unwrap(self.bar)
		self.failIf(aopython.iswrapped(func), 'function has advice after unwrap')

	def testFailOnUnwrapNonwrappedFunction(self):
		"""unwrap should raise aopython.MethodHasNoAdviceError given a function that is not wrapped"""
		self.assertRaises(aopython.MethodHasNoAdviceError, aopython.unwrap, self.foo)

	def testFailOnUnwrapUnwrappedFunction(self):
		"""unwrap should raise aopython.MethodHasNoAdviceError given a function that has been unwrapped"""
		func = aopython.unwrap(self.bar)
		self.assertRaises(aopython.MethodHasNoAdviceError, aopython.unwrap, func)

	def testExecuteWrappedFuncion(self):
		"""function return value should not be affected by generic Aspect advice"""
		self.assertEqual(self.foo(0), self.bar(0), 'function without advice returned a different value function with advice')
	
	def testAdviceExecution(self):
		"""advice should be executed each time an advised funtion is called"""
		a = self.CallCounterAspect()
		func = a.wrap(self.foo)
		self.assertEqual(a.advisedCalls, 0, 'CallCounterAspect.advisedCalls should be zero before first call')
		func(0)
		self.assertEqual(a.advisedCalls, 1, 'CallCounterAspect.advisedCalls should be 1 after first call')
		func(0)
		self.assertEqual(a.advisedCalls, 2, 'CallCounterAspect.advisedCalls should be 2 after second call')
		func(0)
		self.assertEqual(a.advisedCalls, 3, 'CallCounterAspect.advisedCalls should be 3 after third call')

	def testMultipleAdviceExecution(self):
		"""advice should be executed each time an advised funtion is called"""
		a = self.CallCounterAspect()
		func = a.wrap(self.foo)
		func = a.wrap(func)
		func = a.wrap(func)
		self.assertEqual(a.advisedCalls, 0, 'CallCounterAspect.advisedCalls should be zero before first call')
		func(0)
		self.assertEqual(a.advisedCalls, 3, 'CallCounterAspect.advisedCalls should be 3 after first call')
		func(0)
		self.assertEqual(a.advisedCalls, 6, 'CallCounterAspect.advisedCalls should be 6 after second call')
		func(0)
		self.assertEqual(a.advisedCalls, 9, 'CallCounterAspect.advisedCalls should be 9 after third call')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvisedInstanceMethodTests(unittest.TestCase):
	"""Tests for aopython.Aspect, aopython.iswrapped, and aopython.unwrap for instance methods"""

	class CallCounterAspect(aopython.Aspect):
		"""Aspect that counts the number of times it advises other methods"""
		def __init__(self):
			self.advisedCalls = 0
		def advise(self, method, *args, **kwargs):
			self.advisedCalls += 1
			return method(*args, **kwargs)

	class Test(object):
		def foo(self, x=1):
			return x

	def setUp(self):
		self.a = aopython.Aspect()
		self.obj = self.Test()
		self.obj.bar = self.a.wrap(self.obj.foo, allowUnwrap=True)

	def testInstanceMethods(self):
		"""sanity check: make sure we're working with instance method"""
		self.assert_(inspect.ismethod(self.obj.foo), 'foo should be an instance method')
		self.assert_(inspect.ismethod(self.obj.bar), 'bar should be an instance method')

	def testDetectNonwrappedInstanceMethod(self):
		"""iswrapped should return false given an instance method that was never wrapped"""
		self.failIf(aopython.iswrapped(self.obj.foo), 'instance method should not have advice, but iswrapped returned true')

	def testDetectWrappedInstanceMethod(self):
		"""iswrapped should return True given a wrapped instance method"""
		self.assert_(aopython.iswrapped(self.obj.bar), 'instance method should have advice, but iswrapped returned false')

	def testDetectUnwrappedInstanceMethod(self):
		"""iswrapped should return False given an instance method that been unwrapped"""
		func = aopython.unwrap(self.obj.bar)
		self.failIf(aopython.iswrapped(func), 'instance method has advice after unwrap')

	def testFailOnUnwrapNonwrappedInstanceMethod(self):
		"""unwrap should raise aopython.MethodHasNoAdviceError given an instance method that is not wrapped"""
		self.assertRaises(aopython.MethodHasNoAdviceError, aopython.unwrap, self.obj.foo)

	def testFailOnUnwrapUnwrappedInstanceMethod(self):
		"""unwrap should raise aopython.MethodHasNoAdviceError given an instance method that has been unwrapped"""
		func = aopython.unwrap(self.obj.bar)
		self.assertRaises(aopython.MethodHasNoAdviceError, aopython.unwrap, func)

	def testExecuteWrappedInstanceMethod(self):
		"""instance method return value should not be affected by generic Aspect advice"""
		self.assertEqual(self.obj.foo(0), self.obj.bar(0), 'instance method without advice returned a different value function with advice')
	
	def testAdviceExecution(self):
		"""advice should be executed each time an advised instance method is called"""
		a = self.CallCounterAspect()
		self.obj.foobar = a.wrap(self.obj.foo)
		self.assertEqual(a.advisedCalls, 0, 'CallCounterAspect.advisedCalls should be zero before first call')
		self.obj.foobar(0)
		self.assertEqual(a.advisedCalls, 1, 'CallCounterAspect.advisedCalls should be 1 after first call')
		self.obj.foobar(0)
		self.assertEqual(a.advisedCalls, 2, 'CallCounterAspect.advisedCalls should be 2 after second call')
		self.obj.foobar(0)
		self.assertEqual(a.advisedCalls, 3, 'CallCounterAspect.advisedCalls should be 3 after third call')

	def testMultipleAdviceExecution(self):
		"""advice should be executed each time an advised instance method is called"""
		a = self.CallCounterAspect()
		self.obj.foobar = a.wrap(self.obj.foo)
		self.obj.foobar = a.wrap(self.obj.foobar)
		self.obj.foobar = a.wrap(self.obj.foobar)
		self.assertEqual(a.advisedCalls, 0, 'CallCounterAspect.advisedCalls should be zero before first call')
		self.obj.foobar(0)
		self.assertEqual(a.advisedCalls, 3, 'CallCounterAspect.advisedCalls should be 3 after first call')
		self.obj.foobar(0)
		self.assertEqual(a.advisedCalls, 6, 'CallCounterAspect.advisedCalls should be 6 after second call')
		self.obj.foobar(0)
		self.assertEqual(a.advisedCalls, 9, 'CallCounterAspect.advisedCalls should be 9 after third call')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvisedClassMethodTests(unittest.TestCase):
	"""Tests for aopython.Aspect, aopython.iswrapped, and aopython.unwrap for class methods"""

	class CallCounterAspect(aopython.Aspect):
		"""Aspect that counts the number of times it advises other methods"""
		def __init__(self):
			self.advisedCalls = 0
		def advise(self, method, *args, **kwargs):
			self.advisedCalls += 1
			return method(*args, **kwargs)

	class Test(object):
		def foo(self, x=1):
			return x

	def setUp(self):
		self.a = aopython.Aspect()
		self.Test.bar = self.a.wrap(self.Test.foo, allowUnwrap=True)

	def testClassMethods(self):
		"""sanity check: make sure we're working with class methods"""
		self.assert_(inspect.ismethod(self.Test.foo), 'foo should be a method')
		self.assert_(inspect.ismethod(self.Test.bar), 'bar should be a method')

	def testDetectNonwrappedClassMethod(self):
		"""iswrapped should return false given a class method that was never wrapped"""
		self.failIf(aopython.iswrapped(self.Test.foo), 'class method should not have advice, but iswrapped returned true')

	def testDetectWrappedClassMethod(self):
		"""iswrapped should return True given a wrapped class method"""
		self.assert_(aopython.iswrapped(self.Test.bar), 'class method should have advice, but iswrapped returned false')

	def testDetectUnwrappedClassMethod(self):
		"""iswrapped should return False given a class method that been unwrapped"""
		func = aopython.unwrap(self.Test.bar)
		self.failIf(aopython.iswrapped(func), 'class method has advice after unwrap')
	
	def testVerifyNonwrappedClassMethod(self):
		"""instance method should NOT be wrapped if class method was not wrapped"""
		obj = self.Test()
		self.failIf(aopython.iswrapped(obj.foo), 'instance method is wrapped')

	def testVerifyWrappedClassMethod(self):
		"""instance method should be wrapped if class method was wrapped"""
		obj = self.Test()
		self.assert_(aopython.iswrapped(obj.bar), 'instance method is not wrapped')

	def testFailOnUnwrapNonwrappedClassMethod(self):
		"""unwrap should raise aopython.MethodHasNoAdviceError given a class method that is not wrapped"""
		self.assertRaises(aopython.MethodHasNoAdviceError, aopython.unwrap, self.Test.foo)

	def testFailOnUnwrapUnwrappedClassMethod(self):
		"""unwrap should raise aopython.MethodHasNoAdviceError given a class method that has been unwrapped"""
		func = aopython.unwrap(self.Test.bar)
		self.assertRaises(aopython.MethodHasNoAdviceError, aopython.unwrap, func)

	def testExecuteWrappedClassMethod(self):
		"""class method return value should not be affected by generic Aspect advice"""
		obj = self.Test()
		self.assertEqual(obj.foo(0), obj.bar(0), 'instance method without advice returned a different value function with advice')
	
	def testAdviceExecution(self):
		"""advice should be executed each time an advised class method is called"""
		a = self.CallCounterAspect()
		obj = self.Test()
		obj.foobar = a.wrap(obj.foo)
		self.assertEqual(a.advisedCalls, 0, 'CallCounterAspect.advisedCalls should be zero before first call')
		obj.foobar(0)
		self.assertEqual(a.advisedCalls, 1, 'CallCounterAspect.advisedCalls should be 1 after first call')
		obj.foobar(0)
		self.assertEqual(a.advisedCalls, 2, 'CallCounterAspect.advisedCalls should be 2 after second call')
		obj.foobar(0)
		self.assertEqual(a.advisedCalls, 3, 'CallCounterAspect.advisedCalls should be 3 after third call')

	def testMultipleAdviceExecution(self):
		"""advice should be executed each time an advised class method is called"""
		a = self.CallCounterAspect()
		obj = self.Test()
		obj.foobar = a.wrap(obj.foo)
		obj.foobar = a.wrap(obj.foobar)
		obj.foobar = a.wrap(obj.foobar)
		self.assertEqual(a.advisedCalls, 0, 'CallCounterAspect.advisedCalls should be zero before first call')
		obj.foobar(0)
		self.assertEqual(a.advisedCalls, 3, 'CallCounterAspect.advisedCalls should be 3 after first call')
		obj.foobar(0)
		self.assertEqual(a.advisedCalls, 6, 'CallCounterAspect.advisedCalls should be 6 after second call')
		obj.foobar(0)
		self.assertEqual(a.advisedCalls, 9, 'CallCounterAspect.advisedCalls should be 9 after third call')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WrapperAttributes(unittest.TestCase):

	def testFunctionWrapperDict(self):
		"""Test if wrapped function __dict__ is the same as that of """
		def foo(x):
			return x
		a = aopython.Aspect()
		bar = a.wrap(foo)
		bar = a.wrap(bar)
		self.assert_(foo.__dict__ is bar.__dict__)

	def testClassMethodWrapperDict(self):
		"""Call a wrapped class method"""
		class Test(object):
			def func(self, x=1):
				return x
		a = aopython.Aspect()
		Test.wfunc = a.wrap(Test.func)
		Test.wfunc = a.wrap(Test.wfunc)
		test = Test()
		self.assert_(Test.func.__dict__ is Test.wfunc.__dict__)

	def testInstanceMethodWrapperDict(self):
		"""Call a wrapped instance method"""
		class Test(object):
			def func(self, x=1):
				return x
		a = aopython.Aspect()
		test = Test()
		test.wfunc = a.wrap(test.func)
		test.wfunc = a.wrap(test.wfunc)
		self.assert_(test.func.__dict__ is test.wfunc.__dict__)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AspectBaseTestCase(unittest.TestCase):
	"""AspectBaseTestCase is the base TestCase for testing aopython.weave"""

	class Test(object):
		def func(self, x=1):
			return x
		def func2(self, x):
			return x
		def _func(self, x):
			return x
		class Nested(object):
			def func(self, x=1):
				return x
			def func2(self, x):
				return x
			def _func(self, x):
				return x

	def assertWrapped(self, func):
		"""Helper method - assert that the given function is wrapped"""
		self.assert_(aopython.iswrapped(func), "%s is NOT wrapped" % func.__name__)

	def failIfWrapped(self, func):
		"""Helper method - fail if the given function is wrapped"""
		self.failIf(aopython.iswrapped(func), "%s is wrapped" % func.__name__)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WeaveTest(AspectBaseTestCase):

	def setUp(self):
		aopython.Aspect().weave(self.Test, allowUnwrap=True)
	
	def tearDown(self):
		aopython.unweave(self.Test)

	wrapped = {
		"Test": ("func", "func2")
	}
	notwrapped = {
		"Test": ("_func", "__new__", "__init__", "__hash__", "__reduce__", "__getattribute__", None),
		"Test.Nested": ("func", "func2", "_func", "__new__", "__init__", "__hash__", "__reduce__", "__getattribute__", None)
	}

class UnweaveTest(AspectBaseTestCase):

	def setUp(self):
		aopython.Aspect().weave(self.Test, allowUnwrap=True)
		aopython.unweave(self.Test)
	
	notwrapped = {
		"Test": ("func", "func2", "_func", "__new__", "__init__", "__hash__", "__reduce__", "__getattribute__", None),
		"Test.Nested": ("func", "func2", "_func", "__new__", "__init__", "__hash__", "__reduce__", "__getattribute__", None)
	}

class WeaveTestIncludes(AspectBaseTestCase):

	def setUp(self):
		def isFunc2(funcName):
			return funcName.startswith('func2')
		aopython.Aspect().weave(self.Test, includes=("_func", isFunc2), allowUnwrap=True)

	def tearDown(self):
		aopython.unweave(self.Test)

	wrapped = {
		"Test": ("func2",)
	}
	notwrapped = {
		"Test": ("func", "_func", "__new__", "__init__", "__hash__", "__reduce__", "__getattribute__", None)
	}

class WeaveTestExcludes(AspectBaseTestCase):

	def setUp(self):
		def isFunc2(funcName):
			return funcName.startswith('func2')
		aopython.Aspect().weave(self.Test, excludes=("_func", isFunc2), allowUnwrap=True)

	def tearDown(self):
		aopython.unweave(self.Test)

	wrapped = {
		"Test": ("func",)
	}
	notwrapped = {
		"Test": ("func2", "_func", "__new__", "__init__", "__hash__", "__reduce__", "__getattribute__", None)
	}

class WeaveTestDepth(AspectBaseTestCase):

	def setUp(self):
		aopython.Aspect().weave(self.Test, depth=1, allowUnwrap=True)

	def tearDown(self):
		aopython.unweave(self.Test, depth=1)

	wrapped = {
		"Test": ("func", "func2"),
		"Test.Nested": ("func", "func2")
	}
	notwrapped = {
		"Test": ("_func", "__new__", "__init__", "__hash__", "__reduce__", "__getattribute__", None),
		"Test.Nested": ("_func", "__new__", "__init__", "__hash__", "__reduce__", "__getattribute__", None)
	}

class WeaveTestWrapWithUnderscore(AspectBaseTestCase):

	def setUp(self):
		aopython.Aspect().weave(self.Test, allowUnwrap=True, wrapIfStartsWithUnderscore=True)

	def tearDown(self):
		aopython.unweave(self.Test)

	wrapped = {
		"Test": ("func", "func2", "_func",)
	}
	notwrapped = {
		"Test": ("__new__", "__init__", "__hash__", "__reduce__", "__getattribute__", None,)
	}

class WeaveTestWrapAllCallables(AspectBaseTestCase):

	def setUp(self):
		aopython.Aspect().weave(self.Test, allowUnwrap=True, wrapIfStartsWithUnderscore=True, weaveTest=callable)

	def tearDown(self):
		aopython.unweave(self.Test)

	wrapped = {
		"Test": ("func", "func2", "_func", "__new__", "__init__", "__hash__", "__reduce__", "__getattribute__"),
		"Test.Nested": (None,)
	}
	notwrapped = {
		"Test": (None,),
		"Test.Nested": ("func", "func2", "_func", "__new__", "__init__", "__hash__", "__reduce__", "__getattribute__")
	}

class WeaveNonCallables(unittest.TestCase):
	"""Tests weave with a weaveTest that returns true for non-callable objects"""

	class Test(object):
		def __init__(self):
			self.d = ('tuple', 4, 5)

	def testWeaveNonCallable(self):
		"""Weave with a weaveTest that returns true for non-callable objects"""
		aspect = aopython.Aspect()
		obj = self.Test()
		def test(obj):
			return not callable(obj)
		self.assert_(test(obj.d), "test(obj.d) must return True")
		# Weave should raise a TypeError when weaveTest returns True for a non-callable object
		self.assertRaises(TypeError, aspect.weave, obj, weaveTest=test)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def processTests():
	"""Post-process test cases
	
	Classes with 'wrapped' or 'notwrapped' members will have tests added to
	them that check if objects/functions/methods are wrapped or not.
	
	If one of the values (not the key) in 'wrapped' or 'notwrapped' is None
	then the key will be checked instead of one of its members.
	"""

	def getMember(obj, memberName):
		if "." in memberName:
			memberName, childName = memberName.split(".", 1)
			return getMember(getattr(obj, memberName), childName)
		return getattr(obj, memberName)
	
	def createTest(testClass, testMethod, callableName, doc):
		def test(self):
			testMethod(self, getMember(testClass, callableName))
		testName = "test_" + callableName
		test.__doc__ = doc % (testClass.__name__, callableName)
		setattr(testClass, testName, test)

	def createTests(testClass, testMethod, classDict, doc):
		if classDict:
			for objName, callableNames in classDict.items():
				for callableName in callableNames:
					if callableName:
						callableName = "%s.%s" % (objName, callableName)
					else:
						callableName = objName
					createTest(testClass, testMethod, callableName, doc)

	import aopythontest
	for testClass in aopythontest.__dict__.values():
		if isinstance(testClass, type) and issubclass(testClass, AspectBaseTestCase):
			createTests(testClass, testClass.assertWrapped, getattr(testClass, "wrapped", None), "%s.%s should be wrapped")
			createTests(testClass, testClass.failIfWrapped, getattr(testClass, "notwrapped", None), "%s.%s should NOT be wrapped")

processTests()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def doctestSuite():
	"""Create a TestSuite of doctests from aopythonexamples"""
	import doctest
	try:
		import aopythonexamples
		return doctest.DocTestSuite(aopythonexamples)
	except ImportError:
		def doctestImportFailed():
			raise ImportError("Could not import aopythonexamples")
		return unittest.FunctionTestCase(doctestImportFailed)

def unittestSuite():
	"""Create a TestSuite of unittests from aopythontest"""
	import aopythontest
	allTests = unittest.TestSuite()
	for case in aopythontest.__dict__.values():
		if isinstance(case, type) and issubclass(case, unittest.TestCase):
			allTests.addTest(unittest.makeSuite(case))
	return allTests

if __name__ == "__main__":
	suite = unittest.TestSuite()
	suite.addTest(unittestSuite())
	suite.addTest(doctestSuite())
	unittest.TextTestRunner().run(suite)
