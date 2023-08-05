cdef class AAA:
    cpdef foo(self, int k):
        return k
    cpdef opt(self, k=1, int x=None):
        return k

    
        
cdef int blah(int k):
    return k*k