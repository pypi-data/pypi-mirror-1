cdef class A:
    pass
    
cdef class B:
    pass
    
cdef A a = None
cdef B b = a

cdef struct my_struct:
    int a
    double b
    
cdef extern from *:
    forward(x, list y, type)
    my_struct* blah()
    my_struct (* blah)()
    
    struct fake_class:
        my_struct (*blah)(int)
        

        
#def will_segfault():
#    cdef fake_class my_class
#    my_class.blah(5)
#    cdef int (*iranges)[3] = NULL

def foo(x, list y, type):
    """just a doctest"""
    cdef a = x
    cdef list b = x
    cdef c = y
    cdef list d = y
    d = [(), ()]
    y.append(list)
    y.append(list(x))
    print "all is well"
    cdef char* s = "hi"
    print type
    
cdef int cfoo(A aa, A, int* aaa):
    pass
