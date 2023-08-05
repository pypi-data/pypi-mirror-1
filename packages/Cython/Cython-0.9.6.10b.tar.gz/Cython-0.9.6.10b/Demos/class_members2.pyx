cdef extern from "math.h":
    double sqrt(double)

cdef class Run:
    x = 2
    y = sqrt(x)
    def foo(x):
        return x
    foo = classmethod(foo)
