def intersection((a, b), (x, y)):
    if b <= x or a >= y:
        return None
    else:
        start = max(a, x)
        end = min(b, y)
        return start, end

def test_intersection():
    assert intersection((1, 4), (2, 3)) == (2, 3)
    assert intersection((2, 3), (1, 4)) == (2, 3)
    assert intersection((1, 7), (5, 9)) == (5, 7)
    assert intersection((5, 9), (1, 7)) == (5, 7)
    assert intersection((1, 4), (5, 9)) == None
    assert intersection((5, 9), (1, 4)) == None
