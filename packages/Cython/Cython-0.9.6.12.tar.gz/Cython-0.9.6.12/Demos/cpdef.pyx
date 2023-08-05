cdef class A:
    cpdef foo(self, int k):
        return "A %s" % k
        
    def bar(self, int k):
        return self.foo(k), A.foo(self, k)
        
    cpdef opt(self, k=1, int x=2):
        print k, x
        
cdef class B(A):
    cdef int b_int
    cpdef foo(self, int k):
        self.a_int += 1
        cdef A a = self
        a.a_int += 1
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
    
cdef class AA:
    cdef optional(self, int j):
        print j
        
cdef class BB(AA):
    cdef optional(self, int j, int k=3):
        print "BB", k, x

cdef class CC(BB):
    cdef optional(self, int j, int k=99, AA x=AA()):
        print "CC", k, x

cdef class DD(CC):
    cdef DD optional(self, int j, int k=99, AA x=AA()):
        return self
        
cdef class EE(DD):
    def optional(self):
        return 17


assert float(4), A().foo(int(4))

def blah(object x, double a, int b):
    print <int>a
    print <object>a
    print <int>x
    print <bint>x
    print <object>b
    cdef void* z
    z = <void *>x
    print <object>z
    cdef A aa
    aa = x
    aa = <A>x
    aa = <A?>x
    
cdef AA aaa = AA()
aaa.optional(5)

aaa = BB()
aaa.optional(5)

aaa = CC()
aaa.optional(6)

cdef BB bbb = BB()
bbb.optional(5, 1)
bbb.optional(5)

cdef BB bbb = CC()
bbb.optional(5, 1)
bbb.optional(5)

cdef CC ccc = CC()
ccc.optional(5, 1, aaa)
ccc.optional(5, 1)
ccc.optional(5)

cdef DD ddd = DD()
ddd = ddd.optional(3)

ccc = None
cdef foo(CC x=None):
    print x

cdef bint lots_of_args(int a=1, b=2, float c=1.5, d=2.5, e=None, f=True, bint g=(), h="hi", char* i="yo", void** j=NULL, int *k=NULL):
    return True, None, repr
    
bob = repr, repr("a"), bool, len

def f(**argsByName):
    (aVal, bVal) = "hi"
    (aVal, bVal) = [argsByName.get(argName,None) for argName in ["a","b"]]

    
print lots_of_args(0, 0, 0, 0, 0, 0, 0, "bye", "chao", NULL)

print ccc is None and (ddd is None or <bint>(ddd == 0))
    
cpdef module_level(x, double a):
    print "good"
    return a
    
    
print module_level(None, 3)
mf = module_level
print mf(None, 4)
