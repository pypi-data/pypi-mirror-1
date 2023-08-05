cdef class A:
    def doit(self):
        print type(self)
        self.doit_c()
    cdef doit_c(self):
        print "A"
    
cdef class B(A):
    cdef B b
    cdef bb
    
cdef class C(B):
    cdef doit_c(self):
        print "C"
    
cdef class D(C):
    # cdef d
    cdef doit_c(self):
        print "D"
    
cdef class E(D):
    def __new__(self, *args):
        print "hi"
    
cdef extern from "complexobject.h":

    struct Py_complex:
        double real
        double imag

    ctypedef class __builtin__.complex [object PyComplexObject]:
        cdef Py_complex cval 
        cdef o
        
cdef class X(complex):
    pass

cdef class Y(X):
    cdef y
    
    def __new__(self):
        print "hi"
    
    def __dealloc__(self):
        print "bye"

cdef class Z(complex):
    cdef z

