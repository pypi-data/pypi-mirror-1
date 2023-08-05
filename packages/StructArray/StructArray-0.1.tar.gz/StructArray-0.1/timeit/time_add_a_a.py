import structarray


def setup():
    global array
    array = structarray.StructArray(("x", "y", "dx", "dy"), size=10000)

def test():
    array.x = array.y + array.dx


if __name__=='__main__':
    from timeit import Timer
    t = Timer("test()", "from __main__ import test, setup; setup()")
    print min(t.repeat(10, 1000))
