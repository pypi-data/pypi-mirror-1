cdef class Foo:
  pass

cdef class Bar:
  cdef Foo foo

cdef class Baz:
  cdef Bar bar
  
  cpdef test(self):
      pass

cdef int somefunc(Baz baz):
  cdef Foo foo

  foo = baz.bar.foo  #<--- fails
