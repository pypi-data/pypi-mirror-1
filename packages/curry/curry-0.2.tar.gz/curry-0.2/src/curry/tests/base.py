from time import time

import sys
import unittest
import doctest
import examples
import textwrap
import StringIO
import cPickle
import random
import curry
import logging

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

try:
    import pickletools
except ImportError:
    logging.warn("The ``pickletools`` module is not available.")
    pickletools = None

def report_stat(data):
    sys.stderr.write("%s - " % data)

def timing(func, *args, **kwargs):
    t1 = t2 = time()
    i = 0
    while t2 - t1 < 0.5:
        result = func(*args, **kwargs)
        i += 1
        t2 = time()
    return result, float(100*(t2-t1))/i

class Dummy(object):
    """Object to hang a dictionary (state) on; also performs recursive
    comparison that takes self-referentiality into account."""

    marker = object()
    seen = set()
    
    def __eq__(self, other):
        if other in self.seen:
            return True
        self.seen.add(other)
        for name, value in self.__dict__.items():
            if value is self:
                continue
            if value != getattr(other, name, self.marker):
                return False
        self.seen.remove(other)
        return True

class TestExamples(unittest.TestCase):
    """Examples.

    This suite tests a number of example-classes with and without the
    use of the library. If the return-values of are equal, the test
    passes.

    As part of the output, a benchmark value is printed, giving some
    indication of the performance gain.
    """

    def decorator(func):
        def test(self):
            method, args = func(self)
            cooked = curry.cook(method)
            try:
                sys.stdout = StringIO.StringIO()
                result1, t1 = timing(method, *args)
                result2, t2 = timing(cooked, *args)

                # if the result is trivial, grab result from standard
                # output instead
                if result1 is None:
                    sys.stdout = StringIO.StringIO()
                    method(*args)
                    result1 = sys.stdout.getvalue()
                    sys.stdout = StringIO.StringIO()
                    cooked(*args)
                    result2 = sys.stdout.getvalue()
            finally:
                sys.stdout = sys.__stdout__

            self.assertEqual(
                result1, result2,
                "%s: %s != %s." % (
                    method.im_class.__name__, repr(result1), repr(result2)))

            report_stat("%.1f%%" % (100*t2/t1))
        test.__doc__ = func.__doc__
        return test

    @decorator
    def testIndex(self):
        """Example: Index"""

        return examples.Index("Lorem ipsum dolor sit amet.").search, ("ipsum",)

    @decorator
    def testTemplate(self):
        """Example: Template"""

        return examples.Template("Hello ${context}!").render, ("world",)

    @decorator
    def testInterpreter(self):
        """Example: Interpreter"""

        source = """\
        dummy = 'abc'
        print dummy
        """
        
        return examples.Interpreter(textwrap.dedent(source)).execute, ()

class TestTransformer(unittest.TestCase):
    """Functional tests.

    These are somewhat inexhaustive, e.g. test one binary operator
    overload, you've tested them all (which is simply not the case,
    especially because Python does not map operators to methods
    directly).
    """
    
    class Dummy(object):
        _dict = {'dummy': 42, 42: 42}
        _int = 42
        _str = 'dummy'

        def __add__(self, other):
            return self._int + other

        def __getitem__(self, other):
            return self._int + other

        def test_augassign(self, test):
            dummy = self._int
            dummy += self._int
            dummy += test
            return dummy
            
        def test_binops(self, test):
            left = self._int
            right = self._int / 2
            left = left + right
            left = left - right ** left
            left = left / right
            left = left * right
            left = left // right
            left = left % right
            left = left << right >> left | left & right ^ left
            return left + test

        def test_binop_override(self, test):
            result1 = self + self._int
            result2 = self + test
            return result1 + result2

        def test_call(self, test):
            result1 = self.test_slicing(1)
            result2 = self.test_slicing(test)
            dummy = test + len(result1) + len(result2)
            return dummy

        def test_closure(self, test):
            foo = self._int
            def closure(bar, foo=foo):
                boo = foo + self._int
                foo = bar + foo + boo
                return foo + test
            return closure(test)

        def test_for_loop(self, test):
            dummy = test
            for i in range(4):
                dummy = dummy + test
            else:
                dummy = dummy + test
            for i in range(4):
                if i > 2:
                    continue
                dummy = dummy + test
            for i in range(4):
                dummy = dummy + test
                if i < 2:
                    break
            return dummy

        def test_print(self, test):
            print test + self._int
            
        def test_slicing(self, test):
            return [self._int, self._int*2, 3, 4][1:][:-1:1][test:]

        def test_slicing_override(self, test):
            return self[test] + test

        def test_subscript(self, test):
            _dict = self._dict
            dummy = self._dict['dummy']
            dummy = dummy + _dict[test] + _dict[self._str]
            return dummy

        def test_unops(self, test):
            result1 = ~self._int
            result2 = +self._int
            result3 = -self._int
            result4 = not self._int
            return result1, result2, result3, result4

        def test_while_loop(self, test):
            dummy = test
            counter = 4
            while counter > 0:
                counter = counter - 1
                dummy = dummy + test
            else:
                dummy = dummy + test
            counter = 8
            while True:
                counter = counter - 1
                dummy = dummy + test
                if counter < 4:
                    break
            counter = 4
            while counter > 0:
                counter = counter - 1
                if counter > 2:
                    continue
                dummy = dummy + test
            while dummy > 0:
                dummy = dummy - 1
                counter = counter + 1
            return counter + dummy

    dummy = Dummy()

    def decorator(func):
        def test(self):
            bound_method, args = func(self)
            cooked = curry.cook(bound_method)

            try:
                sys.stdout = StringIO.StringIO()
                result1 = bound_method(*args)
                result2 = cooked(*args)

                # if the result is trivial, grab result from standard
                # output instead
                if result1 is None:
                    sys.stdout = StringIO.StringIO()
                    bound_method(*args)
                    result1 = sys.stdout.getvalue()
                    sys.stdout = StringIO.StringIO()
                    cooked(*args)
                    result2 = sys.stdout.getvalue()
            finally:
                sys.stdout = sys.__stdout__

            self.assertEqual(
                result1, result2, "Cooked result (%s) != expected (%s)." % (
                    result1, result2))
        test.__doc__ = func.__doc__
        return test

    @decorator
    def testAugAssign(self):
        """Functional: Augmenting assignment"""

        return self.dummy.test_augassign, (42,)

    @decorator
    def testBinaryOperators(self):
        """Functional: Binary operators"""

        return self.dummy.test_binops, (42,)

    @decorator
    def testBinaryOperatorOverride(self):
        """Functional: Binary operator override"""

        return self.dummy.test_binop_override, (42,)

    @decorator
    def testClosure(self):
        """Functional: Closure"""

        return self.dummy.test_closure, (42,)

    @decorator
    def testForLoop(self):
        """Functional: For-loop"""

        return self.dummy.test_for_loop, (1,)

    @decorator
    def testFunctionCall(self):
        """Functional: Function call"""

        return self.dummy.test_call, (1,)

    @decorator
    def testSubscript(self):
        """Functional: Subscript"""

        return self.dummy.test_subscript, (42,)

    @decorator
    def testSlicing(self):
        """Functional: Slicing"""

        return self.dummy.test_slicing, (1,)

    @decorator
    def testSlicingOverride(self):
        """Functional: Slicing override"""

        return self.dummy.test_slicing_override, (1,)

    @decorator
    def testUnaryOperators(self):
        """Functional: Unary operators"""

        return self.dummy.test_unops, (42,)

    @decorator
    def testWhileLoop(self):
        """Functional: While-loop"""

        return self.dummy.test_while_loop, (42,)

    @decorator
    def testPrint(self):
        """Functional: Print"""

        return self.dummy.test_print, (42,)

class TestPickling(unittest.TestCase):
    """Test pickling functionality."""

    words = set()
    while len(words) < 1000:
        words.add("".join(
            random.choice("abcdefghijklmnopqrstuvwxyz") 
            for i in range(random.randint(1, 10))))
    words = list(words)
    
    def decorator(func):
        def test(self):
            obj = func(self)

            p_cpickle = cPickle.dumps(obj, -1)
            p_curry = curry.dumps(obj)

            if pickletools:
                p_cpickle = pickletools.optimize(p_cpickle)

            # benchmark (load)
            result1, t1 = timing(cPickle.loads, p_cpickle)
            result2, t2 = timing(curry.loads, p_curry)

            # unpickle, repickle and compare size
            unpickled = curry.loads(p_curry)
            self.assertEqual(
                unpickled, obj,
                "Object state changed during pickle.")

            report_stat("%.1f%%" % (100*t2/t1))
        test.__doc__ = func.__doc__
        return test

    @decorator
    def testMutableSubobjects10(self):
        """Pickle: 50 sets with 20 strings each."""

        dummy = Dummy()
        for i in range(50):
            value = set((random.choice(self.words) for j in range(20)))
            setattr(dummy, random.choice(self.words), value)
        return dummy

    @decorator
    def testSelfReferential1(self):
        """Pickle: 1 reference to self."""

        dummy = Dummy()
        dummy.self = dummy
        return dummy

    @decorator
    def testSelfReferential(self):
        """Pickle: 10 references to self."""

        dummy = Dummy()
        dummy.self = (dummy,) * 10
        return dummy

    @decorator
    def testStrings10(self):
        """Pickle: 10 strings"""

        dummy = Dummy()
        for i in range(10):
            setattr(dummy, random.choice(self.words), random.choice(self.words))
        return dummy

    @decorator
    def testStrings100(self):
        """Pickle: 100 strings"""

        dummy = Dummy()
        for i in range(100):
            setattr(dummy, random.choice(self.words), random.choice(self.words))
        return dummy

    @decorator
    def testStrings1000(self):
        """Pickle: 1000 strings"""

        dummy = Dummy()
        for i in range(1000):
            setattr(dummy, random.choice(self.words), random.choice(self.words))
        return dummy
