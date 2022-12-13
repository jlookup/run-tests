

# RUN-TESTS

Executes the unit tests in a module when you run the module as a script.

Enables easy debugging in IDEs like VS Code and PyCharm. Set your breakpoints and run the test module in debug mode.

## **NOTE**
This was created as an excercise to learn some of python's internals. It was not initially meant for use in production code (although I have used it without issue). 

If you're using `pytest` you can get [essentially the same behavior (plus extra options)](https://docs.pytest.org/en/7.1.x/how-to/usage.html#calling-pytest-from-python-code) by adding this at the end of your module

    if __name__ == '__main__':
        import pytest
        pytest.main([__file__])

If you're not using `pytest`, or if you want a different output format, or you just want to learn about python's internals - then read on.


### Usage 

Include this at the end of each unit test module

    if __name__ == '__main__':
        from run_tests.run_tests import run_tests
        run_tests()


Now running the module in Debug mode will execute the unit tests. You will get a printout of the tests as they're running, the results, and details about any failed tests similar to `pytest`'s.

By default, if an exception is encountered `run_tests` will catch it, fail the unit test in which it happened, and proceed to the next unit test. Error messages and tracebacks will be included in the failure report at the end. 

If you want errors to be raised immediately you can pass `raise_on_err=True`

    if __name__ == '__main__':
        from run_tests.run_tests import run_tests
        run_tests(raise_on_err=True)


As with `pytest`, this behavior does not affect any error handling in the code being tested (or in pytest). It is only relevant when an exception is encountered that would have stopped the execution. For example, this will still run as expected and return success:

    import pytest

    def test_a():
        with pytest.raises(ZeroDivisionError):
            x = 1/0 

    if __name__ == '__main__':
        from run_tests.run_tests import run_tests
        run_tests(False)


You can specify which unit tests to run by passing the test name(s) as string(s)

    def test_a():
        assert 1 = 1 

    def test_b():
        assert 1 = 0

    def test_c():
        assert 0 = 0

    if __name__ == '__main__':
        from run_tests.run_tests import run_tests
        run_tests(
            False,
            'test_a',
            'test_c',
        )   

Note that you must pass a value to `raise_on_err`, and it must be positional (don't include the arg name).


## Formatting requirements

Unit tests can be methods in a test class or functions in the module.
  - Test function/method names must start with `test_`
  - Test class names must start with `Test`


Entry point: `run_tests()`
    Args:
        raise_on_err: Optional[bool], default False. 
            Dictates exception behavior.
            When True, errors are raised and stop execution. Good for running in debug mode.
            When False, errors fail the test and testing continues.
            Note, this does not override any error handling in the code being tested, 
            or in pytest. It is only relevant when an exception is raised that would 
            otherwise have stopped the execution.
        *tests_to_run: str. 
            If you don't want to run all tests in the module, pass the names
            of the functions you do want to run as strings. Only those will be run.
            (coming soon: support for setup and teardown.)

Usage:
    ```python
    # tests/test_my_module.py
    import pytest
    from run_tests import run_tests

    import my_module

    ...
    # your pytest functions or classes 
    # eg: 
    # def test_my_function(): 
    #   expected = 1
    #   result = my_module.my_function()
    #   assert result == expected
    ...

    if __name__ == '__main__':
        
        # run everything
        run_tests()

        # or just run select tests
        # must explicitly supply raise_on_err 
        run_tests(
            raise_on_err=True,
            'test_my_function',
            'test_my_other_function',
        )
    ```
