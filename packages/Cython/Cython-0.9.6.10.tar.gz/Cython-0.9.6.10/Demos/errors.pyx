# from spam cimport Spam

def foo():
    try:
        bar(1,2,3)
    except AttributeError:
        print "att"

def bar(bint a, int b, Py_ssize_t c, **kwds):
    print a, b, c
    try:
        flub()
    except:
        raise AttributeError, 'raised'
        
def flub():
    try:
        str.flub()
    except ValueError:
        print "got here"
        
foo()

cdef int jjj = 7
cdef object x = 4
jjj = x

# cdef Spam s = Spam()

cdef object y = A()

cdef class A:
    def __del__(self):
        print "deleting A"
    
class B(A):
    def blah(self):
        pass
    def blug(self):
        pass
        
        

