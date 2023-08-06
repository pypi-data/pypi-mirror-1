#!/usr/bin/python

import sys
sys.setrecursionlimit(15000)

from tailspin.plain import tail as tailspin
from tailspin.lazy import tail as ltailspin
from tailspin.fast import tail as ctailspin
from tailspin.fastlazy import tail as cltailspin

def test(tail):
    
    @tail
    def factorial(n, acc=1):
        "calculate a factorial"
        if n == 0:
            return acc
        return factorial(n-1, n*acc)

    assert factorial(5) == 120
    
    @tail 
    def even(n): 
        if n == 0: 
            return True 
        else: 
            return odd(n-1)

    @tail 
    def odd(n): 
        if n == 0: 
            return False 
        else: 
            return even(n-1)
    
    assert odd(3)
    assert not even(3)
    assert not odd(222)
    assert even(222)

def ftime(tail,n):
    global factorial
    @tail
    def fact(n, acc=1):
        "calculate a factorial"
        if n == 0:
            return acc
        return factorial(n-1, n*acc)
    factorial = fact

    import timeit
    return timeit.Timer('factorial(%d)'%n,
                        "from __main__ import factorial").timeit(100)

if __name__ == '__main__':
    test(tailspin)
    test(ltailspin)
    test(ctailspin)
    test(cltailspin)
    test(lambda f:f)
    for n in xrange(100,3000,500):
        base = ftime(lambda f:f,n)
        print "tailspin",n,ftime(tailspin,n)/base
        print "ltailspin",n,ftime(ltailspin,n)/base
        print "ctailspin",n,ftime(ctailspin,n)/base
        print "cltailspin",n,ftime(cltailspin,n)/base
