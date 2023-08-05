class A:
    def f(self, x):
        print x

a = A()
if 2:
    b = a
b.f(42)
