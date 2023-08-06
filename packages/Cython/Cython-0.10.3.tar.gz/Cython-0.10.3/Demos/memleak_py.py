from memleak import foo
from sage.all import get_memory_usage

def test():
    print get_memory_usage()
    for i in range(100000):
        try:
            foo()
            raise TypeError
        except TypeError:
            pass
    print get_memory_usage()

test()
