## -*- coding: utf-8 -*-
################################################################
## Author : Gaël Le Mignot
## Email : gael@pilotsystems.net
################################################################

__author__ = "gael@pilotsystems.net"
__format__ = "plaintext"
__version__ = "$Id: decorators.py 9 2007-03-17 10:32:12Z gael.le-mignot $"

def cached(cache, marshaller = lambda *args, **kwargs: repr((args, kwargs))):
    """
    This is a decorator that cache results according to parameters

    The marshaller computes a key from function arguments
    """
    def decorator(func):
        def inner(*args, **kwargs):
            key = marshaller(*args, **kwargs)
            
            res = cache[key]
            if res is None:
                res = func(*args, **kwargs)
                cache[key] = res

            return res
        return inner
    return decorator

def verbose(func):
    """
    Decorator to print debug stuff - use it only on python >= 2.4
    """
    def verbose_func(self, *args, **kwargs):
        print "  " * self.level, "==> Entering: %s(*%r, **%r)" % (func.__name__, args, kwargs)
        self.level += 1
        print "  " * self.level, self.lru
        res = func(self, *args, **kwargs)
        print "  " * self.level, self.lru
        self.level -= 1
        print "  " * self.level, "==> Leaving %s: %r" % (func.__name__, res)
        return res
    return verbose_func

def synchronized(func):
    """
    Synchronize a method using internal lock object, a decorator
    """
    def inner(self, *args, **kwargs):
        """
        The inner function
        """
        self.lock.acquire()
        try:        
            return func(self, *args, **kwargs)
        finally:
            self.lock.release()
    return inner

