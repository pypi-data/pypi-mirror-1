def f4(x):
    return min(x)

def g4(y):
    return max(y)

class Test4:
    def reset(self):
        class Inside:
            def foo(self):
                f4(self)
        f4(self)
        g4(self)

class Tset4:
    def __init__(self):
        f4(self)
    def parse(self):
        g4(self)
