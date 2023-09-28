"""Runs pytest unit tests in a module when you execute the module as a script.

Enables easy debugging in VS Code. Set your breakpoints and run the test module
in debug mode.

Unit tests can be methods in a test class or functions in the module.
Test function/method names must start with `test_`. 
Test class name must start with `Test`.

Pytest can also be run as usual. 

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
    #   asset result == expected
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
"""

import inspect
import traceback
import sys
import pathlib
from typing import Any

import direct_stdout as stdout


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
c = bcolors


def format_test_result(test, max_text_len,success=True):
    num_dots = max_text_len - len(test)
    dots = '.' * num_dots if num_dots > 1 else '' 
    if success:
        return f'{dots}...{c.GREEN}success{c.END}'
    else:
        return f'{dots}......{c.RED}FAIL{c.END}'

    
def format_failed_test_printout(test, exc, captured_stdout, locals=None):
    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)[2:]

    failed_test = (f"\n{c.RED}FAILED TEST{c.END}: {test}\n{''.join(tb)}")
    if captured_stdout:
        failed_test += f"  Captured stdout calls:\n{captured_stdout}"
    if failed_test.endswith('\n'): failed_test = failed_test[:-1]

    # frame_info = inspect.getframeinfo(e.__traceback__.tb_next)._asdict()
    # exc_info = f"{e.__class__.__name__}: {str(e)}" # can also use e.__repr__()
    # failed_test = FailedTest(test_class, exc_info, **frame_info)

    # TODO: capture and print local variables inside the test

    return failed_test


def get_local_variables():
    """Adds local variables to the log record if an exception was raised.

    The record's `exc_info` attribute is used as the indicator that an exception
    was encountered. If any variable is of type `PrefectFuture`, it is replaced
    with its underlying value.

    Args:
        record: the logging object that has been passed to a logger.

    Returns:
        A copy of `record`, unchanged if there was no exception, 
          or with an added attribute `variables` containing a dict
          of the local variables and their values in the scope where
          the record was created. 
    """
    locals: dict = None
    try:
        locals = inspect.trace()[-1][0].f_locals
    except:
        _=''
    return locals


class TestResults:
    def __init__(self):
        self.testcount: int = 0
        # self.successcount = 0
        self.failcount:int = 0
        self.failed_tests: list = []

    def print_test_summary(self):
        success = str(self.testcount - self.failcount).rjust(5)
        fail = str(self.failcount).rjust(5)
        print('\n', end='')
        print(f'Testing complete. Out of {self.testcount} tests:')
        print(f'{c.GREEN}{success}{c.END} succeeded')
        print(f'{c.RED}{fail}{c.END} failed')
        for test in self.failed_tests:
            print(test)



def run_tests(raise_on_err: bool=False, *tests_to_run: str):
    """
    Runs pytest unit tests in a module
    without calling the testing framework.
    Enables easy debugging in an IDE.

    Requires pytest.
    
    Unit tests can be methods in a test class or functions in the module.
    Test function/method names must start with 'test_'. 
    Test class name must start with 'Test'.

    See the bottom of this module for a test file template.

        :raise_on_err: Optional[bool], default False. Dictates exception behavior
            When True, errors are raised and stop execution. Good for running in debug mode.
            When False, errors fail the test and testing continues.
            Note, this does not override any error handling in the code being tested, 
            or in pytest. It is only relevant when an exception is raised that would 
            otherwise have stopped the execution.
        :*tests_to_run: str. 
            If you don't want to run all tests in the module, pass the names
            of the functions you do want to run as strings. Only those will be run.
            (coming soon: Setup and teardown are still run.)
    """
    mod = sys.modules['__main__']
    mod_name = pathlib.Path(mod.__file__).stem
    mod_dir = dir(mod)
    results = TestResults()

    # Run module-level test functions
    run_tests_in(mod_name, mod, results, tests_to_run, raise_on_err)

    # Gather and run test methods within test classes
    test_classes = [
        attr for attr in mod_dir \
        if attr.startswith('Test') \
        and inspect.isclass(getattr(mod,attr))
    ]

    for cls in test_classes:
        class_name = f"{mod_name}.{cls}"
        test_class = getattr(mod,cls)()
        run_tests_in(class_name, test_class, results, tests_to_run, raise_on_err)

    # All tests done. Print results
    results.print_test_summary()


def run_tests_in(test_class_name, test_class, test_results, 
                 tests_to_run, raise_on_err):
    print(f"\nGathering tests for {test_class_name}:")
    
    tests = [attr for attr in dir(test_class) if attr.startswith('test_')]
    if tests_to_run:
        tests = [test for test in tests if test in tests_to_run]
    
    if tests:
        max_text_len = max(map(len,tests))

    for test in tests:
        test_results.testcount += 1
        print(f"  running {test}", end='')
        stdout.switch()                        
        try:
            getattr(test_class, test)()

        except Exception as e:
            captured_printout = stdout.switch(read_stream=True)
            locals = get_local_variables()
            failed_test = format_failed_test_printout(
                test, e, captured_printout, locals
            )
            test_results.failed_tests.append(failed_test) 

            print(format_test_result(test, max_text_len, False))          
            test_results.failcount += 1
            # err = sys.exc_info()
            if raise_on_err: raise e

        else:
            stdout.switch(flush_stream=True)
            print(format_test_result(test, max_text_len))    
