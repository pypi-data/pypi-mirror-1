def foo(x):
    cdef long c = x
    cdef int b = x
    x = 200
    cdef short a = x
    x = 300
    cdef long long d = x
    print a, b, c, d
    
cdef bar(object x):
    cdef short a = x
    
print bar(4), <long>&bar