
RUN-TESTS
=========

Executes the unit tests in a module when you run the module as a script.

Enables easy debugging in IDEs like VS Code and PyCharm. Set your breakpoints and run the test module in debug mode.

**NOTE**: ``Run-Tests`` was written as an excercise in code introspection and to learn some of python's internals. It is not currently a full-featured unit test framework. It does not have a CLI; there is no way to run your entire test suite. It is designed to execute one module, or even just one test, at a time using your IDE's Debugger. It can be used to step through and debug the function(s) being tested, or the unit tests themselves.

If you're using ``pytest`` you can get `essentially the same behavior (plus extra options)`_ by adding this to your module

.. _essentially the same behavior (plus extra options): https://docs.pytest.org/en/7.1.x/how-to/usage.html#calling-pytest-from-python-code

.. code-block:: python

    import pytest 

    # your unit tests here

    if __name__ == '__main__':
        pytest.main([__file__])

If you're not using ``pytest``, or if you want a different output format, or you just want to learn about python's internals - then read on.


Installation
------------

.. code-block:: text 

    $ pip install git+ssh://git@github.com/jlookup/run-tests.git@main


Usage
-----

There is just one public function, ``run_tests()``. It searches the module for unit tests, executes them, and prints the results. 

.. code-block:: python

    run_tests(raise_on_err: bool=False, *tests_to_run: str)

Include this at the end of each test module

.. code-block:: python

    if __name__ == '__main__':
        from run_tests import run_tests
        run_tests()


Now running the module directly or in Debug mode will execute the unit tests. You will get a printout of the tests as they're running, the results, and details about any failed tests similar to ``pytest``'s.

.. code-block:: python 

    # test_abc.py

    def test_a():
        assert 0 == 0

    def test_b():
        assert 1 == 0

    def test_c():
        assert 1 == 1

    if __name__ == '__main__':
        from run_tests import run_tests
        run_tests()

.. code-block:: text

    $ python test_abc.py 

    Gathering tests for test_abc:
      running test_a...success
      running test_b......FAIL
      running test_c...success

    Testing complete. Out of 3 tests:
        2 succeeded
        1 failed

    FAILED TEST: test_b
    File "unit_test.py", line 6, in test_b
        assert 1 == 0
    AssertionError  

By default, if an exception is encountered ``run_tests`` will catch it, fail the unit test in which it happened, and proceed to the next unit test. Error messages and tracebacks will be included in the failure report at the end. 

If you want errors to be raised immediately you can pass ``raise_on_err=True``

.. code-block:: python

    if __name__ == '__main__':
        from run_tests import run_tests
        run_tests(raise_on_err=True)

As with ``pytest``, this behavior does not affect any error handling in the code being tested (or in ``pytest`` itself). It is only relevant when an exception is encountered that would have stopped execution. For example, this will still run as expected and return success:

.. code-block:: python

    import pytest

    def test_a():
        with pytest.raises(ZeroDivisionError):
            x = 1 / 0 

    if __name__ == '__main__':
        from run_tests import run_tests
        run_tests(raise_on_err=True)

While a test is running, calls to ``stdout`` will be captured rather than printed to the console. If a test passes, the captured output is discarded. If a test fails the captured output is saved and printed as part of that test's failure report.

.. code-block:: python 

    # test_abc.py

    def test_a():
        print('running test a')    
        assert 1 == 1

    def test_b():
        print('running test b')
        assert 0 == 0

    def test_c():
        x = 0
        print('running test c')
        print(f"x: {x}")
        assert 1 == x

    if __name__ == '__main__':
        from run_tests import run_tests
        run_tests()

.. code-block:: text

    $ python test_abc.py 

    Gathering tests for test_abc:
      running test_a...success
      running test_b...success
      running test_c......FAIL

    Testing complete. Out of 3 tests:
        2 succeeded
        1 failed

    FAILED TEST: test_c
    File "unit_test.py", line 9, in test_c
        assert 1 == 0
    AssertionError  
      Captured stdout calls:
    running test c
    x: 0

You don't have to run all tests in the module. You can specify which unit tests to run by passing the test name(s) as string(s) to ``*tests_to_run``

.. code-block:: python

    # test_abc.py

    ...

    if __name__ == '__main__':
        from run_tests import run_tests
        run_tests(
            False,
            'test_a',
            'test_b',
        )   

.. code-block:: text

    $ python test_abc.py 

    Gathering tests for test_abc:
      running test_a...success
      running test_b...success

    Testing complete. Out of 2 tests:
        2 succeeded
        0 failed

Note that you must pass a value to ``raise_on_err``, and it must be positional (don't include the arg name).


Formatting requirements
-----------------------

Unit tests can be methods in a test class or functions in the module.

- Test function/method names must start with ``test_`` (eg, ``test_my_func()``)
- Test class names must start with ``Test`` (eg, ``TestMyClass``)

You can use any testing library or framework, just be sure to import it in the module and follow its rules as you normally would. You can also just use simple assert statements. 
