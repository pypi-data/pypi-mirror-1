ctypedef struct foo "blah":
    int a
    foo *b

cdef foo f
f.a = 3
f.b = &f
