from itaps import iBase, iMesh
import unittest

class TestIter(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()
        self.empty = self.mesh.createEntSet(True)

        self.ent = self.mesh.createVtx([1,2,3])
        self.set = self.mesh.createEntSet(True)
        self.set.add(self.ent)

    def testEmpty(self):
        for i in self.empty.iterate(iBase.Type.all, iMesh.Topology.all):
            self.fail('empty iterator has >0 elements')

    def testArrEmpty(self):
        for i in self.empty.iterate(iBase.Type.all, iMesh.Topology.all, 16):
            self.fail('empty iterator has >0 elements')

    def testSingle(self):
        count = 0
        for i in self.set.iterate(iBase.Type.all, iMesh.Topology.all):
            count += 1
            self.assertEqual(i, self.ent)
        self.assertEqual(count, 1)

    def testArr(self):
        count = 0
        for i in self.set.iterate(iBase.Type.all, iMesh.Topology.all, 16):
            count += 1
            self.assertEqual(i[0], self.ent)
        self.assertEqual(count,1)

    def testAlternate(self):
        count = 0
        iter = iMesh.Iterator(self.set, iBase.Type.all, iMesh.Topology.all)

        self.assertEqual(iter.instance, self.mesh)

        for i in iter:
            count += 1
            self.assertEqual(i, self.ent)
        self.assertEqual(count, 1)
        iter.reset()

if __name__ == '__main__':
    unittest.main()
