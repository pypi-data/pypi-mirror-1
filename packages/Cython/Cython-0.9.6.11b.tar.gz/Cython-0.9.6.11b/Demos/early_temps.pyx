cdef foo(x):
    return x + (x-x) + x*x
    
def test_it(N):
    x = 10
    cdef int i
    for i from 0 <= i < N:
        foo(x)
        

