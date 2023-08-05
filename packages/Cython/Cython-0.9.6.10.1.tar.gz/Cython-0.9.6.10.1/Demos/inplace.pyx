

cdef class Blah:
    def __add__(self, y):
        print "add"
        return self
    def __iadd__(self, y):
        print "iadd"
        return self

    
cdef Blah a = Blah()
a += 5

cdef int b

b += a


c = 3

c += a

cdef object c

c += a