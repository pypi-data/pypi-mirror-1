# -*- coding: utf-8 -*-

def expect_exception(*exceptions):
    """
    Decorator to make succeed tests that should raise an exception.

    Usage:
      @expect_exception(IOError)
      def test_foo_bar: pass
    """
    def decorator(test_method):
        def expect_exception_func(self):
            self.assertRaises(exceptions, lambda: test_method(self))
        return expect_exception_func
    return decorator
