cdef class A:
    cpdef foo(self, int k):
        return "A %s" % k
        
    def bar(self, int k):
        return self.foo(k), A.foo(self, k)
        
cdef class B(A):
    cpdef foo(self, int k):
        return "B %s" % k
        
class C(B):
    def foo(self, int k):
        return "C %s" % k

class D(C):
    def foo(self, int k):
        return "D %s" % k, C.foo(self, k), B.foo(self, k), A.foo(self, k)
        
for x in [A(), B(), C(), D()]:
    print x.foo(5)
    print x.bar(10)
    
cdef class AA(A):
    cpdef foo(self, int k):
        return k
        
assert float(4), A().foo(int(4))