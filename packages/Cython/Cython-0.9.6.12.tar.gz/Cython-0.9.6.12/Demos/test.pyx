#l = len([len, True, bool, bool])

from pxd6 cimport MyStruct

cdef MyStruct my_var

from cpdef2 cimport AAA

cdef int aa
cdef int bb = hash(True)

# from withGIL cimport Blah

def foo(x):
    if x is None:
        print "yes"
    if x is None or x is not None:
        print "no"

cdef class MyInt:
    """
    Doctests are good. 
    """
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
        """
        cpfoo docstring
        """
        return a
        
    cpdef cpbar(self, int a):
        return a
        
    def blah(self):
        """
        blah docstring
        """
        
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
    
def kwds(a, **s):
    return "working"
    
def star_args(a, *x):
    return x
    
def both_stars(a, *x, **s):
    return a, x, s
    
#print both_stars(1, 2, 3, x=4) == (1, (2,3), {'x':4})
#print both_stars(a=1, x=4) == (1, (), {'x':4})
    
cdef int ee(int i) except -1:
    return i
    
cdef int eee(int i):
    return ee(i)
    
cdef int eeee(int i) except -1:
    return eee(i) + ee(i)
    
# cdef a = name_error - 3

def kw_only_args(a, *args, x):
    return 1

def test_tuple(a, int b, Py_ssize_t c, MyInt d, short e, f=7, int g=8):
#    T = 1,2,3
#    a, b, c = T
    return a, b, c, d, e, f, g

test_tuple(1,2,3,MyInt(10),5,6,7)

def default_args(a=1, b=1, c=1, d=1, e=1, f=1):
    return
    
def prepppp_args(a, b, c, d, e, f):
    return
    
cdef extern from "Python.h":
    object PyObject_CallObject(object, object)
    
def test_call(f, args, N):
    cdef int i
    for i from 0 <= i < N:
        PyObject_CallObject(f, args)
