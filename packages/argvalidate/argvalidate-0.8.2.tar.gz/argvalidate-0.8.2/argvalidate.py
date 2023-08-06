#   Copyright (C) 2009 Stephan Peijnik (stephan@peijnik.at)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

__version__ = '0.8.2'

import os
import warnings

from new import classobj

__all__ = ['ArgvalidateException', 'DecoratorLengthException',
    'DecoratorNonKeyLengthException', 'DecoratorKeyUnspecifiedException',
    'DecoratorStackingException', 'ArgumentTypeException',
    'ArgumentLengthException', 'func_args', 'method_args', 'return_value',
    'one_of', 'type_any', 'raises_exceptions', 'warns_kwarg_as_arg']

# Check for environment variables
argvalidate_warn = 0
if 'ARGVALIDATE_WARN' in os.environ:
    argvalidate_warn_str = os.environ['ARGVALIDATE_WARN']
    try:
        argvalidate_warn = int(argvalidate_warn_str)
    except ValueError:
        pass

argvalidate_warn_kwarg_as_arg = 0
if 'ARGVALIDATE_WARN_KWARG_AS_ARG' in os.environ:
    argvalidate_warn_kwarg_as_arg_str =\
         os.environ['ARGVALIDATE_WARN_KWARG_AS_ARG']
    try:
        argvalidate_warn_kwarg_as_arg =\
            int(argvalidate_warn_kwarg_as_arg_str)
    except ValueError:
        pass

class ArgvalidateErrorException(Exception):
    """
    Base argvalidate exception.

    Used as base for all exceptions in exception mode.

    .. note::

       Do not use this exception directly. Always use ArgvalidateException
       when checking for argvalidate errors.

    """
    pass

class ArgvalidateErrorWarning(Warning):
    """
    Base argvalidate warning.

    Used as base for all warnings in warning mode.

    .. note::

       Do not use this warning directly. Always use ArgvalidateException
       when checking for argvalidate errors.

    """
    pass

if argvalidate_warn:
    ArgvalidateException = ArgvalidateErrorWarning
else:
    ArgvalidateException = ArgvalidateErrorWarning

class ArgumentLengthException(ArgvalidateException):
    """
    Exception for invalid function-call argument count.

    This exception provides the following attributes:

    * func_name
        Name of function that caused the exception to be raised
        (str, read-only).

    * expected_count
        Number of arguments that were expected (int, read-only).

    * passed_count
        Number of arguments that were passed to the function (int, read-only).
        
    """
    def __init__(self, func_name, expected_count, passed_count):
        self.func_name = func_name
        self.expected_count = expected_count
        self.passed_count = passed_count

        msg = '%s: wrong number of arguments passed to function (expected %d, got %d).' %\
            (func_name, expected_count, passed_count)
        ArgvalidateException.__init__(self, msg)

class DecoratorLengthException(ArgvalidateException):
    """
    Exception for invalid decorator argument count.

    This exception provides the following attributes:

    * func_name
        Name of function that caused the exception to be raised
        (str, read-only).

    * expected_count
        Number of arguments that were expected (int, read-only).

    * passed_count
        Number of arguments that were passed to the function (int, read-only).

    """
    def __init__(self, func_name, expected_count, passed_count):
        self.func_name = func_name
        self.expected_count = expected_count
        self.passed_count = passed_count
        msg = '%s: wrong number of arguments specified in decorator ' %\
            (func_name)
        msg += '(expected %d, got %d).' % (expected_count, passed_count)
        ArgvalidateException.__init__(self, msg)

class DecoratorNonKeyLengthException(ArgvalidateException):
    """
    Exception for invalid decorator non-keyword argument count.

    This exception provides the following attributes:

    * func_name
        Name of function that caused the exception to be raised
        (str, read-only).

    * expected_count
        Number of arguments that were expected (int, read-only).

    * passed_count
        Number of arguments that were passed to the function (int, read-only).

    """
    def __init__(self, func_name, expected_count, passed_count):
        self.func_name = func_name
        self.expected_count = expected_count
        self.passed_count = passed_count
        msg = '%s: wrong number of non-keyword arguments specified in' %\
             (func_name) 
        msg += ' decorator (expected %d, got %d).' %\
             (expected_count, passed_count)
        ArgvalidateException.__init__(self, msg)

class DecoratorKeyUnspecifiedException(ArgvalidateException):
    """
    Exception for unspecified decorator keyword argument.

    This exception provides the following attributes:

    * func_name
        Name of function that caused the exception to be raised
        (str, read-only).

    * arg_name
        Name of the keyword argument passed to the function, but not specified
        in the decorator (str, read-only).
        
    """
    def __init__(self, func_name, arg_name):
        self.func_name = func_name
        self.arg_name = arg_name
        msg = '%s: keyword argument %s not specified in decorator.' %\
            (func_name, arg_name)
        ArgvalidateException.__init__(self, msg)

class DecoratorStackingException(ArgvalidateException):
    """
    Exception for stacking a decorator with itself.

    This exception provides the following attributes:

    * func_name
        Name of function that caused the exception to be raised
        (str, read-only).

    * decorator_name
        Name of the decorator that was stacked with itself (str, read-only).

    """
    def __init__(self, func_name, decorator_name):
        self.func_name = func_name
        self.decorator_name = decorator_name
        msg = '%s: decorator %s stacked with itself.' %\
            (func_name, decorator_name)
        ArgvalidateException.__init__(self, msg)

class ArgumentTypeException(ArgvalidateException):
    """
    Exception for invalid argument type.

    This exception provides the following attributes:

    * func_name
        Name of function that caused the exception to be raised
        (str, read-only).

    * arg_name
        Name of the keyword argument passed to the function, but not specified
        in the decorator (str, read-only).

    * expected_type
        Argument type that was expected (type, read-only).

    * passed_type
        Argument type that was passed to the function (type, read-only).

    """
    def __init__(self, func_name, arg_name, expected_type, passed_type):
        self.func_name = func_name
        self.arg_name = arg_name
        self.expected_type = expected_type
        self.passed_type = passed_type
        msg = '%s: invalid argument type for %r (expected %r, got %r).' %\
            (func_name, arg_name, expected_type, passed_type)
        ArgvalidateException.__init__(self, msg)

class ReturnValueTypeException(ArgvalidateException):
    """
    Exception for invalid return value type.

    This exception provides the following attributes:

    * func_name
        Name of function that caused the exception to be raised
        (string, read-only).

    * expected_type
        Argument type that was expected (type, read-only).

    * passed_type
        Type of value returned by the function (type, read-only).

    """
    def __init__(self, func_name, expected_type, passed_type):
        self.func_name = func_name
        self.expected_type = expected_type
        self.passed_type = passed_type
        msg = '%s: invalid type for return value (expected %r, got %r).' %\
            (func_name, expected_type, passed_type)
        ArgvalidateException.__init__(self, msg)

class KWArgAsArgWarning(ArgvalidateErrorWarning):
    def __init__(self, func_name, arg_name):
        msg = '%s: argument %s is a keyword argument and was passed as a '\
            'non-keyword argument.' % (func_name, arg_name)
        ArgvalidateException.__init__(self, msg)

def __raise(exception, stacklevel=3):
    if argvalidate_warn:
        warnings.warn(exception, stacklevel=stacklevel)
    else:
        raise exception

def __check_return_value(func_name, expected_type, return_value):
    return_value_type = type(return_value)
    error = False

    if expected_type is None:
        error = False

    elif isinstance(return_value, classobj):
        if not isinstance(return_value, expected_type) and\
            not issubclass(return_value.__class__, expected_type):
                error=True
    else:
        if not isinstance(return_value, expected_type):
            error=True

    if error:
        __raise(ReturnValueTypeException(func_name, expected_type,\
             return_value_type), stacklevel=3)

def __check_type(func_name, arg_name, expected_type, passed_value,\
    stacklevel=4):
    passed_type = type(passed_value)
    error=False

    # None means the type is not checked
    if expected_type is None:
        error=False

    # Check a class
    elif isinstance(passed_value, classobj):
        if not isinstance(passed_value, expected_type) and\
            not issubclass(passed_value.__class__, expected_type):
            error=True
    
    # Check a type
    else:
        if not isinstance(passed_value, expected_type):
            error=True

    if error:
        __raise(ArgumentTypeException(func_name, arg_name, expected_type,\
            passed_type), stacklevel=stacklevel)

def __check_args(type_args, type_kwargs, start=0):
    def validate(f):
        args_func = getattr(f, '_args_stacked_func', None)
        if args_func:
            if start == 0:
                raise DecoratorStackingException(args_func.func_name,\
                     'func_args')
            elif start == 1:
                raise DecoratorStackingException(args_func.func_name,\
                     'method_args')
            else:
                raise DecoratorStackingException(args_func.func_name,\
                     'unknown; start=%d' % (start))

        func = getattr(f, '_return_value_stacked_func', f)

        func_argcount = func.func_code.co_argcount - start
        func_key_argcount = 0
        f_name = func.func_name
        
        if func.func_defaults:
            func_key_argcount = len(func.func_defaults)

        func_nonkey_argcount = func_argcount - func_key_argcount

        def __wrapper_func(*call_args, **call_kwargs):
            arg_count = (len(call_args)-start) + len(call_kwargs)

            # Check minimum argument count.
            if arg_count < func_nonkey_argcount:
                __raise(ArgumentLengthException(f_name, func_nonkey_argcount,\
                     arg_count))

            type_nonkey_argcount = len(type_args)
            type_key_argcount = len(type_kwargs.keys())
            call_nonkey_argcount = len(call_args)
            
            type_arg_count = type_nonkey_argcount + type_key_argcount

            # Check argument count of decorator.
            if type_arg_count != func_argcount:
                __raise(DecoratorLengthException(f_name, func_argcount,
                     type_arg_count))

            if type_nonkey_argcount != func_nonkey_argcount:
                __raise(DecoratorNonKeyLengthException(f_name,
                    func_nonkey_argcount, type_nonkey_argcount))

            # Check non-keyword arguments
            if type_nonkey_argcount > 0:
                for i in range(start, type_nonkey_argcount+start):
                    arg_name = func.func_code.co_varnames[i]
                    __check_type(f_name, arg_name, type_args[i-start], call_args[i])
                

            # Check keyword arguments passed as non-keyword arguments
            for i in range(type_nonkey_argcount+start, call_nonkey_argcount):
                # Try keyword arguments passed as non-keyword arguments first
                #kwarg_pos_nonkey = i + (func_nonkey_argcount-start)
                arg_name = func.func_code.co_varnames[i]
                arg_value = call_args[i]
                
                if not arg_name in type_kwargs:
                    __raise(DecoratorKeyUnspecifiedException(f_name, arg_name))
                    continue

                typ = type_kwargs[arg_name]
                __check_type(f_name, arg_name, typ, arg_value)

                if argvalidate_warn_kwarg_as_arg:
                    warnings.warn(KWArgAsArgWarning(f_name, arg_name))

            # Check keyword arguments
            for arg_name in call_kwargs.keys():
                if not arg_name in type_kwargs:
                        __raise(DecoratorKeyUnspecifiedException(f_name,\
                             arg_name))
                        continue

                typ = type_kwargs[arg_name]
                arg_value = call_kwargs[arg_name]
                __check_type(f_name, arg_name, typ, arg_value)

            return func(*call_args, **call_kwargs)

        __wrapper_func.func_name = func.func_name
        __wrapper_func._args_stacked_func = func
        return __wrapper_func
    
    return validate

def func_args(*type_args, **type_kwargs):
    """
    Decorator used for checking arguments passed to a function.

    :param type_args: type definitions of non-keyword arguments.
    :param type_kwargs: type definitions of keyword arguments.
    
    
    :raises ArgumentLengthException: Raised if the number of arguments passed
        to the function does not match the number of arguments the function
        accepts.
        
    :raises DecoratorLengthException: Raised if the number of arguments 
        specified in the decorator does not match the number of arguments the 
        function accepts.

    :raises DecoratorNonKeyLengthException: Raised if the number of non-keyword
        arguments specified in the decorator does not match the number of
        non-keyword arguments the function accepts.

    :raises DecoratorKeyLengthException: Raised if the number of keyword
        arguments specified in the decorator does not match the number of
        non-keyword arguments the function accepts.

    :raises DecoratorKeyUnspecifiedException: Raised if a keyword argument's
        type has not been specified in the decorator.

    :raises ArgumentTypeException: Raised if an argument type passed to the
        function does not match the type specified in the decorator.


    Example::

      @func_args(int, int, z_is_str_or_int=one_of(int, str))
      def my_func(x_is_int, y_is_str, z_is_str_or_int=5):
         pass
         
    """
    return __check_args(type_args, type_kwargs, start=0)

def method_args(*type_args, **type_kwargs):
    """
    Decorator used for checking arguments passed to a method.

    :param type_args: type definitions of non-keyword arguments.
    :param type_kwargs: type definitions of keyword arguments.

    :raises ArgumentLengthException: Raised if the number of arguments passed
        to the method does not match the number of arguments the method
        accepts.

    :raises DecoratorLengthException: Raised if the number of arguments
        specified in the decorator does not match the number of arguments the
        method accepts.

    :raises DecoratorNonKeyLengthException: Raised if the number of non-keyword
        arguments specified in the decorator does not match the number of
        non-keyword arguments the method accepts.

    :raises DecoratorKeyLengthException: Raised if the number of keyword
        arguments specified in the decorator does not match the number of
        non-keyword arguments the method accepts.

    :raises DecoratorKeyUnspecifiedException: Raised if a keyword argument's
        type has not been specified in the decorator.

    :raises ArgumentTypeException: Raised if an argument type passed to the
        function does not match the type specified in the decorator.

    Example::

        class MyClass:
            @method_args(int, str, z_is_str_or_int=one_of(int, str))
            def my_method(self, x_is_int, y_is_str, z_is_str_or_int=5):
                pass

    Note that the *self* parameter is automatically ignored in the check.
    """
    return __check_args(type_args, type_kwargs, start=1)

def return_value(expected_type):
    """
    Decorator used for checking the return value of a function or method.

    :param expected_type: expected type or return value

    :raises ReturnValueTypeException: Raised if the return value's type does not
        match the definition in the decorator's `expected_type` parameter.

    Example::
    
        @return_value(int)
        def my_func():
            return 5
            
    """
    def validate(f):
        return_value_func = getattr(f, '_return_value_stacked_func', None)
        if return_value_func:
            raise DecoratorStackingException(return_value_func.func_name,\
                'return_value')

        func = getattr(f, '_args_stacked_func', f)

        def __wrapper_func(*args, **kwargs):
            result = func(*args, **kwargs)
            __check_return_value(func.func_name, expected_type, result)
            return result
        
        __wrapper_func.func_name = func.func_name
        __wrapper_func._return_value_stacked_func = func
        return __wrapper_func
    return validate

class __OneOfTuple(tuple):
    def __repr__(self):
        return 'one of %r' % (tuple.__repr__(self))

# Used for readability, using a tuple alone would be sufficient.
def one_of(*args):
    """
    Simple helper function to create a tuple from every argument passed to it.

    :param args: type definitions

    A tuple can be used instead of calling this function, however, the tuple
    returned by this function contains a customized __repr__ method, which
    makes Exceptions easier to read.

    Example::

        @func_check_args(one_of(int, str, float))
        def my_func(x):
            pass
            
    """
    return __OneOfTuple(args)

def raises_exceptions():
    """
    Returns True if argvalidate raises exceptions, False if argvalidate
    creates warnings instead.

    This behaviour can be controlled via the environment variable
    :envvar:`ARGVALIDATE_WARN`.
    """
    return not argvalidate_warn

def warns_kwarg_as_arg():
    """
    Returns True if argvalidate generates warnings for keyword arguments
    passed as arguments.

    This behaviour can be controlled via the environment variable
    :envvar:`ARGVALIDATE_WARN_KWARG_AS_ARG`.
    """

# Used for readbility, using None alone would be sufficient
type_any = None
