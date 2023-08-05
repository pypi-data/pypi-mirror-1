class A:
    def f(self, x, y):
        if x == 1:
            o = y
        elif x == 2:
            o = A()
        else:
            o = self
        return o.f(x - 1, y)

class B:
    def f(self, x, y):
        print x
        return x

a = A()
b = B()
a.f(10, b)
