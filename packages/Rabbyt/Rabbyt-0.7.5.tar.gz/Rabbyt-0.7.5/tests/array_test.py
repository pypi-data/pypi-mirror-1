#from __future__ import division

import unittest

from rabbyt.arrays import *

class TestArray1d(unittest.TestCase):
    def setUp(self):
        self.array = Array1d(range(10))

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
        self.assertEqual(tuple(self.array + Array1d(range(100,110))),
                tuple(range(100, 120, 2)))

    def test_inplace_add(self):
        self.array += 100
        self.assertEqual(tuple(self.array), tuple(range(100, 110)))


    def test_sub_scalar(self):
        self.assertEqual(tuple(self.array - 10), tuple(range(-10,0)))

    def test_sub_array(self):
        self.assertEqual(tuple(self.array - Array1d(range(100,110))),
                tuple([-100]*10))

    def test_inplace_sub(self):
        self.array -= (-100)
        self.assertEqual(tuple(self.array), tuple(range(100, 110)))


    def test_mul_scalar(self):
        self.assertEqual(tuple(self.array * 10), tuple(range(0,100,10)))

    def test_mul_array(self):
        self.assertEqual(tuple(self.array * Array1d(range(10,20))),
                tuple([i*(i+10) for i in range(10)]))

    def test_inplace_mul(self):
        self.array *= 100
        self.assertEqual(tuple(self.array), tuple(range(0, 1000,100)))


    def test_div_scalar(self):
        self.assertEqual(tuple(self.array / .5 ), tuple(range(0,20, 2)))

    def test_div_array(self):
        res = tuple(self.array / Array1d(range(10,20)))
        for i in range(10):
            self.assertAlmostEqual(res[i], i/(i+10.))

    def test_inplace_div(self):
        self.array /= .5
        self.assertEqual(tuple(self.array), tuple(range(0, 20, 2)))

    # TODO: Compairing

    def test_repeat(self):
        self.assertEqual(tuple(self.array.repeat(3)), tuple(range(10)*3))

    def test_stretch(self):
        self.assertEqual(tuple(self.array.stretch(3)), (0,0,0,1,1,1,2,2,2,
                3,3,3,4,4,4,5,5,5,6,6,6,7,7,7,8,8,8,9,9,9))

    def test_append_repeat(self):
        r = self.array.repeat(3)
        self.array.append(10)
        self.assertEqual(tuple(r), tuple(range(11)*3))

    def test_append_stretch(self):
        s = self.array.stretch(3)
        self.array.append(10)
        self.assertEqual(tuple(s), (0,0,0,1,1,1,2,2,2,
                3,3,3,4,4,4,5,5,5,6,6,6,7,7,7,8,8,8,9,9,9,10,10,10))

    def test_shrink_repeat(self):
        r = self.array.repeat(3)
        self.array.set_size(5)
        self.assertEqual(tuple(r), tuple(range(5)*3))

    def test_shrink_stretch(self):
        s = self.array.stretch(3)
        self.array.set_size(5)
        self.assertEqual(tuple(s), (0,0,0,1,1,1,2,2,2,3,3,3,4,4,4))

class TestArray2d(unittest.TestCase):
    def setUp(self):
        self.array = Array2d(('x','y'), zip(range(10), range(100,110)))

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
        self.array.set_size(100)
        self.assertEqual(len(x), 100)

    def test_resize_item_attr(self):
        item = self.array[8]
        self.array.set_size(3)
        self.assertRaises(IndexError, lambda:item.x)

    def test_resize_item_index(self):
        item = self.array[8]
        self.array.set_size(3)
        self.assertRaises(IndexError, lambda:item[0])

    def test_append(self):
        self.array.append((10,110))
        self.assertEqual(self.array[10].x, 10)
        self.assertEqual(self.array[10].y, 110)

    def test_append_from_zero(self):
        array = Array2d(('x','y'))
        array.append((5,6))
        self.assertEqual(len(array), 1)
        self.assertEqual(array[0].x, 5)

class TestArray2dByteAttributes(unittest.TestCase):
    def setUp(self):
        self.array = Array2d((('r','g','b','a'),), [(.5,.5,.5,.5),
                (.1,.3,.1,.1),(.2,.2,.2,.2)])

    def test_len(self):
        self.assertEqual(len(self.array), 3)

    def test_item_item_access(self):
        self.assertAlmostEqual(self.array[1][0], .1, 2)
        self.assertAlmostEqual(self.array[1][1], .3, 2)

    def test_item_attribute_access(self):
        self.assertAlmostEqual(self.array[1].x, .1, 2)
        self.assertAlmostEqual(self.array[1].y, .3, 2)

    def test_attribute_access(self):
        self.assertEqual(len(self.array.r), 3)
        self.assertAlmostEqual(self.array.r[2], .2, 2)


    def test_item_item_assign(self):
        self.array[1][1] = .6
        self.assertAlmostEqual(self.array[1][1], .6, 2)

    def test_item_attribute_access(self):
        self.array[1].a = .8
        self.assertAlmostEqual(self.array[1].a, .8, 2)

    def test_attribute_item_assign(self):
        self.array.r[2] = .11
        self.assertAlmostEqual(self.array.r[2], .11, 2)


    def test_attribute_assign(self):
        self.array.r = self.array.g
        self.assertEqual(self.array.r[1], self.array.g[1])

    def test_item_assign(self):
        self.array[1] = (1,1,1,1)
        self.assertEqual(tuple(self.array[1]), (1,1,1,1))

    def test_upper_bounds(self):
        self.array[0].r = 5
        self.assertEqual(self.array[0].r, 1)

    def test_lower_bounds(self):
        self.array[0].r = -5
        self.assertEqual(self.array[0].r, 0)


if __name__ == '__main__':
    unittest.main()
