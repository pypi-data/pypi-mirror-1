from itaps import iBase, iMesh
import sys

if len(sys.argv) != 2:
    print "usage: python tags.py filename"
    exit(1)

mesh = iMesh.Mesh()
mesh.load(sys.argv[1])
tags = set(mesh.getAllTags(mesh.rootSet))

for i in mesh.getEntities(iBase.Type.all, iMesh.Topology.all):
    tags |= set(mesh.getAllTags(i))
for i in mesh.getEntSets(0):
    tags |= set(mesh.getAllTags(i))

for i in tags:
    print i.name
