#!/usr/bin/env python

def fib(n):
    if n <= 1:
        return 1
    else:
        return fib(n - 2) + fib(n - 1)

print fib(10) # try 32 for a bigger test!

# vim: tabstop=4 expandtab shiftwidth=4
