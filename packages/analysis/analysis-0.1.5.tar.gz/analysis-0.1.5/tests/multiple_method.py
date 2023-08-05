class X:
    def m(self):
        print "X.m"

class Y:
    def m(self):
        print "Y.m"

if 2:
    x = X()
else:
    x = Y()

x.m()
