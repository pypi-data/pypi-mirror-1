
cdef short i

a = -7

for i in range(3, a, -1):
    print i
    
def myothersum_good(n):
    cdef double s=0.0
    cdef double i
    for i from 0 <= i < n:
        s += 2.0*i
    return s
        
def myothersum_bad(n):
    cdef double s=0.0
    for i from 0 <= i < n:
        s += 2.0*i
    return s
        
print myothersum_good(10)
print myothersum_bad(10)


def test(k):
    cdef unsigned long m = k
    cdef long a = k
    cdef long long b = k
    cdef short c = k
    return m

test(int(2)**36)

