from itaps import iBase, iGeom
from itaps.iBase import StorageOrder as Stg
import unittest
import numpy

class TestCoords(unittest.TestCase):
    def setUp(self):
        self.geom = iGeom.Geom()

    def tearDown(self):
        self.geom.deleteAll()

    def testVtxCoordsXYZ(self):
        ent = self.geom.createBrick(2, 2, 2)
        verts = self.geom.getEntities(iBase.Type.vertex)

        coords = self.geom.getVtxCoords(verts[0])
        self.assert_((coords == [1,-1,1]).all())

        coords = self.geom.getVtxCoords(verts, Stg.interleaved)
        self.assert_((coords == [ [ 1, -1,  1],
                                  [ 1,  1,  1],
                                  [-1,  1,  1],
                                  [-1, -1,  1],
                                  [ 1,  1, -1],
                                  [ 1, -1, -1],
                                  [-1, -1, -1],
                                  [-1,  1, -1] ]).all())

    def testVtxCoordsUV(self):
        ent = self.geom.createBrick(2, 2, 2)
        faces = self.geom.getEntities(iBase.Type.face)
        verts = self.geom.getEntAdj(faces, iBase.Type.vertex)

        result = [ [ 1, -1],
                   [ 1,  1],
                   [ 1, -1],
                   [-1,  1],
                   [-1,  1],
                   [ 1, -1] ]

        # 1 vertex, 1 entity
        coords = self.geom.getVtxCoords(verts[0,0],dest=faces[0])
        self.assert_((coords == [1,-1]).all())
        coords = self.geom.getVtxCoords(verts[0,0],
                                        dest=(faces[0], iGeom.Basis.uv))
        self.assert_((coords == [1,-1]).all())
        coords = self.geom.getVtxCoords(verts[0,0], Stg.interleaved,
                                        dest=faces[0:1])
        self.assert_((coords == [[1,-1]]).all())
        coords = self.geom.getVtxCoords(verts[0,0], Stg.interleaved,
                                        dest=(faces[0:1], iGeom.Basis.uv))
        self.assert_((coords == [[1,-1]]).all())

        # 1 vertex, n entities
        coords = self.geom.getVtxCoords(verts[0,0], Stg.interleaved,
                                        dest=[faces[0]]*4)
        self.assert_((coords == [[1,-1]]*4).all())
        coords = self.geom.getVtxCoords(verts[0,0], Stg.interleaved,
                                        dest=([faces[0]]*4, iGeom.Basis.uv))
        self.assert_((coords == [[1,-1]]*4).all())

        # n vertices, 1 entity
        coords = self.geom.getVtxCoords(verts[0], Stg.interleaved,
                                        dest=faces[0])
        self.assert_((coords == [[1,-1], [1,1], [-1,1], [-1,-1]]).all())
        coords = self.geom.getVtxCoords(verts[0], Stg.interleaved,
                                        dest=(faces[0], iGeom.Basis.uv))
        self.assert_((coords == [[1,-1], [1,1], [-1,1], [-1,-1]]).all())

        # n vertices, n entities
        first_verts = [ verts[i,0] for i in range(len(verts)) ]
        coords = self.geom.getVtxCoords(first_verts, Stg.interleaved,
                                        dest=faces)
        self.assert_((coords == result).all())
        coords = self.geom.getVtxCoords(first_verts, Stg.interleaved,
                                        dest=(faces, iGeom.Basis.uv))
        self.assert_((coords == result).all())

    def testVtxCoordsU(self):
        ent = self.geom.createBrick(2, 2, 2)
        edges = self.geom.getEntities(iBase.Type.edge)
        verts = self.geom.getEntAdj(edges, iBase.Type.vertex)

        # 1 vertex, 1 entity
        coords = self.geom.getVtxCoords(verts[0,0],dest=edges[0])
        self.assert_((coords == [-1]).all())
        coords = self.geom.getVtxCoords(verts[0,0],
                                        dest=(edges[0], iGeom.Basis.u))
        self.assert_((coords == [-1]).all())
        coords = self.geom.getVtxCoords(verts[0,0], Stg.interleaved,
                                        dest=edges[0:1])
        self.assert_((coords == [[-1]]).all())
        coords = self.geom.getVtxCoords(verts[0,0], Stg.interleaved,
                                        dest=(edges[0:1], iGeom.Basis.u))
        self.assert_((coords == [[-1]]).all())

        # 1 vertex, n entities
        coords = self.geom.getVtxCoords(verts[0,0], Stg.interleaved,
                                        dest=[edges[0]]*4)
        self.assert_((coords == [[-1]]*4).all())
        coords = self.geom.getVtxCoords(verts[0,0], Stg.interleaved,
                                        dest=([edges[0]]*4, iGeom.Basis.u))
        self.assert_((coords == [[-1]]*4).all())

        # n vertices, 1 entity
        coords = self.geom.getVtxCoords(verts[0], Stg.interleaved,
                                        dest=edges[0])
        self.assert_((coords == [[-1], [1]]).all())
        coords = self.geom.getVtxCoords(verts[0], Stg.interleaved,
                                        dest=(edges[0], iGeom.Basis.u))
        self.assert_((coords == [[-1], [1]]).all())

        # n vertices, n entities
        first_verts = [ verts[i,0] for i in range(len(verts)) ]
        coords = self.geom.getVtxCoords(first_verts, Stg.interleaved,
                                        dest=edges)
        self.assert_((coords == [[-1]]*12).all())
        coords = self.geom.getVtxCoords(first_verts, Stg.interleaved,
                                        dest=(edges, iGeom.Basis.u))
        self.assert_((coords == [[-1]]*12).all())

    def testEntCoordsXYZtoUV(self):
        ent = self.geom.createBrick(2, 2, 2)
        faces = self.geom.getEntities(iBase.Type.face)

        ##### 1 vertex, 1 entity
        coords = self.geom.getEntCoords([0,0,0], dest=faces[0])
        self.assert_((coords == [0,0]).all())
        coords = self.geom.getEntCoords([0,0,0], dest=(faces[0],iGeom.Basis.uv))
        self.assert_((coords == [0,0]).all())
        coords = self.geom.getEntCoords([0,0,0], Stg.interleaved,
                                        dest=faces[0:1])
        self.assert_((coords == [0,0]).all())
        coords = self.geom.getEntCoords([0,0,0], Stg.interleaved,
                                        dest=(faces[0:1], iGeom.Basis.uv))
        self.assert_((coords == [0,0]).all())

        ##### 1 vertex, n entities
        coords = self.geom.getEntCoords([0,0,0], Stg.interleaved, dest=faces)
        self.assert_((coords == [[0,0]]*6).all())
        coords = self.geom.getEntCoords([0,0,0], Stg.interleaved,
                                        dest=(faces, iGeom.Basis.uv))
        self.assert_((coords == [[0,0]]*6).all())

        ##### n vertices, 1 entity
        coords = self.geom.getEntCoords([[0,0,0]]*6, Stg.interleaved,
                                        dest=faces[0])
        self.assert_((coords == [[0,0]]*6).all())
        coords = self.geom.getEntCoords([[0,0,0]]*6, Stg.interleaved,
                                        dest=(faces[0], iGeom.Basis.uv))
        self.assert_((coords == [[0,0]]*6).all())

        ##### n vertices, n entities
        coords = self.geom.getEntCoords([[0,0,0]]*6, Stg.interleaved,
                                        dest=faces)
        self.assert_((coords == [[0,0]]*6).all())
        coords = self.geom.getEntCoords([[0,0,0]]*6, Stg.interleaved,
                                        dest=(faces, iGeom.Basis.uv))
        self.assert_((coords == [[0,0]]*6).all())

    def testEntCoordsUVtoXYZ(self):
        ent = self.geom.createBrick(2, 2, 2)
        faces = self.geom.getEntities(iBase.Type.face)
        result = [ [ 0,  0,  1],
                   [ 0,  0, -1],
                   [ 0, -1,  0],
                   [-1,  0,  0],
                   [ 0,  1,  0],
                   [ 1,  0,  0] ]

        ##### 1 vertex, 1 entity
        coords = self.geom.getEntCoords([0,0], src=faces[0])
        self.assert_((coords == result[0]).all())
        coords = self.geom.getEntCoords([0,0], src=(faces[0], iGeom.Basis.uv))
        self.assert_((coords == result[0]).all())
        coords = self.geom.getEntCoords([0,0], Stg.interleaved, src=faces[0:1])
        self.assert_((coords == result[0]).all())
        coords = self.geom.getEntCoords([0,0], Stg.interleaved,
                                        src=(faces[0:1], iGeom.Basis.uv))
        self.assert_((coords == result[0]).all())

        ##### 1 vertex, n entities
        coords = self.geom.getEntCoords([0,0], Stg.interleaved, src=faces)
        self.assert_((coords == result).all())
        coords = self.geom.getEntCoords([0,0], Stg.interleaved,
                                        src=(faces, iGeom.Basis.uv))
        self.assert_((coords == result).all())

        ##### n vertices, 1 entity
        coords = self.geom.getEntCoords([[0,0]]*6, Stg.interleaved,
                                        src=faces[0])
        self.assert_((coords == result[0:1]*6).all())
        coords = self.geom.getEntCoords([[0,0]]*6, Stg.interleaved,
                                        src=(faces[0], iGeom.Basis.uv))
        self.assert_((coords == result[0:1]*6).all())

        ##### n vertices, n entities
        coords = self.geom.getEntCoords([[0,0]]*6, Stg.interleaved, src=faces)
        self.assert_((coords == result).all())
        coords = self.geom.getEntCoords([[0,0]]*6, Stg.interleaved,
                                        src=(faces, iGeom.Basis.uv))
        self.assert_((coords == result).all())

    def testEntCoordsXYZtoU(self):
        ent = self.geom.createBrick(2, 2, 2)
        edges = self.geom.getEntities(iBase.Type.edge)

        ##### 1 vertex, 1 entity
        coords = self.geom.getEntCoords([0,0,0], dest=edges[0])
        self.assert_((coords == [0]).all())
        coords = self.geom.getEntCoords([0,0,0], dest=(edges[0],iGeom.Basis.u))
        self.assert_((coords == [0]).all())
        coords = self.geom.getEntCoords([0,0,0], Stg.interleaved,
                                        dest=edges[0:1])
        self.assert_((coords == [0]).all())
        coords = self.geom.getEntCoords([0,0,0], Stg.interleaved,
                                        dest=(edges[0:1], iGeom.Basis.u))
        self.assert_((coords == [0]).all())

        ##### 1 vertex, n entities
        coords = self.geom.getEntCoords([0,0,0], Stg.interleaved, dest=edges)
        self.assert_((coords == [[0]]*12).all())
        coords = self.geom.getEntCoords([0,0,0], Stg.interleaved,
                                        dest=(edges, iGeom.Basis.u))
        self.assert_((coords == [[0]]*12).all())

        ##### n vertices, 1 entity
        coords = self.geom.getEntCoords([[0,0,0]]*12, Stg.interleaved,
                                        dest=edges[0])
        self.assert_((coords == [[0]]*12).all())
        coords = self.geom.getEntCoords([[0,0,0]]*12, Stg.interleaved,
                                        dest=(edges[0], iGeom.Basis.u))
        self.assert_((coords == [[0]]*12).all())

        ##### n vertices, n entities
        coords = self.geom.getEntCoords([[0,0,0]]*12, Stg.interleaved,
                                        dest=edges)
        self.assert_((coords == [[0]]*12).all())
        coords = self.geom.getEntCoords([[0,0,0]]*12, Stg.interleaved,
                                        dest=(edges, iGeom.Basis.u))
        self.assert_((coords == [[0]]*12).all())

    def testEntCoordsUtoXYZ(self):
        ent = self.geom.createBrick(2, 2, 2)
        edges = self.geom.getEntities(iBase.Type.edge)
        result = [ [ 1,  0,  1],
                   [ 0,  1,  1],
                   [-1,  0,  1],
                   [ 0, -1,  1],
                   [ 1,  0, -1],
                   [ 0, -1, -1],
                   [-1,  0, -1],
                   [ 0,  1, -1],
                   [-1, -1,  0],
                   [ 1, -1,  0],
                   [-1,  1,  0],
                   [ 1,  1,  0] ]

        ##### 1 vertex, 1 entity
        coords = self.geom.getEntCoords([0], src=edges[0])
        self.assert_((coords == result[0]).all())
        coords = self.geom.getEntCoords([0], src=(edges[0], iGeom.Basis.u))
        self.assert_((coords == result[0]).all())
        coords = self.geom.getEntCoords([0], Stg.interleaved, src=edges[0:1])
        self.assert_((coords == result[0]).all())
        coords = self.geom.getEntCoords([0], Stg.interleaved,
                                        src=(edges[0:1], iGeom.Basis.u))
        self.assert_((coords == result[0]).all())

        ##### 1 vertex, n entities
        coords = self.geom.getEntCoords([0], Stg.interleaved, src=edges)
        self.assert_((coords == result).all())
        coords = self.geom.getEntCoords([0], Stg.interleaved,
                                        src=(edges, iGeom.Basis.u))
        self.assert_((coords == result).all())

        ##### n vertices, 1 entity
        coords = self.geom.getEntCoords([[0]]*12, Stg.interleaved,
                                        src=edges[0])
        self.assert_((coords == result[0:1]*12).all())
        coords = self.geom.getEntCoords([[0]]*12, Stg.interleaved,
                                        src=(edges[0], iGeom.Basis.u))
        self.assert_((coords == result[0:1]*12).all())

        ##### n vertices, n entities
        coords = self.geom.getEntCoords([[0]]*12, Stg.interleaved, src=edges)
        self.assert_((coords == result).all())
        coords = self.geom.getEntCoords([[0]]*12, Stg.interleaved,
                                        src=(edges, iGeom.Basis.u))
        self.assert_((coords == result).all())

    def testEntCoordsUtoUV(self):
        ent = self.geom.createBrick(2, 2, 2)
        edges = self.geom.getEntities(iBase.Type.edge)
        faces = self.geom.getEntities(iBase.Type.face)

        ##### 1 vertex, 1 edge, 1 face
        coords = self.geom.getEntCoords([0], src=edges[0], dest=faces[0])
        self.assert_((coords == [1,0]).all())
        coords = self.geom.getEntCoords([0], src =(edges[0], iGeom.Basis.u),
                                             dest=(faces[0], iGeom.Basis.uv))
        self.assert_((coords == [1,0]).all())
        coords = self.geom.getEntCoords([0], Stg.interleaved,
                                        src=edges[0:1], dest=faces[0:1])
        self.assert_((coords == [1,0]).all())
        coords = self.geom.getEntCoords([0], Stg.interleaved,
                                        src =(edges[0:1], iGeom.Basis.u),
                                        dest=(faces[0:1], iGeom.Basis.uv))
        self.assert_((coords == [1,0]).all())

        ##### 1 vertex, 1 edge, n faces
        result = [[1,0], [1,0], [1,1], [-1,0], [-1,1], [1,0]]
        coords = self.geom.getEntCoords([0], Stg.interleaved,
                                        src=edges[0], dest=faces)
        self.assert_((coords == result).all())
        coords = self.geom.getEntCoords([0], Stg.interleaved,
                                        src =(edges[0], iGeom.Basis.u),
                                        dest=(faces,    iGeom.Basis.uv))
        self.assert_((coords == result).all())

        ##### 1 vertex, n edges, 1 face
        result = [[1,0], [0,1], [-1,0], [0,-1], [1,0], [0,-1], [-1,0], [0,1],
                  [-1,-1], [1,-1], [-1,1], [1,1]]
        coords = self.geom.getEntCoords([0], Stg.interleaved,
                                        src=edges, dest=faces[0])
        self.assert_((coords == result).all())
        coords = self.geom.getEntCoords([0], Stg.interleaved,
                                        src =(edges,    iGeom.Basis.u),
                                        dest=(faces[0], iGeom.Basis.uv))
        self.assert_((coords == result).all())

        ##### 1 vertex, n edges, n faces
        result = [[1,0], [0,1], [1,-1], [-1,-1], [1,1], [-1,-1]]
        coords = self.geom.getEntCoords([0], Stg.interleaved,
                                        src=edges[0:6], dest=faces)
        self.assert_((coords == result).all())
        coords = self.geom.getEntCoords([0], Stg.interleaved,
                                        src =(edges[0:6], iGeom.Basis.u),
                                        dest=(faces,      iGeom.Basis.uv))
        self.assert_((coords == result).all())

        ##### n vertices, 1 edge, 1 face
        coords = self.geom.getEntCoords([[0]]*6, Stg.interleaved,
                                        src=edges[0], dest=faces[0])
        self.assert_((coords == [[1,0]]*6).all())
        coords = self.geom.getEntCoords([[0]]*6, Stg.interleaved,
                                        src =(edges[0], iGeom.Basis.u),
                                        dest=(faces[0], iGeom.Basis.uv))
        self.assert_((coords == [[1,0]]*6).all())

        ##### n vertices, 1 edge, n faces
        result = [[1,0], [1,0], [1,1], [-1,0], [-1,1], [1,0]]
        coords = self.geom.getEntCoords([[0]]*6, Stg.interleaved,
                                        src=edges[0], dest=faces)
        self.assert_((coords == result).all())
        coords = self.geom.getEntCoords([[0]]*6, Stg.interleaved,
                                        src =(edges[0], iGeom.Basis.u),
                                        dest=(faces, iGeom.Basis.uv))
        self.assert_((coords == result).all())

        ##### n vertices, n edges, 1 face
        result = [[1,0], [0,1], [-1,0], [0,-1], [1,0], [0,-1], [-1,0], [0,1],
                  [-1,-1], [1,-1], [-1,1], [1,1]]
        coords = self.geom.getEntCoords([[0]]*12, Stg.interleaved,
                                        src=edges, dest=faces[0])
        self.assert_((coords == result).all())
        coords = self.geom.getEntCoords([[0]]*12, Stg.interleaved,
                                        src =(edges,    iGeom.Basis.u),
                                        dest=(faces[0], iGeom.Basis.uv))
        self.assert_((coords == result).all())

        ##### n vertices, n edges, n faces
        result = [[1,0], [0,1], [1,-1], [-1,-1], [1,1], [-1,-1]]
        coords = self.geom.getEntCoords([[0]]*6, Stg.interleaved,
                                        src=edges[0:6], dest=faces)
        self.assert_((coords == result).all())
        coords = self.geom.getEntCoords([[0]]*6, Stg.interleaved,
                                        src =(edges[0:6], iGeom.Basis.u),
                                        dest=(faces,      iGeom.Basis.uv))
        self.assert_((coords == result).all())

    def testRange(self):
        ent = self.geom.createBrick(2, 2, 2)
        faces = self.geom.getEntities(iBase.Type.face)
        edges = self.geom.getEntities(iBase.Type.edge)

        range = self.geom.getEntRange(faces[0], basis=iGeom.Basis.uv)
        self.assert_((range == [[-1,-1], [1,1]]).all())
        range = self.geom.getEntRange(faces[0])
        self.assert_((range == [[-1,-1], [1,1]]).all())

        range = self.geom.getEntRange(faces, Stg.interleaved, iGeom.Basis.uv)
        self.assert_((range == [[[-1,-1]]*6, [[1,1]]*6]).all())
        range = self.geom.getEntRange(faces, Stg.interleaved)
        self.assert_((range == [[[-1,-1]]*6, [[1,1]]*6]).all())

        range = self.geom.getEntRange(edges[0], basis=iGeom.Basis.u)
        self.assert_((range == [[-1], [1]]).all())
        range = self.geom.getEntRange(edges[0])
        self.assert_((range == [[-1], [1]]).all())

        range = self.geom.getEntRange(edges, basis=iGeom.Basis.u)
        self.assert_((range == [[[-1]]*12, [[1]]*12]).all())
        range = self.geom.getEntRange(edges)
        self.assert_((range == [[[-1]]*12, [[1]]*12]).all())


if __name__ == '__main__':
    unittest.main()
