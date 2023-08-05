def f(x):
    y = x or 1
    x = 1
    return y

a = None
b = a or 1
f(None)
