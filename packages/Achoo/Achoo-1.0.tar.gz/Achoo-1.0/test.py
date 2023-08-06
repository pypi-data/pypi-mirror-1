#
# Achoo. A fluent interface for testing Python objects.
# Copyright (C) 2008 Quuxo Software.
# <http://web.quuxo.com/projects/achoo>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#

"""
Unit tests for Achoo.
"""

import unittest

import achoo


# if only achoo could be used to test itself... sigh.

class TestRequiring(unittest.TestCase):
    """
    Tests for the `requiring' function.
    """

    def testRequiring(self):
        value = object()

        builder = achoo.requiring(value)

        self.failIf(not isinstance(builder, achoo.ValueAssertionBuilder))
        self.failUnlessEqual(builder.value, value)


class TestValueAssertionBuilder(unittest.TestCase):
    """
    Tests for the `ValueAssertionBuilder' class.
    """

    def testIsNot(self):
        builder = achoo.ValueAssertionBuilder(object())
        self.failUnlessEqual(True, builder.is_not.invert_sense)

    def testEqualTo(self):
        value = 'foo'
        builder = achoo.ValueAssertionBuilder(value)
        self._assertNormal(builder.equal_to, value, 'bar')

    def testEqualToInverse(self):
        value = 'foo'
        builder = achoo.ValueAssertionBuilder(value, True)
        self._assertInverse(builder.equal_to, 'bar', value)

    def testSameAs(self):
        value = ('',)
        builder = achoo.ValueAssertionBuilder(value)
        self._assertNormal(builder.same_as, value, ('',))

    def testSameAsInverse(self):
        value = ('',)
        builder = achoo.ValueAssertionBuilder(value, True)
        self._assertInverse(builder.same_as, ('',), value)

    def testIsNonePass(self):
        builder = achoo.ValueAssertionBuilder(None)
        builder.is_none()

    def testIsNonefail(self):
        # use empty list, they also eval to false
        builder = achoo.ValueAssertionBuilder([])
        self.failUnlessRaises(AssertionError, builder.is_none)

    def testIsNoneInverse(self):
        # use empty list, they also eval to false
        builder = achoo.ValueAssertionBuilder([], True)
        builder.is_none()
        self.failUnlessRaises(AssertionError, builder.is_none)

    def testIsNotNonePass(self):
        # use empty list, they also eval to false
        builder = achoo.ValueAssertionBuilder([])
        builder.is_not_none()

    def testIsNotNoneFail(self):
        builder = achoo.ValueAssertionBuilder(None)
        self.failUnlessRaises(AssertionError, builder.is_not_none)

    def testIsNotNoneInverse(self):
        builder = achoo.ValueAssertionBuilder(None, True)
        # use empty list as they also eval to false
        builder.is_not_none()
        self.failUnlessRaises(AssertionError, builder.is_not_none)

    def testIsA(self):
        value = 'foo'
        builder = achoo.ValueAssertionBuilder(value)
        self._assertNormal(builder.is_a, basestring, list)

    def testEqualToInverse(self):
        value = 'foo'
        builder = achoo.ValueAssertionBuilder(value, True)
        self._assertInverse(builder.is_a, list, basestring)

    def testLength(self):
        builder = achoo.ValueAssertionBuilder(['foo'])
        self._assertNormal(builder.length, 1, 2)

    def testLengthInverse(self):
        builder = achoo.ValueAssertionBuilder(['foo'], True)
        self._assertInverse(builder.length, 2, 1)

    def testContains(self):
        element = 'foo'
        builder = achoo.ValueAssertionBuilder([element])
        self._assertNormal(builder.contains, element, 'bar')

    def testContainsInverse(self):
        element = 'foo'
        builder = achoo.ValueAssertionBuilder([element], True)
        self._assertInverse(builder.contains, 'bar', element)

    def testIndex(self):
        element = 'foo'
        builder = achoo.ValueAssertionBuilder([element])
        builder.index(0).equal_to(element)

    def testIndexInverse(self):
        builder = achoo.ValueAssertionBuilder(object(), True)
        self.failUnlessRaises(AssertionError, builder.index, 0)

    def _assertNormal(self, method, pass_value, fail_value):
        method(pass_value)
        self.failUnlessRaises(AssertionError, method, fail_value)

    def _assertInverse(self, method, inverse_value, normal_value):
        method(inverse_value)
        method(normal_value)


class TestCalling(unittest.TestCase):
    """
    Tests for the `calling' function.
    """

    def testCalling(self):
        callabl = lambda x: x

        builder = achoo.calling(callabl)

        self.failIf(not isinstance(builder, achoo.CallableAssertionBuilder))
        self.failUnlessEqual(builder.callable, callabl)


class TestCallableAssertionBuilder(unittest.TestCase):
    """
    Tests for the `CallableAssertionBuilder' class.
    """

    def testReturnsNonePass(self):
        def callabl():
            pass

        builder = achoo.CallableAssertionBuilder(callabl)
        builder.returns_none()


    def testReturnsNoneFail(self):
        def callabl():
            return 'foo'

        builder = achoo.CallableAssertionBuilder(callabl)
        self.failUnlessRaises(AssertionError, builder.returns_none)


    def testReturns(self):
        ret = 'foo'

        def callabl():
            return ret

        builder = achoo.CallableAssertionBuilder(callabl)
        value_builder = builder.returns()

        self.failIf(not isinstance(value_builder, achoo.ValueAssertionBuilder))
        self.failUnlessEqual(value_builder.value, ret)

    def testReturnsValuePass(self):
        ret = 'foo'

        def callabl():
            return ret

        builder = achoo.CallableAssertionBuilder(callabl)
        value_builder = builder.returns(ret)

        self.failIf(not isinstance(value_builder, achoo.ValueAssertionBuilder))
        self.failUnlessEqual(value_builder.value, ret)


    def testReturnsValueFail(self):
        ret = 'foo'

        def callabl():
            return None

        builder = achoo.CallableAssertionBuilder(callabl)
        self.failUnlessRaises(AssertionError, builder.returns, ret)


    def testRaisesPass(self):
        err = ValueError()
        def callabl():
            raise err

        builder = achoo.CallableAssertionBuilder(callabl)
        value_builder = builder.raises(ValueError)

        self.failIf(not isinstance(value_builder, achoo.ValueAssertionBuilder))
        self.failUnlessEqual(value_builder.value, err)


    def testRaisesFail(self):
        def callabl():
            pass

        builder = achoo.CallableAssertionBuilder(callabl)
        self.failUnlessRaises(AssertionError, builder.raises, ValueError)


    def testPassingPositionalParameter(self):
        param = 'foo'

        def callabl(p1):
            self.failUnlessEqual(param, p1)

        builder = achoo.CallableAssertionBuilder(callabl)
        builder = builder.passing(param)
        builder = builder.returns_none()


    def testPassingKeywordParameter(self):
        param = 'foo'

        def callabl(p1=None):
            self.failUnlessEqual(param, p1)

        builder = achoo.CallableAssertionBuilder(callabl)
        builder = builder.passing(p1=param)
        builder = builder.returns_none()


    def testPassingBothParameters(self):
        param1 = 'foo'
        param2 = 'bar'

        def callabl(p1, p2=None):
            self.failUnlessEqual(param1, p1)
            self.failUnlessEqual(param2, p2)

        builder = achoo.CallableAssertionBuilder(callabl)
        builder = builder.passing(param1, p2=param2)
        builder = builder.returns_none()

