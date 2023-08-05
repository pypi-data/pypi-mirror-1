import structarray


def setup():
    global array, shape, out
    array = structarray.StructArray(("x", "y", "dx", "dy"), size=10000)
    shape = structarray.StructArray(("x", "y"),
            [(-10,10),(10,10),(10,-10),(-10,-10)])
    out = structarray.StructArray(("x", "y"), size=40000)

def test():
    out.x = array.x.stretch(4) + shape.x.repeat(10000)
    out.y = array.y.stretch(4) + shape.y.repeat(10000)


if __name__=='__main__':
    from timeit import Timer
    t = Timer("test()", "from __main__ import test, setup; setup()")
    print min(t.repeat(10, 1000))
