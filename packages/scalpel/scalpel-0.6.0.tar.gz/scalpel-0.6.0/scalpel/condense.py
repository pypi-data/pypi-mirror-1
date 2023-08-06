def cell_start(start, len, width):
    return float(start * len) / width

def _overview(frames, start, end, width):
    bad = frames[start:end]
    length = len(bad)
    out = []
    for i in range(int(width)):
        out.append(i)

    return [out]

# def condense(frames, width)


def test_channels():
    import numpy
    frames = numpy.array(range(1000000))
    
    for w in [1, 10, 13, 14, 15, 29, 54, 12.0, 347, 231., 1030]:
        c = _overview(frames, 0, len(frames), w)
        print  len(c[0]), w, c[0][-1]
        assert len(c[0]) == w

def test_cell_start():
    assert cell_start(0, 1000, 10) == 0
    print cell_start(2, 20, 10)
    assert cell_start(2, 20, 10) == 1

test_cell_start()
test_channels()
