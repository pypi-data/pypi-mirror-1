#   Copyright (C) 2009 Stephan Peijnik (stephan@peijnik.at)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


__version__ = '0.8.0'

from new import classobj

__all__ = ['ArgvalidateException', 'DecoratorLengthException',
    'DecoratorNonKeyLengthException', 'DecoratorKeyLengthException',
    'DecoratorKeyUnspecifiedException', 'ArgvalidateTypeException',
    'func_check_args', 'method_check_args', 'one_of', 'type_any']

class ArgvalidateException(Exception):
    pass

class LengthException(ArgvalidateException):
    def __init__(self, func_name, expected_count, passed_count):
        msg = '%s: too few arguments passed to function (expected %d, got %d).' %\
            (func_name, expected_count, passed_count)
        ArgvalidateException.__init__(self, msg)

class DecoratorLengthException(ArgvalidateException):
    def __init__(self, func_name, expected_count, passed_count):
        msg = '%s: too few arguments specified in decorator ' %\
            (func_name)
        msg += '(expected %d, got %d).' % (expected_count, passed_count)
        ArgvalidateException.__init__(self, msg)

class DecoratorNonKeyLengthException(ArgvalidateException):
    def __init__(self, func_name, expected_count, passed_count):
        msg = '%s: wrong number of non-keyword arguments specified in ' %\
             (func_name) 
        msg += ' decorator (expected %d, got %d).' %\
             (expected_count, passed_count)
        ArgvalidateException.__init__(self, msg)

class DecoratorKeyLengthException(ArgvalidateException):
    def __init__(self, func_name, expected_count, passed_count):
        msg = '%s: wrong number of keyword arguments specified in decorator ' %\
            (func_name)
        msg += '(expected %d, got %d).' % (expected_count, passed_count)
        ArgvalidateException.__init__(self, msg)

class DecoratorKeyUnspecifiedException(ArgvalidateException):
    def __init__(self, func_name, arg_name):
        msg = '%s: keyword argument %s not specified in decorator.' %\
            (func_name, arg_name)
        ArgvalidateException.__init__(self, msg)

class ArgvalidateTypeException(ArgvalidateException):
    def __init__(self, func_name, arg_name, expected_type, passed_type):
        msg = '%s: invalid argument type for %r (expected %r, got %r).' %\
            (func_name, arg_name, expected_type, passed_type)
        ArgvalidateException.__init__(self, msg)

def __check_type(func_name, arg_name, expected_type, passed_value):
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
        raise ArgvalidateTypeException(func_name, arg_name, expected_type,\
            passed_type)

def __check_args(type_args, type_kwargs, start=0):
    def validate(func):
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
                raise LengthException(f_name, func_nonkey_argcount,\
                     arg_count)

            type_nonkey_argcount = len(type_args)
            type_key_argcount = len(type_kwargs.keys())
            call_nonkey_argcount = len(call_args)
            
            type_arg_count = type_nonkey_argcount + type_key_argcount

            # Check argument count of decorator.
            if type_arg_count != func_argcount:
                raise DecoratorLengthException(f_name, func_argcount,
                     type_arg_count)

            if type_nonkey_argcount != func_nonkey_argcount:
                raise DecoratorNonKeyLengthException(f_name,
                    func_nonkey_argcount, type_nonkey_argcount)

            if type_key_argcount != func_key_argcount:
                raise DecoratorKeyLengthException(f_name, func_key_argcount,
                    type_key_argcount)

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
                    raise DecoratorKeyUnspecifiedException(f_name, arg_name)

                typ = type_kwargs[arg_name]
                __check_type(f_name, arg_name, typ, arg_value)

            # Check keyword arguments
            for arg_name in call_kwargs.keys():
                if not arg_name in type_kwargs:
                        raise DecoratorKeyUnspecifiedException(f_name, arg_name)

                typ = type_kwargs[arg_name]
                arg_value = call_kwargs[arg_name]
                __check_type(f_name, arg_name, typ, arg_value)

            return func(*call_args, **call_kwargs)

        __wrapper_func.func_name = func.func_name
        return __wrapper_func
    
    return validate

def func_check_args(*type_args, **type_kwargs):
    return __check_args(type_args, type_kwargs)

def method_check_args(*type_args, **type_kwargs):
    return __check_args(type_args, type_kwargs, start=1)

# Used for readability, using a tuple alone would be sufficient.
def one_of(*args):
    return args

# Used for readbility, using None alone would be sufficient
type_any = None
