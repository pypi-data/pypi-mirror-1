cdef int a, b
cdef int *foo = &a if a else &b


#cdef double x = &a + 3.3

cdef double x = a if a else 3.3

cdef object s = [], t, u, v = [1,2,3]
z = 1 < 2
z = t is s == u is v
z = t is s is u is v
z = t == s in v
z = t not in s

#import re
#re.compile('/* */') # the '*/' here is bad

a
b

cdef class A:
    cdef int foo(A aa, int a) except -2:
        return a
        
    cdef int foo2(A aa, int a) except -2:
        return aa
        
    cpdef int bar(A aa, int a) except -2:
        return a
        
    def test(self):
        if self is None:
            return self.foo(3)
        else:
            py_func(1)
            L = -1, 0, 1, 1, 2345
            return L
        
    def test2(self):
        return self.test()
        
cdef A aa
print aa is None

cdef A aaa
print aaa == aa

def py_func(x):
    pass