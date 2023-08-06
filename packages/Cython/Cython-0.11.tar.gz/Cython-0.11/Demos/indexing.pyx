def test_unsigned_long():
    cdef int i
    cdef unsigned long ix
    cdef D = {}
    for i from 0 <= i < sizeof(unsigned long) * 8:
        ix = (<unsigned long>1) << i
        D[ix] = True
        assert D[ix] is True
        del D[ix]
    assert len(D) == 0

def test_unsigned_short():
    cdef int i
    cdef unsigned short ix
    cdef D = {}
    for i from 0 <= i < sizeof(unsigned short) * 8:
        ix = (<unsigned short>1) << i
        D[ix] = True
        assert D[ix] is True
        del D[ix]
    assert len(D) == 0

def test_long_long():
    cdef int i
    cdef long long ix
    cdef D = {}
    for i from 0 <= i < sizeof(long long) * 8:
        ix = (<long long>1) << i
        D[ix] = True
        assert D[ix] is True
        del D[ix]
        D[-ix] = True
        assert D[-ix] is True
        del D[-ix]
    assert len(D) == 0
