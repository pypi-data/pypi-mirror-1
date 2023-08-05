def f(x):
    if not isinstance(x, list):
        return g(x)
    else:
        return f(x[0])

def g(x):
    return x + x

f([[[1]]])
f([[["a"]]])
