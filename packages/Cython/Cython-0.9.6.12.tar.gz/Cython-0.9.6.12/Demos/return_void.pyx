
cdef int dummy[1000]

cdef void return_void(int x):
    cdef int i
    for i from 0 <= i < 10:
        dummy[i] += x
        
cdef int return_int(int x):
    cdef int i
    for i from 0 <= i < 10:
        dummy[i] += x


def time_void(N):
    cdef long i
    for i from 0 <= i < N:
        return_void(i)
        
def time_int(N):
    cdef long i
    for i from 0 <= i < N:
        return_int(i)
        
cdef class A:
    cdef foo(self, int x):
        print "A"
        
cdef class B(A):
    cpdef foo(self, int x):
        print "B"

cdef A a = A()
a.foo(1)
a = B()
a.foo(1)
