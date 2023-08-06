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

import unittest

# Environment needs to be set-up before importing argvalidate
import os
os.environ['ARGVALIDATE_WARN'] = '0'
os.environ['ARGVALIDATE_WARN_KWARG_AS_ARG'] = '0'

from argvalidate import method_args, func_args, one_of, type_any, return_value
from argvalidate import ArgumentTypeException, ArgumentLengthException
from argvalidate import ReturnValueTypeException, DecoratorLengthException
from argvalidate import DecoratorNonKeyLengthException
from argvalidate import DecoratorKeyUnspecifiedException
from argvalidate import DecoratorStackingException

loader = unittest.TestLoader()

class TestHelperClass:
    def __init__(self, x):
        self.x = 5

class ArgvalidateLengthTestCase(unittest.TestCase):
    def test00_wrong_decorator_argument_count(self):
        @func_args(int)
        def test_func(x, y):
            pass

        self.assertRaises(DecoratorLengthException, test_func, 1, 2)

    def test01_wrong_decorator_nonkey_argument_count(self):
        @func_args(int, int)
        def test_func(x, y=5):
            pass
        self.assertRaises(DecoratorNonKeyLengthException, test_func, 1, y=2)

    def test02_unspecified_key_argument(self):
        @func_args(int, z=int)
        def test_func(x, y=5):
            pass
        self.assertRaises(DecoratorKeyUnspecifiedException, test_func, 1, y=3)


ArgvalidateLengthSuite =\
    loader.loadTestsFromTestCase(ArgvalidateLengthTestCase)

class ArgvalidateCommonTestCase(unittest.TestCase):
    __test__ = False

    def test00_arg_length_correct(self):
        try:
            self.test_func(123)
        except ArgumentTypeException, e:
            self.fail('ArgvalidateTypeException raised: %s' % (e.message))

    def test01_arg_length_incorrect(self):
        self.assertRaises(ArgumentLengthException, self.test_func)

    def test02_builtin_args_correct(self):
        try:
            self.test_func(123)
        except ArgumentTypeException, e:
            self.fail('ArgvalidateTypeException raised: %s' % (e.message))

    def test03_builtin_args_incorrect(self):
        self.assertRaises(ArgumentTypeException,self.test_func, 'string')
        
    def test04_builtin_kwargs_correct(self):
        try:
            self.test_func2(test_arg=123)
        except ArgumentTypeException, e:
            self.fail('ArgvalidateTypeException raised: %s' % (e.message))

    def test05_builtin_kwargs_incorrect(self):
        self.assertRaises(ArgumentTypeException, self.test_func2,\
             test_arg='string')

    def test06_builtin_kwarg_as_arg_correct(self):
        try:
            self.test_func2(123)
        except ArgumentTypeException, e:
            self.fail('ArgvalidateTypeException raised: %s' % (e.message))

    def test07_builtin_kwarg_as_arg_incorrect(self):
        self.assertRaises(ArgumentTypeException, self.test_func2, 'string')

    def test08_builtin_kwarg_mixed_correct(self):
        try:
            self.test_func4(1, 2, test_arg='test_arg')
        except ArgumentTypeException, e:
            self.fail('ArgvalidateTypeException raised: %s' % (e.message))

    def test09_builtin_kwarg_mixed_incorrect(self):
        self.assertRaises(ArgumentTypeException, self.test_func4, 'str',\
             'str', test_arg=5)
        
    def test10_builtin_kwarg_mixed_incorrect2(self):
        self.assertRaises(ArgumentTypeException, self.test_func4, 1,\
             'test', test_arg='test_arg')

    def test11_builtin_kwarg_default(self):
        try:
            self.test_func3()
        except ArgumentTypeException, e:
            self.fail('ArgvalidateTypeException raised: %s' % (e.message))

    def test12_builtin_kwarg_mixed_default(self):
        try:
            self.test_func5(1, y=2)
        except ArgumentTypeException, e:
            self.fail('ArgvalidateTypeException raised: %s' % (e.message))

    def test13_custom_instance_correct(self):
        try:
            self.test_func6(TestHelperClass(8))
        except ArgumentTypeException, e:
            self.fail('ArgvalidateTypeException raised: %s' % (e.message))

    def test14_custom_instance_incorrect(self):
        self.assertRaises(ArgumentTypeException, self.test_func6, int)

    def test15_custom_instance_incorrect2(self):
        self.assertRaises(ArgumentTypeException, self.test_func6, object())

    def test16_ignore_type(self):
        try:
            self.test_func7(5)
            self.test_func7('test')
        except ArgumentTypeException, e:
            self.fail('ArgvalidateTypeException raised: %s' % (e.message))

    def test17_mixed_type_correct(self):
        try:
            self.test_func8(5)
            self.test_func8('test')
        except ArgumentTypeException, e:
            self.fail('ArgvalidateTypeException raised: %s' % (e.message))

    def test18_mixed_type_incorrect(self):
        self.assertRaises(ArgumentTypeException, self.test_func8, 0.5)

class ArgvalidateFuncTestCase(ArgvalidateCommonTestCase):
    __test__ = True
    
    def __init__(self, *args, **kwargs):
        @func_args(int)
        def test_func(x):
            self.assertEquals(x, 123)

        @func_args(test_arg=int)
        def test_func2(test_arg=1):
            self.assertEquals(test_arg, 123)

        @func_args(test_arg=int)
        def test_func3(test_arg=1):
            self.assertEquals(test_arg, 1)

        @func_args(int, y=int, test_arg=str)
        def test_func4(x, y=1, test_arg='test'):
            self.assertEquals(x, 1)
            self.assertEquals(y, 2)
            self.assertEquals(test_arg, 'test_arg')

        @func_args(int, y=int, test_arg=str)
        def test_func5(x, y=1, test_arg='test_arg'):
            self.assertEquals(x, 1)
            self.assertEquals(y, 2)
            self.assertEquals(test_arg, 'test_arg')

        @func_args(TestHelperClass)
        def test_func6(test_helper_instance):
            self.assertTrue(isinstance(test_helper_instance, TestHelperClass))

        @func_args(type_any)
        def test_func7(ignored_type):
            pass

        @func_args(one_of(str, int))
        def test_func8(str_or_int):
            self.assertTrue(isinstance(str_or_int, (str, int)))

        self.test_func = test_func
        self.test_func2 = test_func2
        self.test_func3 = test_func3
        self.test_func4 = test_func4
        self.test_func5 = test_func5
        self.test_func6 = test_func6
        self.test_func7 = test_func7
        self.test_func8 = test_func8

        ArgvalidateCommonTestCase.__init__(self, *args, **kwargs)

ArgvalidateFuncSuite = loader.loadTestsFromTestCase(ArgvalidateFuncTestCase)

class ArgvalidateMethodTestCase(ArgvalidateCommonTestCase):
    __test__ = True
    
    def __init__(self, *args, **kwargs):
        assert_equals = self.assertEquals
        assert_true = self.assertTrue

        class TestClass(object):
            @method_args(int)
            def test_func(self, x):
                assert_equals(x, 123)

            @method_args(test_arg=int)
            def test_func2(self, test_arg=1):
                assert_equals(test_arg, 123)

            @method_args(test_arg=int)
            def test_func3(self, test_arg=1):
                assert_equals(test_arg, 1)

            @method_args(int, y=int, test_arg=str)
            def test_func4(self, x, y=1, test_arg='test'):
                assert_equals(x, 1)
                assert_equals(y, 2)
                assert_equals(test_arg, 'test_arg')

            @method_args(int, y=int, test_arg=str)
            def test_func5(self, x, y=1, test_arg='test_arg'):
                assert_equals(x, 1)
                assert_equals(y, 2)
                assert_equals(test_arg, 'test_arg')

            @method_args(TestHelperClass)
            def test_func6(self, test_helper_instance):
                assert_true(isinstance(test_helper_instance, TestHelperClass))

            @method_args(type_any)
            def test_func7(self,ignored_type):
                pass

            @method_args(one_of(str, int))
            def test_func8(self, str_or_int):
                assert_true(isinstance(str_or_int, (str, int)))

        instance = TestClass()
        self.test_func = instance.test_func
        self.test_func2 = instance.test_func2
        self.test_func3 = instance.test_func3
        self.test_func4 = instance.test_func4
        self.test_func5 = instance.test_func5
        self.test_func6 = instance.test_func6
        self.test_func7 = instance.test_func7
        self.test_func8 = instance.test_func8
        
        ArgvalidateCommonTestCase.__init__(self, *args, **kwargs)

ArgvalidateMethodSuite = loader.loadTestsFromTestCase(ArgvalidateMethodTestCase)

class ArgvalidateReturnValueTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        @return_value(int)
        def test_func(var):
            return var

        self.test_func = test_func
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test00_return_value_correct(self):
        try:
            self.test_func(5)
        except ReturnValueTypeException, e:
            self.fail('ReturnValueTypeException raised: %s' % (e.message))


    def test01_return_value_incorrect(self):
        self.assertRaises(ReturnValueTypeException, self.test_func, 'test')

ArgvalidateReturnValueSuite =\
     loader.loadTestsFromTestCase(ArgvalidateReturnValueTestCase)

class ArgvalidateStackingCase(unittest.TestCase):
    def test00_stacking_return_value_first(self):
        try:
            @return_value(int)
            @func_args(str)
            def test_func(data):
                return 1

            class A(object):
                @return_value(int)
                @method_args(str)
                def test_func(self, data):
                    return 1

            test_func('test')
            A().test_func('test')
        except DecoratorStackingException, e:
            self.fail('DecoratorStackingException raised: %s' % (e.message))

    def test01_stacking_args_first(self):
        try:
            @func_args(str)
            @return_value(int)
            def test_func(data):
                return 1

            class A(object):
                @method_args(str)
                @return_value(int)
                def test_func(self, data):
                    return 1

            test_func('test')
            A().test_func('test')
        except DecoratorStackingException, e:
            self.fail('DecoratorStackingException raised: %s' % (e.message))

    def test02_stacking_args_invalid(self):
        try:
            @func_args(str)
            @func_args(str)
            def test_func(data):
                return data

            self.fail('DecoratorStackingException not raised for double'+\
                 ' func_args decorator.')
        except DecoratorStackingException:
            pass

        try:
            class A(object):
                @method_args(str)
                @method_args(str)
                def test_func(self, data):
                    return data

            self.fail('DecoratorStackingException not raised for double'+\
                ' method_args decorator.')
        except DecoratorStackingException:
            pass

    def test03_stacking_return_value_invalid(self):
        try:
            @return_value(int)
            @return_value(int)
            def test_func():
                return 5
            self.fail('DecoratorStackingException not raised for double'+\
                ' return_value decorator.')
        except DecoratorStackingException:
            pass

ArgvalidateStackingSuite = loader.loadTestsFromTestCase(ArgvalidateStackingCase)

ArgvalidateTestSuite = unittest.TestSuite(
  [ArgvalidateFuncSuite, ArgvalidateMethodSuite, ArgvalidateReturnValueSuite,
  ArgvalidateLengthSuite, ArgvalidateStackingSuite])
