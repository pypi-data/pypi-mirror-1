cdef class A:
    def __del__(self):
        print "del A"
    
cdef class B(A):
    def __del__(self):
        print "del B"
        
