from __future__ import division

import unittest

from rabbyt.sprites import *


class TestSprite(unittest.TestCase):
    pass


class TestBoundingRadius(unittest.TestCase):
    def test_bounding_radius_from_shape(self):
        s = Sprite()
        self.assertEqual(s.bounding_radius, s.shape.bounding_radius)
        s.shape.width = 100
        self.assertEqual(s.bounding_radius, s.shape.bounding_radius)

    def test_bounding_radius_explicit(self):
        s = Sprite()
        original_shape_radius = s.shape.bounding_radius
        s.bounding_radius = 5
        self.assertEqual(s.bounding_radius, 5)
        self.assertEqual(s.shape.bounding_radius, original_shape_radius)
        s.shape.width = 100
        self.assertEqual(s.bounding_radius, 5)
        del s.bounding_radius
        self.assertEqual(s.bounding_radius, s.shape.bounding_radius)

    def test_bounding_radius_squared(self):
        s = Sprite()
        self.assertEqual(s.bounding_radius_squared, s.bounding_radius**2)
        s.bounding_radius = 10
        self.assertEqual(s.bounding_radius_squared, 100)

class TestSpriteSides(unittest.TestCase):
    def setUp(self):
        self.s = Sprite(shape=(1,20,2,10))

    def testLeft(self):
        self.assertEqual(self.s.left, 1)

    def testTop(self):
        self.assertEqual(self.s.top, 20)

    def testRight(self):
        self.assertEqual(self.s.right, 2)

    def testBottom(self):
        self.assertEqual(self.s.bottom, 10)


if __name__ == '__main__':
    unittest.main()
