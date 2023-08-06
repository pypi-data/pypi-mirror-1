from itaps import iBase, iMesh, iGeom, iRel
from itaps.iBase import StorageOrder as Stg
import numpy
import unittest

class TestBasic(unittest.TestCase):
    def setUp(self):
        self.mesh = iMesh.Mesh()
        self.geom = iGeom.Geom()
        self.rel  = iRel.Assoc()

    def tearDown(self):
        self.geom.deleteAll()

    def testMinimal(self):
        pair = self.rel.createAssociation(self.mesh, 0, self.geom, 0)
        self.rel.destroyAssociation(pair)

        self.assertEqual(pair.instance, self.rel)
        self.assertEqual(pair.first,    self.mesh)
        self.assertEqual(pair.second,   self.geom)

        self.mesh = None
        #self.geom = None
        self.rel  = None

    def testAssoc(self):
        pair = self.rel.createAssociation(self.mesh, 0, self.geom, 0)
        self.assertEqual(self.geom,
                         self.rel.getAssociatedInterfaces(self.mesh)[0])

        self.rel.destroyAssociation(pair)
        self.assertEqual(len(self.rel.getAssociatedInterfaces(self.mesh)), 0)

    def testCreateVtxAssoc(self):
        self.geom.createBrick(1, 1, 1)
        geom_verts = self.geom.getEntities(iBase.Type.vertex)
        coords = self.geom.getVtxCoords(geom_verts,Stg.interleaved)

        pair = self.rel.createAssociation(self.mesh, 0, self.geom, 0)

        mesh_vert = self.rel.createVtxAndAssociate(coords[0],geom_verts[0])
        self.assertEqual(geom_verts[0], pair.getEntAssociation(first=mesh_vert))

        mesh_verts = self.rel.createVtxAndAssociate(coords,geom_verts,
                                                    Stg.interleaved)
        assoc = pair.getEntAssociation(first=mesh_verts)
        self.assert_((assoc.offsets == numpy.arange(len(geom_verts)+1)).all())
        self.assert_((assoc.raw == geom_verts).all())


if __name__ == '__main__':
    unittest.main()
