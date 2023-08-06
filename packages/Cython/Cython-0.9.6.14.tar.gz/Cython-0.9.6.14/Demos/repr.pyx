def test_one(a, b):
    return a(b)

def test_two():
    return test_one(repr, 'bob')
