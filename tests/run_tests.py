"""Runs pytest unit tests in a module when you execute the module as a script.

Enables easy debugging in VS Code.

Requires pytest.

Unit tests can be methods in a test class or functions in the module.
Test function/method names must start with 'test_'. 
Test class name must start with 'Test'.

Attributes:
    run_tests:

        run_tests Args:
            raise_on_err: Optional[bool], default True. 
                Dictates exception behavior.
                When True, errors are raised and stop execution. Good for running in debug mode.
                When False, errors fail the test and testing continues.
                Note, this does not override any error handling in the code being tested, 
                or in pytest. It is only relevant when an exception is raised that would 
                otherwise have stopped the execution.
            *tests_to_run: str. 
                If you don't want to run all tests in the module, pass the names
                of the functions you do want to run as strings. Only those will be run.
                (coming soon: Setup and teardown are still run.)

        run_tests Usage:
            ```python
            import pytest

            ...
            < your pytest functions or classes >
            ...

            if __name__ == '__main__':
                from run_tests import run_tests
                run_tests()
            ```

"""


import inspect
import traceback
import io 
import sys
import pathlib
from typing import Any

import pytest

__all__ = ['run_tests']

class SwitchStdout:
    orig = sys.stdout
    redir = io.StringIO()
    saved_streams = {}
    is_switched = False

    @classmethod
    def switch_stdout(cls, 
        print_stream:bool = False,
        read_stream: bool = False,
        save_stream_as: str = None,
        flush_stream: bool = False,
    ) -> Any:
        """Switches stdout between the console and the filestream override.

        Args:
          print_stream: bool, default False. When True, any currently diverted writes
            to stdout will be printed to the console.
          read_stream: bool, default False. When True, any currently diverted writes
            to stdout will be returned as a string.
          save_stream_as: str, default None. When passed, the current diverted filestream
            will be saved to the saved_streams dict, with `saved_stream_as` as the key. A new
            diverted filestream will be initialized as the new current.
          flush_stream: bool, default False. When True, the current diverted filestream
            will be dumped. A new diverted filestream will be initialized as the new current.
            Note that a flush is done automatically after print_stream, read_stream, 
            or save_stream_as.

        Returns:
            str: The contents of the diverted filestream if read_stream is True, or
            io.TextIOBase: the new value of sys.stdout

        Exceptions:


        Notes:  
            If none of the arguments are True the current diverted filestream 
              is preserved. If you are switching to the console you can switch back
              again to the diverted filestream later and continue writing to the same
              object.

            print_stream, read_stream, and save_stream_as are mutually exclusive. 
              You can only choose one. If in doubt, save the stream. You can always
              read or print it later.  
        """
        return_val = None

        if cls.is_switched:
            # TODO: create validation and Exceptions for these assertions
            assert isinstance(cls.orig, io.TextIOWrapper)
            assert isinstance(sys.stdout, io.StringIO)
            assert cls.redir == sys.stdout
            assert 1 >= sum([print_stream, read_stream, (save_stream_as != None)])
            sys.stdout = cls.orig 
            cls.is_switched = False
            if save_stream_as:
                cls.save_stream(save_stream_as)            
            elif print_stream:
                cls.print_stream()
            elif read_stream:
                # return early to avoid returning 
                # sys.stdout when saved stream is None
                return cls.read_stream()
            elif flush_stream:
                cls._flush_stream()

        else:
            assert isinstance(cls.orig, io.TextIOWrapper)
            assert (cls.orig == sys.stdout)
            sys.stdout = cls.redir
            cls.is_switched = True

        return sys.stdout

    @classmethod 
    def save_stream(cls, name):
        """Saves the current redirected stream and creates a new one.
        """
        cls.saved_streams[name] = cls.redir
        cls._renew_stream()

    @classmethod 
    def print_stream(cls, stream_name: str = None):
        """Writes stream to the console and flushes it.
        """
        cls.orig.write(cls._flush_stream(stream_name), end='')

    @classmethod 
    def read_stream(cls, stream_name: str = None):
        """Returns the contents of stream and flushes it.
        """
        return cls._flush_stream(stream_name)

    @classmethod 
    def _flush_stream(cls, stream_name: str = None):
        """Returns the contents of stream and flushes it.
        """
        if stream_name:
            stream = cls.saved_streams.pop(stream_name)
        else:
            stream = cls.redir 
            cls._renew_stream()

        content = stream.getvalue()
        return stream.getvalue()

        # stream = (cls.saved_streams.pop(stream_name)
        #           or cls.redir)
        # output = stream.getvalue()
        # if not stream_name: cls._renew_stream()
        # return output

    @classmethod 
    def _renew_stream(cls):
        """Start a fresh redirect stream.
        """
        cls.redir = io.StringIO()
        if cls.is_switched:
            assert isinstance(cls.orig, io.TextIOWrapper)
            sys.stdout = cls.redir        

switch_stdout = SwitchStdout.switch_stdout
save_stream = SwitchStdout.save_stream
print_stream = SwitchStdout.print_stream
read_stream = SwitchStdout.read_stream


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

        :raise_on_err: Optional[bool], default True. Dictates exception behavior
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
        switch_stdout()                        
        try:
            getattr(test_class, test)()

        except Exception as e:
            captured_printout = switch_stdout(read_stream=True)
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
            switch_stdout(flush_stream=True)
            print(format_test_result(test, max_text_len))    









############ saving this for later in case it becomes useful ###############
# class FailedTest:
#     def __init__(self, 
#         test_class, exc_info, filename,
#         lineno, function, code_context,
#         index,
#     ):
#         self.test_class = test_class
#         self.exc_info = exc_info
#         self.filename = filename
#         self.lineno = lineno
#         self.function = function
#         self.code_context = code_context
#         self.index = index

#     def __repr__(self) -> str:
#         # return (f"FAILED TEST: {self.test_class}.{self.function}\n" +
#         #         f"  {self.filename}\n" +
#         #         f"  line: {self.lineno}, index: {self.index}\n" +
#         #          "  " + "\n  ".join(self.code_context) + "\n" +
#         #          "  " + self.exc_info
#         # )
#         head =   "FAILED TEST:"
#         frame = f'  File "{self.filename}", line {self.lineno}, in {self.function}'
#         code =   '    ' + '\n    '.join([line.strip() for line in self.code_context])
#         exc =   f'  {self.exc_info}'
#         return '\n'.join([head, frame, code, exc])