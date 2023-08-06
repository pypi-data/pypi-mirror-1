from itaps.helpers import *
import unittest
import numpy
import sys

if sys.hexversion >= 0x020600f0:
    from itaps.namedtuple import namedtuple
    point = namedtuple('point', 'x y')
else:
    point = lambda *args: args

class TestOffsetList(unittest.TestCase):
    def setUp(self):
        self.single = OffsetList(numpy.arange(0, 13, 3),
                                 numpy.arange(12))
        self.multi  = OffsetList(numpy.arange(0, 13, 3),
                                 point(numpy.arange(12),
                                       numpy.arange(12, 24)))

    def testSingleBasic(self):
        self.assertEqual(len(self.single), 4)
        self.assert_((self.single[0] == [0, 1, 2]).all())
        self.assert_((self.single.offsets == numpy.arange(0, 13, 3)).all())
        self.assert_((self.single.raw == numpy.arange(12)).all())

    def testSingleIndex(self):
        for hunk, i in zip(self.single, range(len(self.single))):
            self.assertEqual(len(hunk), 3)
            self.assertEqual(self.single.length(i), 3)
            self.assert_((hunk == numpy.arange(i*3, (i+1)*3)).all())

        self.assertRaises(IndexError, lambda: self.single[4])
        self.assertRaises(IndexError, lambda: self.single[0,3])

    def testMultiBasic(self):
        self.assertEqual(len(self.multi), 4)
        self.assert_((self.multi[0][0] == [ 0,  1,  2]).all())
        self.assert_((self.multi[0][1] == [12, 13, 14]).all())
        self.assert_((self.multi.raw[0] == numpy.arange(12)).all())
        self.assert_((self.multi.raw[1] == numpy.arange(12,24)).all())

    def testMultiIndex(self):
        for hunk, i in zip(self.multi, range(len(self.multi))):
            self.assertEqual(len(hunk), 2)
            self.assertEqual(len(hunk[0]), 3)
            self.assertEqual(self.multi.length(i), 3)
            self.assert_((hunk[0] == numpy.arange(i*3,    (i+1)*3)   ).all())
            self.assert_((hunk[1] == numpy.arange(i*3+12, (i+1)*3+12)).all())

        self.assertRaises(IndexError, lambda: self.multi[4])
        self.assertRaises(IndexError, lambda: self.multi[0,3])

    def testMultiKey(self):
        for hunk, i in zip(self.multi.slice(0), range(len(self.multi))):
            self.assert_((hunk == numpy.arange(i*3, (i+1)*3)).all())
        for hunk, i in zip(self.multi.slice(1), range(len(self.multi))):
            self.assert_((hunk == numpy.arange(i*3+12, (i+1)*3+12)).all())

        self.assertRaises(AttributeError, lambda: self.multi.non_existant)

    if sys.hexversion >= 0x020600f0:
        def testMultiKeyNamed(self):
            print self.multi.fields
            self.assertEqual(self.multi.fields, ('x', 'y'))
            self.assert_((self.multi.x.raw == self.multi.slice('x').raw).all())
            self.assert_((self.multi.x.raw == self.multi.slice(0).raw).all())


if __name__ == '__main__':
    unittest.main()
