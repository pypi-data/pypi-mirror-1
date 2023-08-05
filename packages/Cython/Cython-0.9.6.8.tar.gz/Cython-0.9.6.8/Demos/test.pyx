#l = len([len, True, bool, bool])

cdef int aa
cdef int bb = hash(True)

from withGIL cimport Blah

cdef extern from "arrayobject.h":
#The following exposes the internal C structure of the numpy python object
# extern class [object PyArrayObject]  tells pyrex that this is
# a compiled python class defined by the C struct PyArrayObject
    cdef enum:
        NPY_OWNDATA = 0x0004 #bit mask so numpy does not free array contents when its destroyed
    
    ctypedef int intp 

    ctypedef extern class numpy.ndarray [object PyArrayObject]:
        cdef char *data
        cdef int nd
        cdef intp *dimensions
        cdef intp *strides
        cdef int flags


ctypedef extern class numpy2.ndarray2 [object PyArrayObject]:
    cdef char *data
    cdef int nd
    cdef intp *dimensions
    cdef intp *strides
    cdef int flags


cdef class MyInt:
    cdef int value
    def __init__(self, value):
        self.value = value
    def __add__(x,y):
        """what a doctest"""
        print "got", x, y
        return int(x) + int(y)
    def __int__(self):
        """this is how you make an int"""
        print "__int__"
        return self.value
    def __index__(self):
        print "__index__"
        return self.value
        
    cpdef cpfoo(self, int a):
        return a
        
    cpdef cpbar(self, int a):
        return a
        
def test_index(L, Py_ssize_t k=5):
    return L[k]
    
def test_index2(L, o=7):
#    cdef Py_ssize_t k = o
    cdef Py_ssize_t k
    k = o
    return L[k]

cdef class A:
    cdef int prop
    def foo(self, a, Py_ssize_t c=2345):
        self.foo_c()
        return a, c, len([1,2,3])
        
    def __add__(A self, A other):
        return 13

    cdef foo_c(self):
        return "nothing"
        
    def no_args(self):
        return 17
        
    def one_arg(self, other):
        return 18, other

    def one_int(self, int other):
        return 18, other

    def one_py_ssize_t(self, Py_ssize_t other):
        return 18, other

    def two_py_ssize_t(self, Py_ssize_t other, Py_ssize_t another):
        return 18, other
        
    def ternary(A self, A other, A third):
        return other
        
    def binary(A self, A other):
        self = other
        other = self
        return other.prop
        
def binary2(A other):
    return other.prop

def blah(A first, second, int third=3, Py_ssize_t fourth=4):
    return fourth

def one_arg(a):
    return a
    
def no_args():
    return "nope"
    
def kwds(**s):
    return "working"
    
def star_args(*x):
    return x
    
def both_stars(*x, **s):
    return x, s
    
cdef int ee(int i) except -1:
    return i
    
cdef int eee(int i):
    return ee(i)
    
cdef int eeee(int i) except -1:
    return eee(i) + ee(i)
    
# cdef a = name_error - 3
