import structarray


def setup():
    global array, target_array
    array = structarray.Array(size=10000, default=100)
    target_array = structarray.Array(size=10000)

def test():
    array.assign_to(target_array)


if __name__=='__main__':
    from timeit import Timer
    t = Timer("test()", "from __main__ import test, setup; setup()")
    print min(t.repeat(10, 1000))
