AOPython change log

1.0.3
- Removed re/sre weave test from aopythonexamples (it didn't pass on Python 2.4 and it wasn't a good test).
- Improved Aspect.wrap() function
- Updated copywrite dates
- Added setup.py

1.0.2
- API CHANGE: renamed "maxWeaveDepth" parameter of weave function/method to "depth"
- API CHANGE: rearranged "weave" parameters (hopefully handier and more logical now--least likely to be used are now at the end)
- API CHANGE: replaced "weave" flags "wrapMethodWrappers" and "wrapBuiltIns" with "weaveTest", a function that overrides the normal function/method test when specified.
- Aspect.wrap can now wrap any callable object instead of just methods and functions (this fixed a few bugs where objects could be wrapped using wrap but not useing weave).
- Improved Aspect.wrap handling of class objects--it's not perfect yet, but at least classes can be wrapped.
- Added unweave function (weave is to unweave as wrap is to unwrap).
- Added a LOT more tests--weave (and unweave) are now tested more thoroughly.
- Changed aopythonexamples to use doctest (they're actually tests that run with aopythontest now, which is what I intended all along...yay!)
- Improved documentation.
- Changed whitespace to be more consistent with python style (PEP-0008). Keeping tabs and methodNameConvention for now.

1.0.1
- API CHANGE: Changed argument order of weave function: weave(aspects, object, includes...) seems more logical than weave(object, aspects, includes...) since Aspect now has a weave method with that argument order.
- Removed "dangerous method name" check from Aspect.wrap. Rare cases may exist in which those methods may need to be wrapped. Not to mention it's more consistent with the Zen of Python.
- Switched from using types.MethodType to __get__(instance, class) to create methods from functions. The tests seem to run a tiny bit faster, so it may improve performance (probably not).
- Minor code cleanup.
- Minor improvements to documentation.
- Reorganized the aopython module (moved internal functions to the bottom, etc.).
- Added __version__ and __all__ variables to aopython.
- Renamed unwrapDict to _unwrapDict.

1.0
- Initial release
