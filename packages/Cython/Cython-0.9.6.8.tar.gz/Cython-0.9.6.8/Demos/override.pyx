cdef extern from "stdio.h":
    pass

cdef class A:
    cdef overrideable foo(self, int k):
        print "A.foo", k
        return "ret a"
        
    cdef visible bar(self, int k):
        print "A.bar", k

cdef class B(A):
    cdef overrideable foo(self, int k):
        print "B.foo", k
        return "ret b"
        

class C(B):
    def foo(self, int k):
        print "C.foo", k
        return "ret c"
        
a = A()
b = B()
c = C()

a.foo(1)
b.foo(1)
c.foo(1)

cdef A aa = A(), bb = B(), cc = C()

print "aa", aa.foo(1)
print "bb", bb.foo(1)
print "cc", cc.foo(1)
print "done"



