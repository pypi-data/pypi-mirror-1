from __future__ import division

import unittest

from structarray import *

class TestArray(unittest.TestCase):
    def setUp(self):
        self.array = Array(range(10))

    def test_len(self):
        self.assertEqual(len(self.array), 10)

    def test_item_access(self):
        for i in range(10):
            self.assertEqual(self.array[i], i)

    def test_item_assign(self):
        self.array[2] = 20
        self.assertEqual(self.array[2], 20)

    def test_iter(self):
        self.assertEqual(sum(iter(self.array)), sum(range(10)))


    def test_add_scalar(self):
        self.assertEqual(tuple(self.array + 10), tuple(range(10,20)))

    def test_add_array(self):
        self.assertEqual(tuple(self.array + Array(range(100,110))),
                tuple(range(100, 120, 2)))

    def test_inplace_add(self):
        self.array += 100
        self.assertEqual(tuple(self.array), tuple(range(100, 110)))


    def test_sub_scalar(self):
        self.assertEqual(tuple(self.array - 10), tuple(range(-10,0)))

    def test_sub_array(self):
        self.assertEqual(tuple(self.array - Array(range(100,110))),
                tuple([-100]*10))

    def test_inplace_sub(self):
        self.array -= (-100)
        self.assertEqual(tuple(self.array), tuple(range(100, 110)))


    def test_mul_scalar(self):
        self.assertEqual(tuple(self.array * 10), tuple(range(0,100,10)))

    def test_mul_array(self):
        self.assertEqual(tuple(self.array * Array(range(10,20))),
                tuple([i*(i+10) for i in range(10)]))

    def test_mod(self):
        res = tuple(self.array % 2)
        for i in range(10):
            self.assertAlmostEqual(res[i], i%2)

    def test_inplace_mul(self):
        self.array *= 100
        self.assertEqual(tuple(self.array), tuple(range(0, 1000,100)))


    def test_div_scalar(self):
        self.assertEqual(tuple(self.array / .5 ), tuple(range(0,20, 2)))

    def test_div_array(self):
        res = tuple(self.array / Array(range(10,20)))
        for i in range(10):
            self.assertAlmostEqual(res[i], i/(i+10.))

    def test_inplace_div(self):
        self.array /= .5
        self.assertEqual(tuple(self.array), tuple(range(0, 20, 2)))

    def test_inplace_mod(self):
        self.array %= 2
        for i in range(10):
            self.assertAlmostEqual(self.array[i], i%2)

    def test_max(self):
        res = array_max(self.array, 5).copy()
        for i in range(10):
            self.assertEqual(res[i], max(i,5))

    def test_min(self):
        res = array_min(self.array, 5).copy()
        for i in range(10):
            self.assertEqual(res[i], min(i,5))

    # TODO: Compairing

    def test_repeat(self):
        self.assertEqual(tuple(self.array.repeat(3)), tuple(range(10)*3))

    def test_stretch(self):
        self.assertEqual(tuple(self.array.stretch(3)), (0,0,0,1,1,1,2,2,2,
                3,3,3,4,4,4,5,5,5,6,6,6,7,7,7,8,8,8,9,9,9))

    def test_assign_to(self):
        other = Array(size=10)
        self.array.assign_to(other)
        self.assertEqual(list(other), range(10))

    def test_assign_from(self):
        other = Array(range(10,20))
        self.array.assign_from(other)
        self.assertEqual(list(self.array), range(10,20))

    def test_assign_from_single(self):
        self.array.assign_from(20)
        self.assertEqual(list(self.array), [20]*10)

    def test_assign_from_list(self):
        self.array.assign_from(range(10,20))
        self.assertEqual(list(self.array), range(10,20))

    def test_assign_to_wrong_size(self):
        other = Array(size=5)
        self.assertRaises(ValueError, lambda:self.array.assign_to(other))

    def test_assign_from_wrong_size(self):
        other = Array(size=5)
        self.assertRaises(ValueError, lambda:other.assign_from(self.array))

    def test_assign_from_invalid(self):
        other = StructArray(('x',), size=10)
        self.assertRaises(TypeError, lambda:self.array.assign_from(other))

    def test_assign_to_invalid(self):
        other = StructArray(('x',), size=10)
        self.assertRaises(TypeError, lambda:self.array.assign_to(other))

    def test_initial_data_overful(self):
        array = Array(range(10), size=5)
        self.assertEqual(list(array), range(10))

    def test_initial_data_underful(self):
        array = Array(range(5), size=10, default=10)
        self.assertEqual(list(array), range(5)+[10]*5)

    def test_initial_data_equal(self):
        array = Array(range(10), size=10)
        self.assertEqual(list(array), range(10))

    def test_iter_protocol(self):
        iterator = iter(self.array)
        sum(iterator)
        # Make sure that the iterator still calls StopIteration after it has
        # finished.
        self.assertRaises(StopIteration, iterator.next)

    def test_op_op_arg1(self):
        self.array.assign_from((self.array+10.) + 5.)
        self.assertEqual(list(self.array), range(15,25))

    def test_op_op_arg2(self):
        self.array.assign_from(5. + (self.array+10.))
        self.assertEqual(list(self.array), range(15,25))


class TestMultidimisionArray(unittest.TestCase):
    def setUp(self):
        self.array = Array(size=(10,5), default=1)

    def test_len(self):
        self.assertEqual(len(self.array), 50)

    def test_item_assign(self):
        self.array[5,3] = 10
        self.assertEqual(self.array[5 + 3*10], 10)

    def test_item_access(self):
        self.array[2 + 4*10] = 10
        self.assertEqual(self.array[2,4], 10)

    def test_iter(self):
        self.assertEqual(sum(self.array), 50)

    def test_resize(self):
        self.assertRaises(ValueError, lambda: self.array.set_length(100))

    def test_bounds(self):
        self.assertRaises(IndexError, lambda: self.array[0,5])
        self.assertRaises(IndexError, lambda: self.array[0,-6])
        self.assertRaises(IndexError, lambda: self.array[-11,0])
        self.assertRaises(IndexError, lambda: self.array[10,0])

    def test_reverse_item_access(self):
        self.array[9,3] = 10
        self.assertEqual(self.array[-1,-2], 10)


class TestStructArray(unittest.TestCase):
    def setUp(self):
        self.array = StructArray(('x','y'), zip(range(10), range(100,110)))

    def test_len(self):
        self.assertEqual(len(self.array), 10)

    def test_item_len(self):
        self.assertEqual(len(self.array[0]), 2)

    def test_item_item_access(self):
        self.assertEqual(self.array[1][0], 1)
        self.assertEqual(self.array[1][1], 101)

    def test_item_attribute_access(self):
        self.assertEqual(self.array[1].x, 1)
        self.assertEqual(self.array[1].y, 101)

    def test_attribute_access(self):
        self.assertEqual(len(self.array.x), 10)
        self.assertEqual(self.array.x[2], 2)


    def test_item_item_assign(self):
        self.array[1][1] = 201
        self.assertEqual(self.array[1][1], 201)

    def test_item_attribute_access(self):
        self.array[1].y = 201
        self.assertEqual(self.array[1].y, 201)

    def test_attribute_item_assign(self):
        self.array.x[2] = 30
        self.assertEqual(self.array.x[2], 30)


    def test_attribute_assign(self):
        self.array.x = self.array.y
        self.assertEqual(self.array.x[1], self.array.y[1])
        #self.assertEqual(self.array.x, self.array.y)  # TODO

    def test_resize_attribute(self):
        x = self.array.x
        self.array.set_length(100)
        self.assertEqual(len(x), 100)

    def test_resize_item_attr(self):
        item = self.array[8]
        self.array.set_length(3)
        self.assertRaises(IndexError, lambda:item.x)

    def test_resize_item_index(self):
        item = self.array[8]
        self.array.set_length(3)
        self.assertRaises(IndexError, lambda:item[0])

    def test_append(self):
        self.array.append((10,110))
        self.assertEqual(self.array[10].x, 10)
        self.assertEqual(self.array[10].y, 110)

    def test_append_from_zero(self):
        array = StructArray(('x','y'))
        array.append((5,6))
        self.assertEqual(len(array), 1)
        self.assertEqual(array[0].x, 5)

    def test_iter_protocol(self):
        iterator = iter(self.array)
        [i for i in iterator]
        # Make sure that the iterator still calls StopIteration after it has
        # finished.
        self.assertRaises(StopIteration, iterator.next)

if __name__ == '__main__':
    unittest.main()
