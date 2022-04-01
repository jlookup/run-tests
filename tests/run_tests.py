


def run_tests(raise_on_err=True, *tests_to_run):
    """
    Runs unit tests in a module
    without calling the testing framework.
    Enables easy debugging in an IDE.
    
    All unit tests must be within a test class.
    Class name must start with 'Test'.
    Test method names must start with 'test_'. 
    """
    from sys import modules
    from inspect import isclass

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
                failed_tests.append(f"{test_class}.{test}")
                if raise_on_err: raise e

    success = str(successcount).rjust(5)
    fail = str(failcount).rjust(5) #if failcount else '---'
    print(f'Testing complete. Out of {testcount} tests:')
    print(f'{success} succeeded')
    print(f'{fail} failed')
    for test in failed_tests:
        print(f'  FAILED: {test}')
