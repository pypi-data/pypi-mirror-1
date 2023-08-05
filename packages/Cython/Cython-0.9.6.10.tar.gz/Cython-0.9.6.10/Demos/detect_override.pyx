print "starting"

cdef class A:
    cpdef good(self):
        print "A"
    cpdef overridden(self):
        print "A"
cdef class B(A):
    cpdef overridden(self):
        print "B"
class C(A):
    def overridden(self):
        print "C"


a = A()
b = B()
c = C()
print a.overridden == b.overridden
print a.good == b.good
print a.good

cdef extern from "descrobject.h":
    ctypedef struct PyMethodDef:
        void *ml_meth
        char *ml_name
    ctypedef struct PyMethodDescrObject:
        PyMethodDef *d_method
    void* PyCFunction_GET_FUNCTION(object)
    bint PyCFunction_Check(object)
    bint PyMethod_Check(object)

print "def test", (<void **>(A.good))[0] == (<void **>PyCFunction_GET_FUNCTION(b.good))[0]
print "def test", (<void **>(A.overridden))[0] == (<void **>PyCFunction_GET_FUNCTION(b.overridden))[0]

print <long>(<void **>(A.overridden))[0]
print <long>(<void **>(B.overridden))[0]
print <long>(<void **>PyCFunction_GET_FUNCTION(a.overridden))[0]
print <long>(<void **>PyCFunction_GET_FUNCTION(b.overridden))[0]


print <long>((A.overridden))
print A.overridden(a)
print a.overridden()
print <long>(<void *>(A.overridden))
print <long>(<void *>(PyCFunction_GET_FUNCTION(a.overridden)))
print "b"
print <long>(&(B.overridden))
print <long>(<void **>(B.overridden))
print <long>(<void **>PyCFunction_GET_FUNCTION(b.overridden))

print "cdef test", A.good == (<A>b).good
print "cdef test", A.overridden == (<A>b).overridden

print PyCFunction_Check(b.overridden)


print sizeof(long), sizeof(void *)

print PyMethod_Check((<object>A).good)
method = (<object>A).good
print <long>((<PyMethodDescrObject *>method).d_method)
print <long>((<PyMethodDescrObject *>method).d_method.ml_meth)
print ((<PyMethodDescrObject *>method).d_method.ml_name)

