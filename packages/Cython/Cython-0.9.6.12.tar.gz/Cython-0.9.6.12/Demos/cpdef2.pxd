cdef class AAA:
    cpdef foo(self, int k)
    cpdef opt(self, k=?, int x=*)
    cdef int a_int
    
cdef struct BBB:
    int a
    long b
    double c
    
cdef int blah(int k)
