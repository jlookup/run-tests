

############ saving this for later in case it becomes useful ###############
class FailedTest:
    def __init__(self, 
        test_class, exc_info, filename,
        lineno, function, code_context,
        index,
    ):
        self.test_class = test_class
        self.exc_info = exc_info
        self.filename = filename
        self.lineno = lineno
        self.function = function
        self.code_context = code_context
        self.index = index

    def __repr__(self) -> str:
        # return (f"FAILED TEST: {self.test_class}.{self.function}\n" +
        #         f"  {self.filename}\n" +
        #         f"  line: {self.lineno}, index: {self.index}\n" +
        #          "  " + "\n  ".join(self.code_context) + "\n" +
        #          "  " + self.exc_info
        # )
        head =   "FAILED TEST:"
        frame = f'  File "{self.filename}", line {self.lineno}, in {self.function}'
        code =   '    ' + '\n    '.join([line.strip() for line in self.code_context])
        exc =   f'  {self.exc_info}'
        return '\n'.join([head, frame, code, exc])