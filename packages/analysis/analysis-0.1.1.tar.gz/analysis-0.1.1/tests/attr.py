def f(x, v):
    x.y = v

class X:
    pass

x = X()
x.z = 1
f(x, 3)
print x.z
print x.y
