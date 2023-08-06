# Copyright (c) 2008 Simplistix Ltd
# See license.txt for license details.

from testfixtures import should_raise,Comparison as C
from unittest import TestCase,TestSuite,makeSuite

class TestShouldRaise(TestCase):

    def test_no_params(self):
        def to_test():
            raise ValueError('wrong value supplied')
        should_raise(to_test,ValueError('wrong value supplied'))()
    
    def test_no_exception(self):
        def to_test():
            pass
        try:
            should_raise(to_test,ValueError())()
        except AssertionError,e:
            self.assertEqual(
                e,
                C(AssertionError('None raised, ValueError() expected'))
                )
    
    def test_wrong_exception(self):
        def to_test():
            raise ValueError('bar')
        try:
            should_raise(to_test,ValueError('foo'))()
        except AssertionError,e:
            self.assertEqual(
                e,
                C(AssertionError("ValueError('bar',) raised, ValueError('foo',) expected"))
                )
    
    def test_only_exception_class(self):
        def to_test():
            raise ValueError('bar')
        should_raise(to_test,ValueError)()
    
    def test_no_supplied_or_raised(self):
        def to_test():
            pass
        s = should_raise(to_test)
        s()
        self.failUnless(s.raised is None)
        
    
    def test_args(self):
        def to_test(*args):
            raise ValueError('%s'%repr(args))
        should_raise(
            to_test,
            ValueError('(1,)')
            )(1)
    
    def test_kw_to_args(self):
        def to_test(x):
            raise ValueError('%s'%x)
        should_raise(
            to_test,
            ValueError('1')
            )(x=1)

    def test_kw(self):
        def to_test(**kw):
            raise ValueError('%r'%kw)
        should_raise(
            to_test,
            ValueError("{'x': 1}")
            )(x=1)

    def test_both(self):
        def to_test(*args,**kw):
            raise ValueError('%r %r'%(args,kw))
        should_raise(
            to_test,
            ValueError("(1,) {'x': 2}")
            )(1,x=2)

    def test_method_args(self):
        class X:
            def to_test(self,*args):
                self.args = args
                raise ValueError()
        x = X()
        should_raise(x.to_test,ValueError)(1,2,3)
        self.assertEqual(x.args,(1,2,3))
    
    def test_method_kw(self):
        class X:
            def to_test(self,**kw):
                self.kw = kw
                raise ValueError()
        x = X()
        should_raise(x.to_test,ValueError)(x=1,y=2)
        self.assertEqual(x.kw,{'x':1,'y':2})

    def test_method_both(self):
        class X:
            def to_test(self,*args,**kw):
                self.args = args
                self.kw = kw
                raise ValueError()
        x = X()
        should_raise(x.to_test,ValueError)(1,y=2)
        self.assertEqual(x.args,(1,))
        self.assertEqual(x.kw,{'y':2})

    def test_raised(self):
        def to_test():
            raise ValueError('wrong value supplied')
        s = should_raise(to_test)
        s()
        self.assertEqual(s.raised,C(ValueError('wrong value supplied')))
        

def test_suite():
    return TestSuite((
        makeSuite(TestShouldRaise),
        ))
