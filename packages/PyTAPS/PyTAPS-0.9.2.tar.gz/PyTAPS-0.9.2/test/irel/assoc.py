from itaps import iBase, iMesh, iGeom, iRel
from itaps.iBase import StorageOrder as Stg
import numpy
import unittest

class TestAssoc(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()
        self.geom = iGeom.Geom()
        self.rel  = iRel.Assoc()

    def tearDown(self):
        self.geom.deleteAll()

    def testEntEntAssoc(self):
        pair = self.rel.createAssociation(self.mesh, 0, self.geom, 0)

        mesh_ent = self.mesh.createVtx([0, 0, 0])
        geom_ent = self.geom.createBrick(2, 2, 2)
        pair.setAssociation(mesh_ent, geom_ent)

        self.assertEqual(pair.getEntAssociation(first=mesh_ent),  geom_ent)
        self.assertEqual(pair.getEntAssociation(mesh_ent, False), geom_ent)
        self.assertEqual(pair.getEntAssociation(second=geom_ent), mesh_ent)
        self.assertEqual(pair.getEntAssociation(geom_ent, True),  mesh_ent)

    def testEntEntArrAssoc(self):
        pair = self.rel.createAssociation(self.mesh, 0, self.geom, 0)

        mesh_ent = self.mesh.createVtx([0, 0, 0])
        self.geom.createBrick(2, 2, 2)
        geom_ents = self.geom.getEntities(iBase.Type.vertex)
        pair.setAssociation(mesh_ent, geom_ents)

        assoc = pair.getEntArrAssociation(first=mesh_ent)
        # TODO: finish this test

    def testEntArrEntAssoc(self):
        pair = self.rel.createAssociation(self.mesh, 0, self.geom, 0)

        mesh_ents = self.mesh.createVtx([[0, 0, 0]]*8, Stg.interleaved)
        geom_ent = self.geom.createBrick(2, 2, 2)
        pair.setAssociation(mesh_ents, geom_ent)
        # TODO: finish this test

    def testEntArrEntArrAssoc(self):
        pair = self.rel.createAssociation(self.mesh, 0, self.geom, 0)

        mesh_ents = self.mesh.createVtx([[0, 0, 0]]*8, Stg.interleaved)
        self.geom.createBrick(2, 2, 2)
        geom_ents = self.geom.getEntities(iBase.Type.vertex)
        pair.setAssociation(mesh_ents, geom_ents)

        assoc = pair.getEntAssociation(first=mesh_ents)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.raw == geom_ents).all())

        assoc = pair.getEntAssociation(mesh_ents, False)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.raw == geom_ents).all())

        assoc = pair.getEntAssociation(second=geom_ents)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.raw == mesh_ents).all())

        assoc = pair.getEntAssociation(geom_ents, True)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.raw == mesh_ents).all())

    def testEntSetAssoc(self):
        pair = self.rel.createAssociation(self.mesh, 0, self.geom, 1)

        mesh_ent = self.mesh.createVtx([0, 0, 0])
        geom_set = self.geom.createEntSet(False)
        pair.setAssociation(mesh_ent, geom_set)

        self.assertEqual(pair.getSetAssociation(first=mesh_ent),  geom_set)
        self.assertEqual(pair.getSetAssociation(mesh_ent, False), geom_set)
        self.assertEqual(pair.getEntAssociation(second=geom_set), mesh_ent)
        self.assertEqual(pair.getEntAssociation(geom_set, True),  mesh_ent)

    def testEntSetArrAssoc(self):
        pass

    def testEntArrSetAssoc(self):
        pass

    def testEntArrSetArrAssoc(self):
        pair = self.rel.createAssociation(self.mesh, 0, self.geom, 1)

        mesh_ents = self.mesh.createVtx([[0, 0, 0]]*3, Stg.interleaved)
        geom_sets = [ self.geom.createEntSet(False),
                      self.geom.createEntSet(False),
                      self.geom.createEntSet(False) ]
        pair.setAssociation(mesh_ents, geom_sets)

        assoc = pair.getSetAssociation(first=mesh_ents)
        self.assert_((assoc == geom_sets).all())
        assoc = pair.getSetArrAssociation(first=mesh_ents)
        self.assert_((assoc == geom_sets).all())

        assoc = pair.getSetAssociation(mesh_ents, False)
        self.assert_((assoc == geom_sets).all())
        assoc = pair.getSetArrAssociation(mesh_ents, False)
        self.assert_((assoc == geom_sets).all())

        assoc = pair.getEntAssociation(second=geom_sets)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.raw == mesh_ents).all())
        assoc = pair.getEntArrAssociation(second=geom_sets)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.raw == mesh_ents).all())

        assoc = pair.getEntAssociation(geom_sets, True)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.raw == mesh_ents).all())
        assoc = pair.getEntArrAssociation(geom_sets, True)
        self.assert_((assoc.offsets == numpy.arange(len(mesh_ents)+1)).all())
        self.assert_((assoc.raw == mesh_ents).all())

    def testSetEntAssoc(self):
        pair = self.rel.createAssociation(self.mesh, 1, self.geom, 0)

        mesh_set = self.mesh.createEntSet(False)
        geom_ent = self.geom.createBrick(2, 2, 2)
        pair.setAssociation(mesh_set, geom_ent)

        self.assertEqual(pair.getEntAssociation(first=mesh_set),  geom_ent)
        self.assertEqual(pair.getEntAssociation(mesh_set, False), geom_ent)
        self.assertEqual(pair.getSetAssociation(second=geom_ent), mesh_set)
        self.assertEqual(pair.getSetAssociation(geom_ent, True),  mesh_set)

    def testSetEntArrAssoc(self):
        pass

    def testSetArrEntAssoc(self):
        pass

    def testSetArrEntArrAssoc(self):
        pair = self.rel.createAssociation(self.mesh, 1, self.geom, 0)

        mesh_sets = [ self.mesh.createEntSet(False),
                      self.mesh.createEntSet(False),
                      self.mesh.createEntSet(False) ]
        self.geom.createBrick(2, 2, 2)
        geom_ents = self.geom.getEntities(iBase.Type.vertex)[0:3]
        pair.setAssociation(mesh_sets, geom_ents)

        assoc = pair.getEntAssociation(first=mesh_sets)
        self.assert_((assoc.offsets == numpy.arange(len(geom_ents)+1)).all())
        self.assert_((assoc.raw == geom_ents).all())
        assoc = pair.getEntArrAssociation(first=mesh_sets)
        self.assert_((assoc.offsets == numpy.arange(len(geom_ents)+1)).all())
        self.assert_((assoc.raw == geom_ents).all())

        assoc = pair.getEntAssociation(mesh_sets, False)
        self.assert_((assoc.offsets == numpy.arange(len(geom_ents)+1)).all())
        self.assert_((assoc.raw == geom_ents).all())
        assoc = pair.getEntArrAssociation(mesh_sets, False)
        self.assert_((assoc.offsets == numpy.arange(len(geom_ents)+1)).all())
        self.assert_((assoc.raw == geom_ents).all())

        assoc = pair.getSetAssociation(second=geom_ents)
        self.assert_((assoc == mesh_sets).all())
        assoc = pair.getSetArrAssociation(second=geom_ents)
        self.assert_((assoc == mesh_sets).all())

        assoc = pair.getSetAssociation(geom_ents, True)
        self.assert_((assoc == mesh_sets).all())
        assoc = pair.getSetArrAssociation(geom_ents, True)
        self.assert_((assoc == mesh_sets).all())

    def testSetSetAssoc(self):
        pair = self.rel.createAssociation(self.mesh, 1, self.geom, 1)

        mesh_set = self.mesh.createEntSet(False)
        geom_set = self.geom.createEntSet(False)
        pair.setAssociation(mesh_set, geom_set)

        self.assertEqual(pair.getSetAssociation(first=mesh_set),  geom_set)
        self.assertEqual(pair.getSetAssociation(mesh_set, False), geom_set)
        self.assertEqual(pair.getSetAssociation(second=geom_set), mesh_set)
        self.assertEqual(pair.getSetAssociation(geom_set, True),  mesh_set)

    def testSetSetArrAssoc(self):
        pass

    def testSetArrSetAssoc(self):
        pass

    def testSetArrSetArrAssoc(self):
        pair = self.rel.createAssociation(self.mesh, 1, self.geom, 1)

        mesh_sets = [ self.mesh.createEntSet(False),
                      self.mesh.createEntSet(False),
                      self.mesh.createEntSet(False) ]
        geom_sets = [ self.geom.createEntSet(False),
                      self.geom.createEntSet(False),
                      self.geom.createEntSet(False) ]
        pair.setAssociation(mesh_sets, geom_sets)

        assoc = pair.getSetAssociation(first=mesh_sets)
        self.assert_((assoc == geom_sets).all())
        assoc = pair.getSetArrAssociation(first=mesh_sets)
        self.assert_((assoc == geom_sets).all())

        assoc = pair.getSetAssociation(mesh_sets, False)
        self.assert_((assoc == geom_sets).all())
        assoc = pair.getSetArrAssociation(mesh_sets, False)
        self.assert_((assoc == geom_sets).all())

        assoc = pair.getSetAssociation(second=geom_sets)
        self.assert_((assoc == mesh_sets).all())
        assoc = pair.getSetArrAssociation(second=geom_sets)
        self.assert_((assoc == mesh_sets).all())

        assoc = pair.getSetAssociation(geom_sets, True)
        self.assert_((assoc == mesh_sets).all())
        assoc = pair.getSetArrAssociation(geom_sets, True)
        self.assert_((assoc == mesh_sets).all())

    def testInfer(self):
        pass

    def testInferAll(self):
        pair = self.rel.createAssociation(self.mesh, 0, self.geom, 0)

        self.geom.createBrick(2, 2, 2)
        geom_verts = self.geom.getEntities(iBase.Type.vertex)
        coords = self.geom.getVtxCoords(geom_verts, Stg.interleaved)
        mesh_verts = self.mesh.createVtx(coords, Stg.interleaved)

        pair.inferAllAssociations()


if __name__ == '__main__':
    unittest.main()
