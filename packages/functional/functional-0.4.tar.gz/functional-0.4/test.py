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

from functional import foldl1
class Test_foldl1(unittest.TestCase):
    fold_func = staticmethod(foldl1)
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
            self.fold_func(5, [1, 2, 3])
        except TypeError, e:
            pass
        else:
            self.fail("Failed to raise TypeError")

    def test_bad_third_arg(self):
        try:
            self.fold_func(add, 123)
        except TypeError, e:
            pass
        else:
            self.fail("Failed to raise TypeError")

    def test_with_list(self):
        answer = self.fold_func(sub, [0, 1, 2, 3])
        self.assertEqual(answer, self.minus_answer)

    def test_with_singleton_list(self):
        self.assertEqual(self.fold_func(add, [0]), 0)
        
    def test_with_empty_list(self):
        try:
            self.fold_func(add, [])
        except ValueError:
            pass
        else:
            self.fail("Failed to raise ValueError")

    def test_works_with_generators(self):
        def gen():
            for i in [0, 1, 2, 3]:
                yield i
            raise StopIteration

        answer = self.fold_func(sub, gen())
        self.assertEqual(answer, self.minus_answer)

    def test_errors_pass_through(self):
        try:
            self.fold_func(fail, [0, 1, 2, 3])
        except RuntimeError:
            pass
        else:
            self.fail("Failed to raise RuntimeError")

    def test_func_not_called_for_empty_seq(self):
        self.fold_func(fail, [0])

    def test_seq_not_modified(self):
        seq = [0, 1, 2, 3]
        self.fold_func(add, seq)

        self.assertEqual(seq, [0, 1, 2, 3])
        
from functional import foldr1
class Test_foldr1(Test_foldl1):
    fold_func = staticmethod(foldr1)
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
        
    def test_func_not_called_for_empty_seq(self):
        self.scan_func(fail, 0, [])
        
from functional import scanl1
class Test_scanl1(unittest.TestCase):
    scan_func = staticmethod(scanl1)
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
            self.scan_func(5, [0, 1, 2, 3])
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_second_arg(self):
        try:
            self.scan_func(sub, 5)
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_empty_list(self):
        answer = self.scan_func(sub, [])
    
        self.assertEqual(list(answer), [])
            
    def test_with_list(self):
        answer = self.scan_func(sub, [0, 1, 2, 3])
        
        self.assertEqual(list(answer), self.minus_answer)
        
    def test_with_generator(self):
        def gen():
            for o in [0, 1, 2, 3]:
                yield o
            raise StopIteration
            
        answer = self.scan_func(sub, gen())

        self.assertEqual(list(answer), self.minus_answer)
        
    def test_func_not_called_for_empty_seq(self):
        self.scan_func(fail, [])    
        
from functional import scanr
class Test_scanr(Test_scanl):
    scan_func = staticmethod(scanr)
    minus_answer = [2, -1, 3, 0]
    
from functional import scanr1
class Test_scanr1(Test_scanl1):
    scan_func = staticmethod(scanr1)
    minus_answer = [2, -1, 3, 0]
    
from functional import repeat
class Test_repeat(unittest.TestCase):
    def test_no_args(self):
        try:
            repeat()
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_repeat(self):
        r = repeat(5)
        
        for i in range(10):
            self.assertEqual(r.next(), 5)
            
from functional import cycle
class Test_cycle(unittest.TestCase):
    def test_no_args(self):
        try:
            cycle()
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_empty_list(self):
        try:
            cycle([])
        except ValueError:
            pass
        else:
            self.fail("Failed to raise ValueError")
     
    def test_cycle(self):
        seq = [1, 2, 3]
        cyc = cycle(seq)
        
        for i in (1, 2):
            for j in seq:
                self.assertEqual(j, cyc.next())   
        
    def test_with_generator(self): 
        def gen():
            for o in [1, 2, 3]:
                yield o
        cyc = cycle(gen())
        
        for i in (1, 2):
            for j in [1, 2, 3]:
                self.assertEqual(j, cyc.next())
                
from functional import iterate
class Test_iterate(unittest.TestCase):
    def test_no_args(self):
        try:
            iterate()
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_first_arg(self):
        try:
            iterate(5, [0, 1, 2, 3])
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test(self):
        def add_5(a): return a + 5
        
        i = iterate(add_5, 0)
        for o in (0, 5, 10, 15, 20):
            self.assertEqual(i.next(), o)

from functional import take            
class Test_take(unittest.TestCase):
    def test_no_args(self):
        try:
            take()
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_first_arg(self):
        try:
            take("foo", [0, 1, 2, 3])
        except ValueError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_second_arg(self):
        try:
            take(5, 3)
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_negative_n(self):
        self.assertEqual(list(take(-2, [2, 3, 4])), [])
        
    def test_zero_n(self):
        self.assertEqual(list(take(0, [2, 3, 4])), [])
    
    def test_positive_n_1(self):
        answer = take(3, xrange(0, 12, 3))
    
        self.assertEqual(list(answer), [0, 3, 6])
        
    def test_positive_n_2(self):
        answer = take(4, [0, 1])
    
        self.assertEqual(list(answer), [0, 1])
        
from functional import drop            
class Test_drop(unittest.TestCase):
    def test_no_args(self):
        try:
            drop()
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_first_arg(self):
        try:
            drop("foo", [0, 1, 2, 3])
        except ValueError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_second_arg(self):
        try:
            drop(5, 3)
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
        
    def test_negative_n(self):
        self.assertEqual(list(drop(-2, [2, 3, 4])), [2, 3, 4])
        
    def test_zero_n(self):
        self.assertEqual(list(drop(0, [2, 3, 4])), [2, 3, 4])
    
    def test_positive_n_1(self):
        answer = drop(3, xrange(0, 12, 3))
    
        self.assertEqual(list(answer), [9])
        
    def test_positive_n_2(self):
        answer = drop(4, [0, 1])
    
        self.assertEqual(list(answer), [])
        
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

def approve(a): return True
def reject(a): return False
def approve_n(n):
    def approve(a):
        if approve.n > 0:
            approve.n -= 1
            return True
        return False
    approve.n = n
    return approve

from functional import takeWhile      
class Test_takeWhile(unittest.TestCase):
    def test_no_args(self):
        try:
            takeWhile()
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_first_arg(self):
        try:
            takeWhile("foo", [0, 1, 2, 3])
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_second_arg(self):
        try:
            takeWhile(approve, 3)
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_empty_list(self):
        self.assertEqual(list(takeWhile(approve, [])), [])
        
    def test_func_not_called_for_empty_list(self):
        self.assertEqual(list(takeWhile(fail, [])), [])
        
    def test_no_approval(self):
        self.assertEqual(list(takeWhile(reject, [2, 3, 4])), [])
    
    def test_positive_n_1(self):
        func = approve_n(3)
    
        answer = takeWhile(func, xrange(0, 24, 3))
    
        self.assertEqual(list(answer), [0, 3, 6])
        
    def test_positive_n_2(self):
        func = approve_n(4)
    
        answer = takeWhile(func, [0, 1])
    
        self.assertEqual(list(answer), [0, 1])
        
from functional import dropWhile      
class Test_dropWhile(unittest.TestCase):
    def test_no_args(self):
        try:
            dropWhile()
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_first_arg(self):
        try:
            dropWhile("foo", [0, 1, 2, 3])
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_second_arg(self):
        try:
            dropWhile(approve, 3)
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_empty_list(self):
        self.assertEqual(list(dropWhile(approve, [])), [])
        
    def test_func_not_called_for_empty_list(self):
        self.assertEqual(list(dropWhile(fail, [])), [])
        
    def test_no_approval(self):
        self.assertEqual(list(dropWhile(reject, [2, 3, 4])), [2, 3, 4])
    
    def test_positive_n_1(self):
        func = approve_n(3)
    
        answer = dropWhile(func, xrange(0, 12, 3))
    
        self.assertEqual(list(answer), [9])
        
    def test_positive_n_2(self):
        func = approve_n(4)
    
        answer = dropWhile(func, [0, 1])
    
        self.assertEqual(list(answer), [])
        
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
        
from functional import concat
class Test_concat(unittest.TestCase):
    def test_no_args(self):
        try:
            concat()
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_arg(self):
        try:
            concat(5)
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_with_empty_list(self):
        self.assertEqual(concat([]), [])
            
    def test_with_valid_list(self):
        self.assertEqual(concat([[1], [2], [3]]), [1, 2, 3])
        
    def test_with_invalid_list(self):
        try:
            concat([1, 2, 3])
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
from functional import concatMap
def double(x_xs):
    return [x_xs[0], x_xs[0]]

class Test_concatMap(unittest.TestCase):
    def test_no_args(self):
        try:
            concatMap()
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_first_arg(self):
        try:
            concat(5, [[1], [2], [3]])
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_bad_second_arg(self):
        try:
            concat(double, 5)
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
    def test_with_empty_list(self):
        self.assertEqual(concatMap(double, []), [])
        
    def test_func_not_called_for_empty_list(self):
        concatMap(fail, [])
            
    def test_with_valid_list(self):
        answer = concatMap(double, [[1], [2], [3]])
    
        self.assertEqual(answer, [1, 1, 2, 2, 3, 3])
        
    def test_with_invalid_list(self):
        try:
            concatMap(double, [1, 2, 3])
        except TypeError:
            pass
        else:
            self.fail("Failed to raise TypeError")
            
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

def test_main(verbose=None):
    import sys
    test_classes = (
        TestPartial,
        TestPartialSubclass,
        Test_foldl,
        Test_foldr,
        Test_foldl1,
        Test_foldr1,
        Test_scanl,
        Test_scanr,
        Test_scanl1,
        Test_scanr1,
        Test_repeat,
        Test_cycle,
        Test_iterate,
        Test_take,
        Test_drop,
        Test_flip,
        Test_takeWhile,
        Test_dropWhile,
        Test_id,
        Test_concat,
        Test_concatMap,
        Test_compose,
    )
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
