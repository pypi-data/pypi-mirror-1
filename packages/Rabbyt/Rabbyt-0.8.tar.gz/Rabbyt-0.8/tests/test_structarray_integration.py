import unittest
import rabbyt.anims
from rabbyt.anims import *
import structarray
import weakref
import ctypes


class TestAnimableInArray(unittest.TestCase):
    def setUp(self):
        class Sprite(Animable):
            x = anim_slot()
            y = anim_slot()
            xy = swizzle("x", "y")
        self.Sprite_class = Sprite
        self.sprite = Sprite(xy=(1,2))
        self.sprite2 = Sprite()
        self.array = structarray.ObjectArray(("x","y"))
        self.array.add(self.sprite)
        self.array.add(self.sprite2)

    def test_access(self):
        self.array.x = 1
        self.array.y = 5
        self.assertEqual(self.sprite.x, 1)
        self.assertEqual(self.sprite.y, 5)
        self.assertEqual(self.sprite2.x, 1)
        self.assertEqual(self.sprite2.y, 5)

    def test_write(self):
        self.sprite.x = 2
        self.sprite.y = 6
        self.sprite2.x = 3
        self.sprite2.y = 7
        self.assertEqual(self.array.x[0], 2)
        self.assertEqual(self.array.y[0], 6)
        self.assertEqual(self.array.x[1], 3)
        self.assertEqual(self.array.y[1], 7)

    def test_many(self):
        a = structarray.ObjectArray(("x","y"))
        for i in range(100):
            s = self.Sprite_class()
            a.add(s)
            s.x = sy = i
        self.assertEqual(list(a.x), range(100))

    def test_stride(self):
        self.assertEqual(self.array.get_data_stride(), 12)

    def test_read_anim(self):
        self.array.x[0] = 10
        slot = self.Sprite_class.x.get_slot(self.sprite)
        self.assertEqual(slot.value, 10)

    def test_assign_before_add(self):
        self.assertEqual(self.array.x[0], 1)
        self.assertEqual(self.array.y[0], 2)

    def test_assign_after_add(self):
        self.sprite.xy = 2,3
        self.assertEqual(self.array.x[0], 2)
        self.assertEqual(self.array.y[0], 3)

if __name__ == '__main__':
    unittest.main()
