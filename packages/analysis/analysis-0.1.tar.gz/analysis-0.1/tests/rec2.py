def f(x):
    if x <= 0:
        return 0
    else:
        return g(x)

def g(x):
    return f(x - 1)

print f(3)
