from __future__ import division

import unittest

from rabbyt.primitives import Quad

class TestQuadAsRect(unittest.TestCase):
    def setUp(self):
        self.quad = Quad((-11, 12, 13, -14))

    def test_as_list(self):
        self.assertEqual(list(self.quad),
            [(-11,12), (13,12), (13,-14), (-11,-14)])

    def test_read_left(self):
        self.assertEqual(self.quad.left, -11)

    def test_write_left(self):
        self.quad.left = 1
        self.assertEqual(list(self.quad), [(1,12), (25,12), (25,-14), (1,-14)])

    def test_read_top(self):
        self.assertEqual(self.quad.top, 12)

    def test_write_top(self):
        self.quad.top = 1
        self.assertEqual(list(self.quad),
                [(-11,1), (13,1), (13,-25), (-11,-25)])

    def test_read_right(self):
        self.assertEqual(self.quad.right, 13)

    def test_write_right(self):
        self.quad.right = -1
        self.assertEqual(list(self.quad),
                [(-25,12), (-1,12), (-1,-14), (-25,-14)])

    def test_read_bottom(self):
        self.assertEqual(self.quad.bottom, -14)

    def test_write_bottom(self):
        self.quad.bottom = 1
        self.assertEqual(list(self.quad),
                [(-11,27), (13,27), (13,1), (-11,1)])

    # TODO x,y,width,height

if __name__ == '__main__':
    unittest.main()
