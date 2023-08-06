from itaps import iBase, iGeom
import unittest
from math import sqrt

class TestCreation(unittest.TestCase):
    def setUp(self):
        self.geom = iGeom.Geom()

        # TODO: for some reason this is necessary to make the geometry engine
        # play nice
        self.empty = self.geom.createEntSet(True)

    def tearDown(self):
        self.geom.deleteAll()
        self.geom = None

    def testSphere(self):
        ent = self.geom.createSphere(1)
        self.assert_( (self.geom.getEntBoundBox(ent) ==
                       [[-1,-1,-1], [1,1,1]]).all())

    def testPrism(self):
        ent = self.geom.createPrism(2, 3, 4, 4)

    def testBrick(self):
        ent = self.geom.createBrick(2, 2, 2)
        self.assert_( (self.geom.getEntBoundBox(ent) ==
                       [[-1,-1,-1], [1,1,1]]).all())

        # alternate form
        ent = self.geom.createBrick([2, 2, 2])
        self.assert_( (self.geom.getEntBoundBox(ent) ==
                       [[-1,-1,-1], [1,1,1]]).all())

    def testCylinder(self):
        ent = self.geom.createCylinder(2, 1, 1)
        self.assert_( (self.geom.getEntBoundBox(ent) ==
                       [[-1,-1,-1], [1,1,1]]).all())

    def testCone(self):
        ent = self.geom.createCone(2, 1, 1, 0.5)
        self.assert_( (self.geom.getEntBoundBox(ent) ==
                       [[-1,-1,-1], [1,1,1]]).all())

    def testTorus(self):
        ent = self.geom.createTorus(2, 1)
        self.assert_( (self.geom.getEntBoundBox(ent) ==
                       [[-3,-3,-1], [3,3,1]]).all())

    def testMove(self):
        ent = self.geom.createBrick(2, 2, 2)

        self.geom.moveEnt(ent, [1,0,0])
        self.assert_( (self.geom.getEntBoundBox(ent) ==
                       [[0,-1,-1], [2,1,1]]).all())

    def testScale(self):
        ent = self.geom.createBrick(2, 2, 2)

        self.geom.scaleEnt(ent, [1,2,3])
        self.assert_( (self.geom.getEntBoundBox(ent) ==
                       [[-1,-2,-3], [1,2,3]]).all())

    def testReflect(self):
        ent = self.geom.createBrick(2, 4, 6)

        self.geom.reflectEnt(ent, [1,1,0])
        self.assert_((abs(self.geom.getEntBoundBox(ent) -
                          [[-2,-1,-3], [2,1,3]]) < 1e-5).all())

    def testRotate(self):
        ent = self.geom.createBrick(2, 4, 6)

        self.geom.rotateEnt(ent, 90, [1,0,0])
        self.assert_( (self.geom.getEntBoundBox(ent) ==
                       [[-1,-3,-2], [1,3,2]]).all())

    def testSweep(self):
        ent = self.geom.createBrick(2, 2, 2)
        face = self.geom.getEntities(iBase.Type.face)[0]
        edge = self.geom.getEntAdj(face, iBase.Type.edge)[0]

        axis = self.geom.getEntTangent(edge, [0,0,0])
        result = self.geom.sweepEntAboutAxis(edge, 360, axis)
        self.assert_((abs(self.geom.getEntBoundBox(result) -
                          [[-sqrt(2),-1,-sqrt(2)], [sqrt(2),1,sqrt(2)]])
                      < 1e-5).all())

    def testSection(self):
        ent = self.geom.createSphere(1)
        self.geom.sectionEnt(ent, [1,0,0], 0, False)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.face), 2)

    def testImprint(self):
        ent1 = self.geom.createBrick(2, 2, 2)
        ent2 = self.geom.createBrick(2, 2, 2)
        self.geom.moveEnt(ent2, [1, 0, 0])
        self.geom.imprintEnts([ent1, ent2])
        self.assertEqual(self.geom.getNumOfType(iBase.Type.vertex), 24)

        self.geom.deleteAll()

        # alternate syntax
        ent1 = self.geom.createBrick(2, 2, 2)
        ent2 = self.geom.createBrick(2, 2, 2)
        self.geom.moveEnt(ent2, [1, 0, 0])
        self.geom.imprintEnts(ent1, ent2)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.vertex), 24)

    def testMerge(self):
        ent1 = self.geom.createBrick(2, 2, 2)
        ent2 = self.geom.createBrick(2, 2, 2)

        ents = self.geom.getEntities(iBase.Type.face)

        self.geom.moveEnt(ent2, [2,0,0])
        self.geom.mergeEnts(ents, 0.1)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.face), 11)

    def testDelete(self):
        ent1 = self.geom.createBrick(2, 2, 2)
        ent2 = self.geom.createBrick(2, 2, 2)

        self.geom.deleteEnt(ent1)
        self.assertEqual(self.geom.getNumOfType(iBase.Type.region), 1)

        self.geom.deleteAll()
        self.assertEqual(self.geom.getNumOfType(iBase.Type.all), 0)

    def testCopy(self):
        ent1 = self.geom.createBrick(2, 2, 2)
        ent2 = self.geom.copyEnt(ent1)

        self.assertEqual(self.geom.getNumOfType(iBase.Type.region), 2)
        self.assert_( (self.geom.getEntBoundBox(ent1) ==
                       self.geom.getEntBoundBox(ent2)).all())

    def testUnite(self):
        ent1 = self.geom.createBrick(2, 2, 4)
        ent2 = self.geom.createBrick(2, 4, 2)
        ent3 = self.geom.createBrick(4, 2, 2)

        union = self.geom.uniteEnts([ent1, ent2, ent3])
        self.assert_( (self.geom.getEntBoundBox(union) ==
                       [[-2,-2,-2], [2,2,2]]).all())

        # alternate syntax
        ent1 = self.geom.createBrick(2, 2, 4)
        ent2 = self.geom.createBrick(2, 4, 2)
        ent3 = self.geom.createBrick(4, 2, 2)

        union = self.geom.uniteEnts(ent1, ent2, ent3)
        self.assert_( (self.geom.getEntBoundBox(union) ==
                       [[-2,-2,-2], [2,2,2]]).all())

    def testIntersection(self):
        ent1 = self.geom.createBrick(2, 2, 4)
        ent2 = self.geom.createBrick(2, 4, 2)

        isect = self.geom.intersectEnts(ent1, ent2)
        self.assert_( (self.geom.getEntBoundBox(isect) ==
                       [[-1,-1,-1], [1,1,1]]).all())

    def testSubtract(self):
        ent1 = self.geom.createBrick(4, 4, 4)
        ent2 = self.geom.createBrick(2, 4, 4)
        self.geom.moveEnt(ent2,[1,0,0])

        sub = self.geom.subtractEnts(ent1, ent2)
        self.assert_( (self.geom.getEntBoundBox(sub) ==
                       [[-2,-2,-2], [0,2,2]]).all())


if __name__ == '__main__':
    unittest.main()
