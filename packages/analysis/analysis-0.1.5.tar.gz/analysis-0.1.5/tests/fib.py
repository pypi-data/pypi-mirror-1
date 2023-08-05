def fib(n):
    if n <= 1:
        return 1
    else:
        return fib(n - 2) + fib(n - 1)

print fib(10) # try 32 for a bigger test!
