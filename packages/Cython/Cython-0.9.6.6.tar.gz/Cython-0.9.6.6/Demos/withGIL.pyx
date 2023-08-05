cdef int foo_c(int n, o) with GIL:
    try:
        return n-1
    except TypeError:
        return n+1
    
def foo(n):
    return foo_c(n, "hi")

cdef class Blah:
    cdef bar(self) with GIL:
        return self+1
        
cdef class Glub(Blah):
    cdef bar(self):
        return self+2
    cdef foo(self):
        return self+3
    cdef flub(self) with GIL:
        return self+3
