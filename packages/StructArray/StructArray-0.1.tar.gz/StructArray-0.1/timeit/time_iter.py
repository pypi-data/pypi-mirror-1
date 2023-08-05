import structarray


def setup():
    global array
    array = structarray.Array(size=1000, default=1)

def test():
    sum(array)


if __name__=='__main__':
    from timeit import Timer
    t = Timer("test()", "from __main__ import test, setup; setup()")
    print min(t.repeat(10, 100))
