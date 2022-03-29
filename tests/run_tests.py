


def run_tests():
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
    mod = modules['__main__']
    mod_dir = dir(mod)
    test_classes = [
        attr for attr in mod_dir \
        if attr.startswith('Test') \
        and isclass(getattr(mod,attr))
    ]
    for test_class in test_classes:
        t = getattr(mod,test_class)()
        print(f"gathering tests for {test_class}:")
        tests = [attr for attr in dir(t) if attr.startswith('test_')]
        for test in tests:
            print(f"    running {test}", end='')            
            try:
                getattr(t, test)()
                print('...success')
            except Exception as e:
                print('...failed')
                raise e 