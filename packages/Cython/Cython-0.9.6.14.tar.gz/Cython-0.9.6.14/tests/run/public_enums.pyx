__doc__ = """
    >>> public_enums.a
    0
    >>> public_enums.b
    1
    >>> public_enums.c
    99
    >>> public_enums.d
    1000
    >>> public_enums.x
    Traceback (most recent call last):
    ...
    AttributeError: 'module' object has no attribute 'x'
"""


cdef public enum my_public_enum:
    a
    b
    c = 'c'
    d = 1000

cdef enum my_private_enum:
    x = 5
    y
    z
    
a + x
