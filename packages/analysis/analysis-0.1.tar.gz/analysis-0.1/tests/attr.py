def f(x, v):
    x.y = v

class X:
    pass

x = X()
x.z = 1
f(X(), 3)
