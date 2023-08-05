yy = 3

cdef class Blah:
    def foo(self):
        return 1
    xx = 5
    print "hi"
    print xx, yy, foo(3)
    cdef object zz
    
    def bar(self):
        xx = 5
        print "hi"
        print xx, yy
        
    bar = classmethod(foo)
    
    def call(self, Py_ssize_t j, Py_ssize_t k=5):
        return self.foo()
        
    
class Foo:
    vv = 4
    print vv
    def foo(self):
        return self.vv
    a = foo(4)
