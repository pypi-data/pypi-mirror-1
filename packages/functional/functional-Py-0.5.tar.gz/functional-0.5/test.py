import functional
import unittest
from weakref import proxy
import sys

verbose = True

class Error(Exception):
    """Base class for regression test exceptions."""

class TestFailed(Error):
    """Test failed."""

class TestSkipped(Error):
    """Test skipped.

    This can be raised to indicate that a test was deliberatly
    skipped, but not because a feature wasn't available.  For
    example, if some resource can't be used, such as the network
    appears to be unavailable, this should be raised instead of
    TestFailed.
    """

def run_suite(suite, testclass=None):
    """Run tests from a unittest.TestSuite-derived class."""
    if verbose:
        runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
    else:
        runner = BasicTestRunner()

    result = runner.run(suite)
    if not result.wasSuccessful():
        if len(result.errors) == 1 and not result.failures:
            err = result.errors[0][1]
        elif len(result.failures) == 1 and not result.errors:
            err = result.failures[0][1]
        else:
            if testclass is None:
                msg = "errors occurred; run in verbose mode for details"
            else:
                msg = "errors occurred in %s.%s" \
                      % (testclass.__module__, testclass.__name__)
            raise TestFailed(msg)
        raise TestFailed(err)

def run_unittest(*classes):
    """Run tests from unittest.TestCase-derived classes."""
    suite = unittest.TestSuite()
    for cls in classes:
        if isinstance(cls, (unittest.TestSuite, unittest.TestCase)):
            suite.addTest(cls)
        else:
            suite.addTest(unittest.makeSuite(cls))
    if len(classes)==1:
        testclass = classes[0]
    else:
        testclass = None
    run_suite(suite, testclass)

def capture(*args, **kw):
    """capture all positional and keyword arguments"""
    return args, kw

class TestPartial(unittest.TestCase):

    thetype = functional.partial

    def test_basic_examples(self):
        p = self.thetype(capture, 1, 2, a=10, b=20)
        self.assertEqual(p(3, 4, b=30, c=40),
                         ((1, 2, 3, 4), dict(a=10, b=30, c=40)))
        p = self.thetype(map, lambda x: x*10)
        self.assertEqual(p([1,2,3,4]), [10, 20, 30, 40])

    def test_attributes(self):
        p = self.thetype(capture, 1, 2, a=10, b=20)
        # attributes should be readable
        self.assertEqual(p.func, capture)
        self.assertEqual(p.args, (1, 2))
        self.assertEqual(p.keywords, dict(a=10, b=20))
        # attributes should not be writable
        if not isinstance(self.thetype, type):
            return
        self.assertRaises(TypeError, setattr, p, 'func', map)
        self.assertRaises(TypeError, setattr, p, 'args', (1, 2))
        self.assertRaises(TypeError, setattr, p, 'keywords', dict(a=1, b=2))

    def test_argument_checking(self):
        self.assertRaises(TypeError, self.thetype)     # need at least a func arg
        try:
            self.thetype(2)()
        except TypeError:
            pass
        else:
            self.fail('First arg not checked for callability')

    def test_protection_of_callers_dict_argument(self):
        # a caller's dictionary should not be altered by partial
        def func(a=10, b=20):
            return a
        d = {'a':3}
        p = self.thetype(func, a=5)
        self.assertEqual(p(**d), 3)
        self.assertEqual(d, {'a':3})
        p(b=7)
        self.assertEqual(d, {'a':3})

    def test_arg_combinations(self):
        # exercise special code paths for zero args in either partial
        # object or the caller
        p = self.thetype(capture)
        self.assertEqual(p(), ((), {}))
        self.assertEqual(p(1,2), ((1,2), {}))
        p = self.thetype(capture, 1, 2)
        self.assertEqual(p(), ((1,2), {}))
        self.assertEqual(p(3,4), ((1,2,3,4), {}))

    def test_kw_combinations(self):
        # exercise special code paths for no keyword args in
        # either the partial object or the caller
        p = self.thetype(capture)
        self.assertEqual(p(), ((), {}))
        self.assertEqual(p(a=1), ((), {'a':1}))
        p = self.thetype(capture, a=1)
        self.assertEqual(p(), ((), {'a':1}))
        self.assertEqual(p(b=2), ((), {'a':1, 'b':2}))
        # keyword args in the call override those in the partial object
        self.assertEqual(p(a=3, b=2), ((), {'a':3, 'b':2}))

    def test_positional(self):
        # make sure positional arguments are captured correctly
        for args in [(), (0,), (0,1), (0,1,2), (0,1,2,3)]:
            p = self.thetype(capture, *args)
            expected = args + ('x',)
            got, empty = p('x')
            self.failUnless(expected == got and empty == {})

    def test_keyword(self):
        # make sure keyword arguments are captured correctly
        for a in ['a', 0, None, 3.5]:
            p = self.thetype(capture, a=a)
            expected = {'a':a,'x':None}
            empty, got = p(x=None)
            self.failUnless(expected == got and empty == ())

    def test_no_side_effects(self):
        # make sure there are no side effects that affect subsequent calls
        p = self.thetype(capture, 0, a=1)
        args1, kw1 = p(1, b=2)
        self.failUnless(args1 == (0,1) and kw1 == {'a':1,'b':2})
        args2, kw2 = p()
        self.failUnless(args2 == (0,) and kw2 == {'a':1})

    def test_error_propagation(self):
        def f(x, y):
            x / y
        self.assertRaises(ZeroDivisionError, self.thetype(f, 1, 0))
        self.assertRaises(ZeroDivisionError, self.thetype(f, 1), 0)
        self.assertRaises(ZeroDivisionError, self.thetype(f), 1, 0)
        self.assertRaises(ZeroDivisionError, self.thetype(f, y=0), 1)

    def test_attributes(self):
        p = self.thetype(hex)
        try:
            del p.__dict__
        except TypeError:
            pass
        else:
            self.fail('partial object allowed __dict__ to be deleted')

    def test_weakref(self):
        f = self.thetype(int, base=16)
        p = proxy(f)
        self.assertEqual(f.func, p.func)
        f = None
        self.assertRaises(ReferenceError, getattr, p, 'func')

    def test_with_bound_and_unbound_methods(self):
        data = map(str, range(10))
        join = self.thetype(str.join, '')
        self.assertEqual(join(data), '0123456789')
        join = self.thetype(''.join)
        self.assertEqual(join(data), '0123456789')

class PartialSubclass(functional.partial):
    pass

class TestPartialSubclass(TestPartial):

    thetype = PartialSubclass

def add(a, b): return a + b
def sub(a, b): return a - b
def fail(a, b): raise RuntimeError

from functional import foldl
class Test_foldl(unittest.TestCase):
    fold_func = staticmethod(foldl)
    minus_answer = -6

    def test_bad_arg_count(self):
        try:
            self.fold_func()
        except TypeError, e:
            pass
        else:
            self.fail("Failed to raise TypeError")

    def test_bad_first_arg(self):
        try:
            self.fold_func(5, 0, [1, 2, 3])
        except TypeError, e:
            pass
        else:
            self.fail("Failed to raise TypeError")

    def test_bad_third_arg(self):
        try:
            self.fold_func(add, 0, 123)
        except TypeError, e:
            pass
        else:
            self.fail("Failed to raise TypeError")
                        
    def test_functionality_1(self):
        answer = self.fold_func(sub, 0, [1, 2, 3])
        self.assertEqual(answer, self.minus_answer)

    def test_functionality_2(self):
        self.assertEqual(self.fold_func(add, 0, []), 0)

    def test_works_with_generators(self):
        def gen():
            for i in [1, 2, 3]:
                yield i
            raise StopIteration

        answer = self.fold_func(sub, 0, gen())
        self.assertEqual(answer, self.minus_answer)
        
    def test_generators_raises_exc(self):
        def gen():
            for i in [1, 2, 3]:
                yield i
            raise RuntimeError

        try:
            list(self.fold_func(sub, 0, gen()))
        except RuntimeError:
            pass
        else:
            self.fail("Failed to raise RuntimeError")

    def test_errors_pass_through(self):
        try:
                self.fold_func(fail, 0, [1, 2, 3])
        except RuntimeError:
                pass
        else:
                self.fail("Failed to raise RuntimeError")
                        
    def test_func_not_called_for_empty_seq(self):
        self.fold_func(fail, 0, [])

    def test_seq_not_modified(self):
        seq = [1, 2, 3]
        self.fold_func(add, 0, seq)

        self.assertEqual(seq, [1, 2, 3])
                
from functional import foldr
class Test_foldr(Test_foldl):
        fold_func = staticmethod(foldr)
        minus_answer = 2
    
from functional import scanl
class Test_scanl(unittest.TestCase):
    scan_func = staticmethod(scanl)
    minus_answer = [0, -1, -3, -6]
    
    def test_no_args(self):
        try:
            self.scan_func()
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_first_arg(self):
        try:
            self.scan_func(5, 0, [1, 2, 3])
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_third_arg(self):
        try:
            self.scan_func(sub, 0, 5)
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_empty_list(self):
        answer = self.scan_func(sub, 0, [])
    
        self.assertEqual(list(answer), [0])
            
    def test_with_list(self):
        answer = self.scan_func(sub, 0, [1, 2, 3])
        
        self.assertEqual(list(answer), self.minus_answer)
        
    def test_with_generator(self):
        def gen():
            for o in [1, 2, 3]:
                yield o
            raise StopIteration
            
        answer = self.scan_func(sub, 0, gen())

        self.assertEqual(list(answer), self.minus_answer)
    
    def test_gen_raises_exc(self):
        def gen():
            for o in [1, 2, 3]:
                yield o
            raise RuntimeError
        
        try:    
            list(self.scan_func(sub, 0, gen()))
        except RuntimeError:
            pass
        else:
            self.fail("Failed to raise RuntimeError")
        
    def test_with_exception(self):
        try:
            list(self.scan_func(fail, 0, [1, 2, 3]))
        except RuntimeError:
            pass
        else:
            self.fail("Failed to raise RuntimeError")
        
    def test_func_not_called_for_empty_seq(self):
        self.scan_func(fail, 0, [])

from functional import scanr
class Test_scanr(Test_scanl):
    scan_func = staticmethod(scanr)
    minus_answer = [2, -1, 3, 0]
    
from functional import flip
class Test_flip(unittest.TestCase):
    def test_no_args(self):
        try:
            flip()
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_first_arg(self):
        try:
            flip("foo")
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test(self):
        flipped_sub = flip(sub)
        
        self.assertEqual(sub(4, 5), -1)
        self.assertEqual(flipped_sub(4, 5), 1)
        
    def test_bad_call(self):
        flipped_sub = flip(sub)
        
        try:
            flipped_sub(4)
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_all_kw(self):
        flipped_sub = flip(sub)
        
        try:
            flipped_sub(f=4, g=3)
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
        
from functional import id
class Test_id(unittest.TestCase):
    def test_no_args(self):
        try:
            id()
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test(self):
        obj = object()
        
        self.failUnless(id(obj) is obj)
            
from functional import compose
class Test_compose(unittest.TestCase):
    def test_no_args(self):
        try:
            compose()
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_first_arg(self):
        try:
            compose(5, compose)
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_second_arg(self):
        try:
            compose(compose, 5)
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test(self):
        def minus_4(a):
            return a - 4
            
        def mul_2(a):
            return a * 2
            
        f = compose(minus_4, mul_2)
        self.assertEqual(f(4), 4)
        
        f = compose(mul_2, minus_4)
        self.assertEqual(f(4), 0)

test_classes = (
        TestPartial,
        TestPartialSubclass,
        Test_foldl,
        Test_foldr,
        Test_scanl,
        Test_scanr,
        Test_flip,
        Test_id,
        Test_compose,
    )
    
suite = unittest.TestSuite()
for cls in test_classes:
    if isinstance(cls, (unittest.TestSuite, unittest.TestCase)):
        suite.addTest(cls)
    else:
        suite.addTest(unittest.makeSuite(cls))

def test_main(verbose=None):
    import sys
    run_unittest(*test_classes)

    # verify reference counting
    if verbose and hasattr(sys, "gettotalrefcount"):
        import gc
        counts = [None] * 5
        for i in xrange(len(counts)):
            run_unittest(*test_classes)
            gc.collect()
            counts[i] = sys.gettotalrefcount()
        print counts

if __name__ == '__main__':
    test_main(verbose=True)
