
import io 
import sys
from typing import Any


class DirectStdout:
    original_stdout = sys.stdout
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
        """Moves stdout between the console and the filestream override.

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
            or save_stream_as. If you pass flush_stream=False along with any of these
            it will be ignored. 

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
            assert isinstance(cls.original_stdout, io.TextIOWrapper)
            assert isinstance(sys.stdout, io.StringIO)
            assert cls.redir == sys.stdout
            assert 1 >= sum([print_stream, read_stream, (save_stream_as != None)])
            sys.stdout = cls.original_stdout 
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
            assert isinstance(cls.original_stdout, io.TextIOWrapper)
            assert (cls.original_stdout == sys.stdout)
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
        cls.original_stdout.write(cls._flush_stream(stream_name), end='')

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
            assert isinstance(cls.original_stdout, io.TextIOWrapper)
            sys.stdout = cls.redir        

switch = DirectStdout.switch_stdout
save_stream = DirectStdout.save_stream
print_stream = DirectStdout.print_stream
read_stream = DirectStdout.read_stream

__all__ = [
    'switch',
    'save_stream',
    'print_stream',
    'read_stream',
]
