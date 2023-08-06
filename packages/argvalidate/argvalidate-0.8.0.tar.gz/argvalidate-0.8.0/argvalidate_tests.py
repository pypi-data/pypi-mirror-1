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

import unittest

from argvalidate import method_check_args, func_check_args, one_of, type_any
from argvalidate import ArgvalidateException, LengthException
from argvalidate import ArgvalidateTypeException

loader = unittest.TestLoader()

class TestHelperClass:
    def __init__(self, x):
        self.x = 5

class ArgvalidateCommonTestCase(unittest.TestCase):
    __test__ = False

    def test00_arg_length_correct(self):
        success = True

        try:
            self.test_func(123)
        except ArgvalidateException:
            success = False

        self.assertTrue(success)

    def test01_arg_length_incorrect(self):
        success = False

        try:
            self.test_func()
        except LengthException:
            success = True

        self.assertTrue(success)

    def test02_builtin_args_correct(self):
        success = True

        try:
            self.test_func(123)
        except ArgvalidateException:
            success = False

        self.assertTrue(success)

    def test03_builtin_args_incorrect(self):
        success = False

        try:
            self.test_func('string')
        except ArgvalidateTypeException:
            success = True

        self.assertTrue(success)

    def test04_builtin_kwargs_correct(self):
        success = True

        try:
            self.test_func2(test_arg=123)
        except ArgvalidateException:
            success = False

        self.assertTrue(success)

    def test05_builtin_kwargs_incorrect(self):
        success = False

        try:
            self.test_func2(test_arg='string')
        except ArgvalidateTypeException:
            success = True

        self.assertTrue(success)

    def test06_builtin_kwarg_as_arg_correct(self):
        success = True

        try:
            self.test_func2(123)
        except ArgvalidateException:
            raise
            success = False

        self.assertTrue(success)

    def test07_builtin_kwarg_as_arg_incorrect(self):
        success = False

        try:
            self.test_func2('string')
        except ArgvalidateTypeException:
            success = True

        self.assertTrue(success)


    def test08_builtin_kwarg_mixed_correct(self):
        success = True

        try:
            self.test_func4(1, 2, test_arg='test_arg')
        except ArgvalidateException:
            raise
            success = False

        self.assertTrue(success)

    def test09_builtin_kwarg_mixed_incorrect(self):
        success = False
        try:
            self.test_func4('str', 'str', test_arg=5)
        except ArgvalidateTypeException:
            success = True

        self.assertTrue(success)

    def test10_builtin_kwarg_mixed_incorrect2(self):
        success = False
        try:
            self.test_func4(1, 'test', test_arg='test_arg')
        except ArgvalidateTypeException:
            success = True
            
        self.assertTrue(success)

    def test11_builtin_kwarg_default(self):
        success = True

        try:
            self.test_func3()
        except ArgvalidateException:
            success = False

        self.assertTrue(success)

    def test12_builtin_kwarg_mixed_default(self):
        success = True
        try:
            self.test_func5(1, y=2)
        except ArgvalidateException:
            success = False

        self.assertTrue(success)

    def test13_custom_instance_correct(self):
        success = True
        try:
            self.test_func6(TestHelperClass(8))
        except ArgvalidateException:
            success = False

        self.assertTrue(success)

    def test14_custom_instance_incorrect(self):
        success = False
        try:
            self.test_func6(int)
        except ArgvalidateTypeException:
            success = True

        self.assertTrue(success)

    def test15_custom_instance_incorrect2(self):
        success = False
        try:
            self.test_func6(object())
        except ArgvalidateTypeException:
            success = True
        self.assertTrue(success)

    def test16_ignore_type(self):
        success = True
        try:
            self.test_func7(5)
            self.test_func7('test')
        except ArgvalidateTypeException:
            success = False
        self.assertTrue(success)

    def test17_mixed_type_correct(self):
        success = True
        try:
            self.test_func8(5)
            self.test_func8('test')
        except ArgvalidateTypeException:
            success = False
        self.assertTrue(success)

    def test18_mixed_type_incorrect(self):
        success = False
        try:
            self.test_func8(0.5)
        except ArgvalidateTypeException:
            success = True
        self.assertTrue(success)

class ArgvalidateFuncTestCase(ArgvalidateCommonTestCase):
    __test__ = True
    
    def __init__(self, *args, **kwargs):
        @func_check_args(int)
        def test_func(x):
            self.assertEquals(x, 123)

        @func_check_args(test_arg=int)
        def test_func2(test_arg=1):
            self.assertEquals(test_arg, 123)

        @func_check_args(test_arg=int)
        def test_func3(test_arg=1):
            self.assertEquals(test_arg, 1)

        @func_check_args(int, y=int, test_arg=str)
        def test_func4(x, y=1, test_arg='test'):
            self.assertEquals(x, 1)
            self.assertEquals(y, 2)
            self.assertEquals(test_arg, 'test_arg')

        @func_check_args(int, y=int, test_arg=str)
        def test_func5(x, y=1, test_arg='test_arg'):
            self.assertEquals(x, 1)
            self.assertEquals(y, 2)
            self.assertEquals(test_arg, 'test_arg')

        @func_check_args(TestHelperClass)
        def test_func6(test_helper_instance):
            self.assertTrue(isinstance(test_helper_instance, TestHelperClass))

        @func_check_args(type_any)
        def test_func7(ignored_type):
            pass

        @func_check_args(one_of(str, int))
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
            @method_check_args(int)
            def test_func(self, x):
                assert_equals(x, 123)

            @method_check_args(test_arg=int)
            def test_func2(self, test_arg=1):
                assert_equals(test_arg, 123)

            @method_check_args(test_arg=int)
            def test_func3(self, test_arg=1):
                assert_equals(test_arg, 1)

            @method_check_args(int, y=int, test_arg=str)
            def test_func4(self, x, y=1, test_arg='test'):
                assert_equals(x, 1)
                assert_equals(y, 2)
                assert_equals(test_arg, 'test_arg')

            @method_check_args(int, y=int, test_arg=str)
            def test_func5(self, x, y=1, test_arg='test_arg'):
                assert_equals(x, 1)
                assert_equals(y, 2)
                assert_equals(test_arg, 'test_arg')

            @method_check_args(TestHelperClass)
            def test_func6(self, test_helper_instance):
                assert_true(isinstance(test_helper_instance, TestHelperClass))

            @method_check_args(type_any)
            def test_func7(self,ignored_type):
                pass

            @method_check_args(one_of(str, int))
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

ArgvalidateTestSuite = unittest.TestSuite(
  [ArgvalidateFuncSuite, ArgvalidateMethodSuite])
