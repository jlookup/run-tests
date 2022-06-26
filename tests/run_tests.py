
import inspect


class FailedTest:
    def __init__(self, 
        test_class, filename,
        lineno, function, code_context,
        index,
    ):
        self.test_class = test_class
        self.filename = filename
        self.lineno = lineno
        self.function = function
        self.code_context = code_context
        self.index = index

    def __repr__(self) -> str:
        return (f"FAILED TEST: {self.test_class}.{self.function}\n" +
                f"  {self.filename}\n" +
                f"  line: {self.lineno}, index: {self.index}\n" +
                 "  " + "\n  ".join(self.code_context)
        )


def run_tests(raise_on_err: bool=True, *tests_to_run: str):
    """
    Runs pytest unit tests in a module
    without calling the testing framework.
    Enables easy debugging in an IDE.

    Requires pytest.
    
    All unit tests must be within a test class.
    Class name must start with 'Test'.
    Test method names must start with 'test_'. 

    See the bottom of this module for a test file template.

        :raise_on_err: Optional[bool], default True. Dictates exception behavior
            When True, errors are raised and stop execution. Good for running in debug mode.
            When False, errors fail the test and testing continues.
            Note, this does not override any error handling in the code being tested, 
            or in pytest. It is only relevant when an exception is raised that would 
            otherwise have stopped the execution.
        :*tests_to_run: str. 
            If you don't want to run all tests in the module, pass the names
            of the functions you do want to run as strings. Only those will be run.
            Setup and teardown are still run.
    """
    from sys import modules
    from inspect import isclass

    import pytest

    testcount = 0
    successcount = 0
    failcount = 0
    failed_tests = []

    mod = modules['__main__']
    mod_dir = dir(mod)

    test_classes = [
        attr for attr in mod_dir \
        if attr.startswith('Test') \
        and isclass(getattr(mod,attr))
    ]

    for test_class in test_classes:
        t = getattr(mod,test_class)()
        print(f"Gathering tests for {test_class}:")
       
        tests = [attr for attr in dir(t) if attr.startswith('test_')]
        if tests_to_run:
            tests = [test for test in tests if test in tests_to_run]
        
        for test in tests:
            testcount += 1
            print(f"  running {test}", end='')            
            try:
                getattr(t, test)()
                print('...success')
                successcount += 1
            except Exception as e:
                print('......FAIL')
                failcount += 1

                frame_info = inspect.getframeinfo(e.__traceback__.tb_next)._asdict()
                failed_test = FailedTest(test_class, **frame_info)
                failed_tests.append(failed_test)

                if raise_on_err: raise e

    success = str(successcount).rjust(5)
    fail = str(failcount).rjust(5) #if failcount else '---'
    # print('\n')
    print(f'Testing complete. Out of {testcount} tests:')
    print(f'{success} succeeded')
    print(f'{fail} failed')
    for test in failed_tests:
        # print(f'  FAILED: {test}')
        print(test)



template = """
import pytest
from sqlcmm import sqlcmd as s

class TestSqlCmd:
    qry = "select top 10 * from sys.tables"

    def test_execute_sqlcmd(self):
        # result = s.execute_sqlcmd(self.qry)
        assert True


if __name__ == '__main__':
    from run_tests import run_tests
    run_tests()
"""