import structarray


def setup():
    global array
    array = structarray.StructArray(("x", "y", "dx", "dy"), size=1000)

def test():
    for i in xrange(len(array)):
        array[i] = (1,2,3,4)


if __name__=='__main__':
    from timeit import Timer
    t = Timer("test()", "from __main__ import test, setup; setup()")
    print min(t.repeat(10, 100))
