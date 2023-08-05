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
        
    rdef int bar(A aa, int a) except -2:
        return a
        
    def test(self):
        if self is None:
            return self.foo(3)
        else:
            return -1, 0, 1, 1, 2
        
    def test2(self):
        return self.test()
        
cdef A aa
print aa is None

cdef A aaa
print aaa == aa