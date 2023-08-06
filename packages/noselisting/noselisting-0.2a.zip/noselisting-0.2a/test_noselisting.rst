    >>> import os

    >>> from nose.plugins.plugintest import run_buffered as run
    >>> import nose.plugins.doctests

    >>> import noselisting

    >>> support = os.path.join(os.path.dirname(__file__), "test-support")

Doctests, test functions, test methods, and unittest.TestCase test
methods are listed.

    >>> run(argv=["nosetests", "--list-test-names", "--with-doctest",
    ...           os.path.join(support, "simple")],
    ...     plugins=[noselisting.TestListingPlugin(),
    ...              nose.plugins.doctests.Doctest()])
    Doctest: module
    Doctest: module.Class
    Doctest: module.function
    test (test.TestCase)
    test.TestClass.test
    test.test_function
    <BLANKLINE>
    ----------------------------------------------------------------------
    Ran 0 tests in ...s
    <BLANKLINE>
    OK


--list-long-test-names gives unambiguous absolute paths

    >>> run(argv=["nosetests", "--list-long-test-names", "--with-doctest",
    ...           os.path.join(support, "simple")],
    ...     plugins=[noselisting.TestListingPlugin(),
    ...              nose.plugins.doctests.Doctest()])
    test-support/simple/module.py
    test-support/simple/module.py:Class
    test-support/simple/module.py:function
    test-support/simple/test.py:TestCase.test
    test-support/simple/test.py:TestClass.test
    test-support/simple/test.py:test_function
    <BLANKLINE>
    ----------------------------------------------------------------------
    Ran 0 tests in ...s
    <BLANKLINE>
    OK


If a fixture raises an exception, the tests in the context of that
fixture are still listed.

    >>> run(argv=["nosetests", "--list-test-names", "--with-doctest",
    ...     os.path.join(support, "badfixtures")],
    ...     plugins=[noselisting.TestListingPlugin(),
    ...              nose.plugins.doctests.Doctest()])
    test (test.TestCase)
    test.TestClass.test
    test.test_function
    Doctest: testdoctests.TestClass
    Doctest: testdoctests.TestClass.test
    Doctest: testdoctests.test_function
    <BLANKLINE>
    ----------------------------------------------------------------------
    Ran 0 tests in ...s
    <BLANKLINE>
    OK
