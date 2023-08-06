import shelve
import one_func

def f1(x):
    y = shelve.open(x)
    z = max(y)
    x = one_func.identity()
    return y
