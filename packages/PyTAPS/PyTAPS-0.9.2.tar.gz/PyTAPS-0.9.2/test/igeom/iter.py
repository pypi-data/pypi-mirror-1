from itaps import iBase, iGeom
import unittest

class TestIter(unittest.TestCase):
    def setUp(self):
        self.geom = iGeom.Geom()
        self.empty = self.geom.createEntSet(True)

        self.ent = self.geom.createBrick(1,1,1)
        self.set = self.geom.createEntSet(True)
        self.set.add(self.ent)

    def tearDown(self):
        self.geom.deleteAll()
        self.geom = None

    def testEmpty(self):
        for i in self.empty.iterate(iBase.Type.all):
            self.fail('empty iterator has >0 elements')

    def testArrEmpty(self):
        for i in self.empty.iterate(iBase.Type.all, 16):
            self.fail('empty iterator has >0 elements')

    def testSingle(self):
        count = 0
        for i in self.set.iterate(iBase.Type.all):
            count += 1
            self.assertEqual(i, self.ent)
        self.assertEqual(count, 1)

    def testArr(self):
        count = 0
        for i in self.set.iterate(iBase.Type.all, 16):
            count += 1
            self.assertEqual(i[0], self.ent)
        self.assertEqual(count,1)

    def testAlternate(self):
        count = 0
        iter = iGeom.Iterator(self.set, iBase.Type.all)

        self.assertEqual(iter.instance, self.geom)

        for i in iter:
            count += 1
            self.assertEqual(i, self.ent)
        self.assertEqual(count, 1)
        iter.reset()

if __name__ == '__main__':
    unittest.main()
