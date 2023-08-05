cdef foo(x):
    return x+1
    

cdef class Blah:
    cdef foo(self, x):
        return x+2
        

cdef class Blah2(Blah):
    cdef foo(self, x):
        return x+3
        
def test():

    cdef long foo_address = <long>foo
    cdef long blah_foo_address = <long>(Blah.foo)
    cdef long blah2_foo_address = <long>(Blah2.foo)
        
    cdef Blah x = Blah(), x2 = Blah2()

    cdef long x_foo_address = <long>(x.foo)
    x.foo(33)
    
    cdef long x2_foo_address = <long>(x2.foo)

    print hex(blah_foo_address), hex(x_foo_address)
    print hex(blah2_foo_address), hex(x2_foo_address)
    
    print Blah.foo is Blah.foo
    print Blah2.foo is Blah.foo

    print x2.foo is Blah.foo
    print x2.foo is Blah2.foo
        
# from func_pointers import test; test()

# PyObject *((struct __pyx_obj_13func_pointers_Blah *,PyObject *))
# PyObject *((struct __pyx_obj_13func_pointers_Blah *,PyObject *))


