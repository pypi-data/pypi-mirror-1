cdef class A:
    pass

cdef class B(A):
    a = 1
    b = 1
    
    def foo(self, k):
        self.a = k
