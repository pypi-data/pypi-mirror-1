def f(x):
    if len(x) == 1:
        return x[0]
    else:
        return f(x[1:])

f([1,2,3])
f(["a", "b", "c"])
